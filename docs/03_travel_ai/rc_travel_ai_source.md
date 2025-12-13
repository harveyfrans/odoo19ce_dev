# rc_travel_ai  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\__init__.py

```
from . import models
from . import controllers

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\__manifest__.py

```
{
    "name": "RC Travel AI Simulation",
    "version": "19.0.2.0.0",
    "summary": "Simulasi AI untuk rekomendasi travel (Tes Kompetensi).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 3: Simulasi AI Assistant & Rekomendasi.
    """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
        "sale",
        "rc_travel_product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/travel_ai_templates.xml",
        "views/travel_ai_menu.xml",
    ],
    "installable": True,
}


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\controllers\__init__.py

```
from . import main

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\controllers\main.py

```
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request



class TravelAiController(http.Controller):

    def _get_website_company_env(self):
        """Return an env locked to the current website company."""
        company = request.website.company_id
        # Use core environment call because with_company/with_context are missing
        ctx = dict(request.env.context)
        ctx.update({
            "company_id": company.id,
            "allowed_company_ids": [company.id],
        })
        env = request.env(context=ctx)
        return env, company

    @http.route(
        "/travel/ai",
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,  # important
    )
    def travel_ai(self, **post):
        """
        PRG pattern:
        - POST creates log + processes -> redirect to /travel/ai?log_id=XX
        - GET renders either empty form or the log specified by log_id
        """
        env, company = self._get_website_company_env()

        # ---------- POST ----------
        if request.httprequest.method == "POST":
            question = (post.get("question") or "").strip()
            if not question:
                # Redirect with an error flag (simple, avoids stale POST resubmission)
                return request.redirect("/travel/ai?err=empty")

            # Create log in website company (sudo ok for logging, but company-bound)
            log = env["travel.ai.log"].sudo().create({
                "request_text": question,
                "company_id": company.id,
            })

            # Process recommendations (IMPORTANT: make the model code company-safe too)
            log.action_process()

            # Redirect to GET page showing that log
            return request.redirect("/travel/ai?log_id=%s" % log.id)

        # ---------- GET ----------
        err = (request.params.get("err") or "").strip()
        error_message = "Pertanyaan tidak boleh kosong." if err == "empty" else None

        log = None
        log_id = request.params.get("log_id")
        if log_id:
            try:
                log_id = int(log_id)
            except Exception:
                log_id = 0

            if log_id:
                # Only allow viewing logs belonging to this website company
                # (or adjust if you want shared logs)
                log = env["travel.ai.log"].sudo().browse(log_id)
                if not log.exists() or (log.company_id and log.company_id.id != company.id):
                    log = None

        values = {
            "log": log,
            "error_message": error_message,
        }
        return request.render("rc_travel_ai.travel_ai_page", values)

    @http.route(
        "/travel/ai/buy/<int:log_id>/<int:product_id>",
        type="http",
        auth="public",
        website=True,
        methods=["GET"],
    )
    def travel_ai_buy(self, log_id, product_id, **kw):
        """
        Store log_id in session, then redirect to product page.
        Enforce website company visibility (no cross-company buy).
        """
        env, company = self._get_website_company_env()

        # Validate log is same company
        log = env["travel.ai.log"].sudo().browse(log_id)
        if not log.exists() or (log.company_id and log.company_id.id != company.id):
            return request.redirect("/travel/ai")

        # Find product template in website company scope (no sudo, respect rules)
        product_tmpl = env["product.template"].browse(product_id)
        if not product_tmpl.exists():
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        # Must be saleable and company-compatible: company_id False or website company
        if product_tmpl.company_id and product_tmpl.company_id.id != company.id:
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        if not product_tmpl.sale_ok:
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        # Store log in session so website_sale can attach it to the order
        request.session["rc_ai_log_id"] = log_id

        # Redirect to first variant product page (website_sale uses product.product route)
        variant = product_tmpl.product_variant_id
        return request.redirect("/shop/product/%s" % variant.id)





```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\models\__init__.py

```
from . import travel_ai_log
from . import sale_order_line

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\models\sale_order_line.py

```
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ai_log_id = fields.Many2one(
        "travel.ai.log",
        string="AI Log",
        readonly=True,
        help="AI Session that recommended this product."
    )

    @api.model_create_multi
    def create(self, vals_list):
        # runtime flow: "That line receives ai_log_id (if present in session)"
        # We check request.session safely
        try:
            if request and request.session.get("rc_ai_log_id"):
                log_id = request.session.get("rc_ai_log_id")
                # Validate existence to be safe? 
                # Odoo will check constraint on write, but session might have stale ID.
                # Assuming ID is valid or ignored if FK fails (actually FK fail raises error).
                # Good practice: check existence if simple.
                # But for performance in create_multi, maybe just trust or catch?
                # Let's trust session for now, or use safe retrieval.
                
                # Check directly in env to avoid overhead?
                # Using sudo to check existence since user might not have read access to logs (public user?)
                # Actually user just created it.
                
                for vals in vals_list:
                    if "ai_log_id" not in vals:
                         vals["ai_log_id"] = log_id
        except Exception:
            # Fallback if request is not available or other issue (e.g. strict environment)
            pass
            
        return super().create(vals_list)


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\models\travel_ai_log.py

```
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

    # Linked lines for traceability (inverse of sale.order.line.ai_log_id)
    # This replaces the old sale_order_ids
    sale_line_ids = fields.One2many(
        "sale.order.line", "ai_log_id", string="Related Sale Lines"
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
        tokens = text_lower.replace(",", "").split()
        
        def parse_num(t):
            try:
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

            prev_word = tokens[i-1] if i > 0 else ""
            next_word = tokens[i+1] if i < len(tokens) - 1 else ""

            # Explicit "days" context
            if "hari" in token or "day" in token or "hari" in next_word or "day" in next_word:
                days = int(val)
                continue
            
            # Explicit "budget" context
            is_budget = False
            multiplier = 1.0
            
            if "juta" in token or "juta" in next_word or "mio" in next_word:
                multiplier = 1_000_000
                is_budget = True
            elif "k" in token or "rb" in next_word or "ibu" in next_word: 
                multiplier = 1_000
                is_budget = True
            elif "budget" in prev_word or "harga" in prev_word or "rp" in prev_word or "usd" in next_word:
                is_budget = True

            if is_budget:
                budget_max = val * multiplier
                continue
            
            # Heuristics
            if val < 50 and days == 0:
                days = int(val)
            elif val >= 1000 and budget_max == 0:
                budget_max = val

        budget_min = 0.0
        return destination, days, budget_min, budget_max, travel_type

    def action_process(self):
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
                ("company_id", "in", [False, company.id]),
            ]

            if dest:
                domain.append(("travel_destination", "ilike", dest))

            if ttype:
                domain.append(("travel_type", "=", ttype))

            if days:
                domain.append(("travel_days", "<=", days + 1))
                domain.append(("travel_days", ">=", max(1, days - 1)))

            if bmax:
                domain.append(("list_price", "<=", bmax))

            products = env_c["product.template"].search(domain, limit=10)

            rec.write({
                "product_ids": [(6, 0, products.ids)],
                "state": "processed",
            })


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\README.md

```
# RC Travel AI Simulation (Tes Kompetensi â€“ Bagian 3)

Simulasi AI Assistant sederhana untuk rekomendasi paket travel.

## Tujuan

Mendemonstrasikan logika parsing teks sederhana (Mock AI) untuk merekomendasikan produk travel berdasarkan input natural language dari customer, dengan arsitektur yang mendukung **mixed carts**.

## Fitur

- **Menu**: AI Assistant (Di Website / Backend).
- **Logika Mock AI (Regex/Keyword Parsing)**:
  - Deteksi **Destinasi**: Bali, Bandung, Singapore, dll.
  - Deteksi **Tipe**: Flight, Hotel, Package.
  - Deteksi **Budget/Durasi**: Mengenali angka hari atau mata uang (juta/rb).
- **Rekomendasi Produk**:
  - Mencocokkan input dengan data di `rc_travel_product`.
  - Menampilkan daftar produk yang relevan.
- **Integrasi E-commerce Granular**:
  - `ai_log_id` disimpan di level **Sale Order Line**, bukan Sale Order.
  - Mendukung keranjang belanja campuran (produk rekomendasi AI + produk manual).
  - Data AI diteruskan dari sesi website ke line saat "Add to Cart".

## Cara Pakai

1. Buka menu **Pemeriksa Cuaca -> AI Log** (atau frontend website `/travel/ai`).
2. Masukkan pertanyaan customer, misal:
   > "Saya mau liburan ke Bali selama 5 hari budget 10 juta"
3. Klik **Process**.
4. Log akan terisi otomatis dengan hasil parsing.
5. Klik **Beli Sekarang** pada salah satu produk rekomendasi.
6. Produk akan masuk ke keranjang, dan line tersebut akan ditandai dengan sumber AI Log tersebut.

## Detail Teknis

- Model: `travel.ai.log`.
- Relasi: `sale_line_ids` (One2many ke `sale.order.line`).
- Website Integration: `request.session` menyimpan `rc_ai_log_id` sementara yang kemudian disuntikkan ke `sale.order.line` saat pembuatan.


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\security\ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_travel_ai_log_all,travel.ai.log.all,model_travel_ai_log,base.group_user,1,1,1,1


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\views\travel_ai_menu.xml

```
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
  <data>

    <record id="action_travel_ai_log" model="ir.actions.act_window">
      <field name="name">Travel AI Logs</field>
      <field name="res_model">travel.ai.log</field>
      <field name="view_mode">list,form</field>
    </record>

    <menuitem id="menu_travel_ai_root"
              name="Travel AI"
              sequence="50"
              parent="sale.sale_menu_root"/>

    <menuitem id="menu_travel_ai_log"
              name="AI Logs"
              parent="menu_travel_ai_root"
              action="action_travel_ai_log"
              sequence="10"/>

    <record id="view_travel_ai_log_list" model="ir.ui.view">
      <field name="name">travel.ai.log.list</field>
      <field name="model">travel.ai.log</field>
      <field name="arch" type="xml">
        <list>
          <field name="create_date"/>
          <field name="request_text"/>
          <field name="destination"/>
          <field name="days"/>
          <field name="budget_max"/>
          <field name="company_id"/>
          <field name="state"/>
        </list>
      </field>
    </record>

    <record id="view_travel_ai_log_form" model="ir.ui.view">
      <field name="name">travel.ai.log.form</field>
      <field name="model">travel.ai.log</field>
      <field name="arch" type="xml">
        <form string="Travel AI Log">
          <sheet>
            <group>
              <field name="request_text"/>
              <field name="destination"/>
              <field name="days"/>
              <field name="budget_min"/>
              <field name="budget_max"/>
              <field name="company_id"/>
              <field name="state"/>
            </group>
            <notebook>
              <page string="Produk Rekomendasi">
                <field name="product_ids" widget="many2many_tags"/>
              </page>
              <page string="Related Sale Lines">
                <field name="sale_line_ids"/>
              </page>
            </notebook>
          </sheet>
        </form>
      </field>
    </record>

  </data>
</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_ai\views\travel_ai_templates.xml

```
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
  <data>
    <!-- <template id="travel_ai_page" name="Travel AI Assistant" page="True"> -->
    <template id="travel_ai_page" name="Travel AI Assistant"> <!-- solution 3 -->
      <t t-call="website.layout">
        <div class="container mt-4 mb-4">
          <h1>Asisten Travel (Simulasi AI)</h1>
          <p>
            Masukkan kebutuhan liburan Anda, misalnya:
            <em>"Saya ingin liburan ke Bali 5 hari dengan budget 5 juta."</em>
          </p>

          <t t-if="error_message">
            <div class="alert alert-danger" role="alert">
              <t t-esc="error_message"/>
            </div>
          </t>

          <form method="post" action="/travel/ai">
            <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/> <!-- solution 1 -->
            <div class="form-group mb-3">
              <label for="question">Pertanyaan / Kebutuhan</label>
              <textarea name="question" id="question" class="form-control" rows="3" required="required"><t t-esc="log.request_text if log else ''"/></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Dapatkan Rekomendasi</button>
          </form>

          <t t-if="log">
            <hr/>
            <h2>Hasil Rekomendasi</h2>

            <p>
              <strong>Destinasi:</strong>
              <t t-esc="log.destination or 'Tidak terdeteksi'"/>
              <span> | </span>

              <strong>Durasi (hari):</strong>
              <t t-esc="log.days or 'Tidak terdeteksi'"/>
              <span> | </span>

              <strong>Budget Maksimal:</strong>
              <t t-esc="log.budget_max or 0"/>
            </p>

            <t t-if="log.product_ids">
              <div class="row">
                <t t-foreach="log.product_ids" t-as="prod">
                  <div class="col-md-4 mb-3">
                    <div class="card h-100">
                      <div class="card-body">
                        <h5 class="card-title">
                          <t t-esc="prod.name"/>
                        </h5>

                        <p class="card-text">
                          <strong>Destinasi:</strong>
                          <t t-esc="prod.travel_destination or '-'"/><br/>
                          <strong>Durasi:</strong>
                          <t t-esc="prod.travel_days or 0"/> hari<br/>
                          <strong>Harga:</strong>
                          <t t-esc="prod.list_price"/>
                        </p>

                        <!-- <a t-att-href="'/travel/ai/buy/%s/%s' % (log.id, prod.id)"
                          class="btn btn-success"> -->
                        <a t-attf-href="/travel/ai/buy/#{log.id}/#{prod.id}" class="btn btn-success"> <!-- solution 2 -->
                          Beli Sekarang
                        </a>
                      </div>
                    </div>
                  </div>
                </t>
              </div>
            </t>

            <t t-if="not log.product_ids">
              <div class="alert alert-warning" role="alert">
                Tidak ada produk yang cocok dengan kriteria Anda.
              </div>
            </t>
          </t>

        </div>
      </t>
    </template>
  </data>
</odoo>


```
