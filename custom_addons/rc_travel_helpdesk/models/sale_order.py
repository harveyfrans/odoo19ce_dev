# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    helpdesk_ticket_ids = fields.One2many(
        "helpdesk.ticket", "sale_order_id", string="Helpdesk Tickets"
    )
    helpdesk_ticket_count = fields.Integer(
        compute="_compute_helpdesk_ticket_count", string="Ticket Count"
    )

    @api.depends("helpdesk_ticket_ids")
    def _compute_helpdesk_ticket_count(self):
        for rec in self:
            rec.helpdesk_ticket_count = len(rec.helpdesk_ticket_ids)

    def action_confirm(self):
        # Super first
        res = super(SaleOrder, self).action_confirm()
        
        for order in self:
            # Check for AI-related lines (mapped to Sale Order Lines)
            # Find lines that have an AI Log attached
            ai_lines = order.order_line.filtered(lambda l: l.ai_log_id)
            
            # Policy: One ticket per order, aggregating AI lines.
            # Avoid duplicate tickets if already created (e.g. re-confirm)
            if ai_lines and not order.helpdesk_ticket_ids:
                self._create_helpdesk_ticket(order, ai_lines)
        
        return res

    def _create_helpdesk_ticket(self, order, ai_lines):
        unique_logs = ai_lines.mapped("ai_log_id")
        
        # Build aggregated description
        desc_parts = []
        desc_parts.append(_("Automated Ticket from AI Recommendation"))
        desc_parts.append("=" * 40)
        
        for log in unique_logs:
            desc_parts.append(f"\n[AI Session: {log.create_date}]")
            desc_parts.append(f"Question: {log.request_text}")
            desc_parts.append(f"Intent: {log.travel_type or 'Any'} / {log.destination or 'Any'} / {log.days} days / Max {log.budget_max}")

        desc_parts.append("\n[Related Products Ordered]")
        for line in ai_lines:
            desc_parts.append(f"- {line.product_id.display_name} (Qty: {line.product_uom_qty})")
        
        description = "\n".join(desc_parts)

        self.env["helpdesk.ticket"].create({
            "sale_order_id": order.id,
            "ai_log_ids": [(6, 0, unique_logs.ids)],
            "partner_id": order.partner_id.id,
            "company_id": order.company_id.id,
            "description": description,
            "state": "draft",
        })

    def action_view_tickets(self):
        self.ensure_one()
        return {
            "name": _("Helpdesk Tickets"),
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {"default_sale_order_id": self.id},
        }
