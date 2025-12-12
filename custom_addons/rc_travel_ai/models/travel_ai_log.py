# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class TravelAiLog(models.Model):
    _name = "travel.ai.log"
    _description = "Travel AI Recommendation Log"
    _order = "create_date desc"

    name = fields.Char(string="Title", default=lambda self: _("Travel AI Session"))
    request_text = fields.Text(string="Customer Question", required=True)

    destination = fields.Char(string="Parsed Destination")
    days = fields.Integer(string="Parsed Days")
    travel_type = fields.Selection([
        ("flight", "Flight"),
        ("hotel", "Hotel"),
        ("package", "Package"),
    ], string="Parsed Type")
    budget_min = fields.Float(string="Budget Min")
    budget_max = fields.Float(string="Budget Max")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    product_ids = fields.Many2many("product.template", string="Recommended Products")

    sale_order_ids = fields.One2many(
        "sale.order", "ai_log_id", string="Sales Orders"
    )

    state = fields.Selection(
        [("draft", "Draft"), ("processed", "Processed")],
        default="draft",
    )

    @api.model
    def _simple_parse_input(self, text):
        text_lower = (text or "").lower()

        # 1. Destination
        destination = None
        # Simple whitelist approach
        for city in ["bali", "bandung", "singapore", "jakarta", "lombok", "yogya"]:
            if city in text_lower:
                destination = city.capitalize()
                break

        # 2. Travel Type
        travel_type = False
        if "flight" in text_lower or "terbang" in text_lower or "pesawat" in text_lower:
            travel_type = "flight"
        elif "hotel" in text_lower or "penginapan" in text_lower:
            travel_type = "hotel"
        elif "package" in text_lower or "paket" in text_lower or "tour" in text_lower:
            travel_type = "package"

        # 3. Numeric Parsing (Days vs Budget)
        days = 0
        budget_max = 0.0

        # Replace common separators and handle multipliers
        # We'll normalize string to help parsing: "5 juta" -> "5000000", "3k" -> "3000"
        tokens = text_lower.replace(",", "").split()
        
        # Helper to parse a token as number
        def parse_num(t):
            try:
                # remove non-digits that might be stuck (like "5hari")
                clean = "".join(filter(lambda x: x.isdigit() or x == '.', t))
                return float(clean)
            except ValueError:
                return 0.0

        for i, token in enumerate(tokens):
            if not any(c.isdigit() for c in token):
                continue
            
            val = parse_num(token)
            if val <= 0:
                continue

            # Check neighbors for context
            prev_word = tokens[i-1] if i > 0 else ""
            next_word = tokens[i+1] if i < len(tokens) - 1 else ""

            # Explicit "days" context
            if "hari" in token or "day" in token or "hari" in next_word or "day" in next_word:
                days = int(val)
                continue
            
            # Explicit "budget" context or multipliers
            is_budget = False
            multiplier = 1.0
            
            if "juta" in token or "juta" in next_word or "mio" in next_word:
                multiplier = 1_000_000
                is_budget = True
            elif "k" in token or "rb" in next_word or "ibu" in next_word: # ribu/thousand
                # "3k" is often 3000. But be careful not to catch "3km". Assuming currency here.
                multiplier = 1_000
                is_budget = True
            elif "budget" in prev_word or "harga" in prev_word or "rp" in prev_word or "usd" in next_word:
                is_budget = True

            if is_budget:
                budget_max = val * multiplier
                continue
            
            # Heuristics if no context found
            if val < 50 and days == 0:
                days = int(val)
            elif val >= 1000 and budget_max == 0:
                budget_max = val

        budget_min = 0.0  # Placeholder, not currently extracted logic for min

        return destination, days, budget_min, budget_max, travel_type

    def action_process(self):
        """
        Parse input & compute recommended products.

        IMPORTANT:
        - Filter products to the log's company (or shared products company_id=False)
        - Do NOT sudo() the product search. Let rules match what the website user can actually buy.
        """
        for rec in self:
            dest, days, bmin, bmax, ttype = self._simple_parse_input(rec.request_text)

            rec.write({
                "destination": dest,
                "days": days,
                "budget_min": bmin,
                "budget_max": bmax,
                "travel_type": ttype,
            })

            company = rec.company_id or self.env.company
            ctx = dict(self.env.context)
            ctx.update({
                "company_id": company.id,
                "allowed_company_ids": [company.id],
            })
            env_c = self.env(context=ctx)

            domain = [
                ("sale_ok", "=", True),
                ("company_id", "in", [False, company.id]),  # shared or this company only
            ]

            if dest:
                domain.append(("travel_destination", "ilike", dest))

            if ttype:
                domain.append(("travel_type", "=", ttype))

            if days:
                # Tighter filtering: +/- 1 day instead of 2
                domain.append(("travel_days", "<=", days + 1))
                domain.append(("travel_days", ">=", max(1, days - 1)))

            if bmax:
                domain.append(("list_price", "<=", bmax))

            products = env_c["product.template"].search(domain, limit=10)

            rec.write({
                "product_ids": [(6, 0, products.ids)],
                "state": "processed",
            })


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ai_log_id = fields.Many2one(
        "travel.ai.log",
        string="AI Recommendation Log",
        help="Filled when the order is created from Travel AI recommendations.",
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        ai_log_id = self.env.context.get("rc_ai_log_id")
        if not ai_log_id:
            return orders

        # Safety: only set ai_log_id if the log exists
        log = self.env["travel.ai.log"].sudo().browse(ai_log_id)
        if log.exists():
            orders.write({"ai_log_id": log.id})

        return orders
