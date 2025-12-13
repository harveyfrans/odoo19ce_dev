# rc_travel_helpdesk  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\__init__.py

```
from . import models


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\__manifest__.py

```
{
    "name": "RC Travel Helpdesk",
    "version": "19.0.1.0.0",
    "summary": "Sistem tiket helpdesk sederhana (Tes Kompetensi).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 4: Manajemen Tiket Helpdesk.
    """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": [
        "sale",
        "rc_travel_ai",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/helpdesk_ticket_views.xml",
        "views/sale_order_views.xml",
        "views/helpdesk_menu.xml",
    ],
    "installable": True,
}


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\data\ir_sequence_data.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="seq_helpdesk_ticket" model="ir.sequence">
            <field name="name">Helpdesk Ticket</field>
            <field name="code">helpdesk.ticket</field>
            <field name="prefix">TICKET/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
    </data>
</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\models\__init__.py

```
from . import helpdesk_ticket
from . import sale_order


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\models\helpdesk_ticket.py

```
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _order = "create_date desc"
    
    name = fields.Char(string="Ticket Reference", required=True, copy=False, readonly=True, default=lambda self: _("New"))
    
    sale_order_id = fields.Many2one(
        "sale.order", string="Order", readonly=True
    )
    
    # Aggregated logs from lines
    ai_log_ids = fields.Many2many(
        "travel.ai.log", string="AI Logs", readonly=True
    )
    
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True
    )
    
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    
    description = fields.Text(string="Description")
    
    state = fields.Selection([
        ("draft", "Draft"),
        ("open", "Open"),
        ("done", "Done"),
    ], string="Status", default="draft")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("helpdesk.ticket") or _("New")
        return super().create(vals_list)

    def action_open(self):
        self.write({"state": "open"})

    def action_done(self):
        self.write({"state": "done"})


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\models\sale_order.py

```
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


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\README.md

```
# RC Travel Helpdesk (Tes Kompetensi â€“ Bagian 4)

Manajemen tiket helpdesk sederhana untuk agen travel.

## Tujuan

Menyediakan sistem tracking issue sederhana yang terintegrasi dengan Sale Order dan AI Log, dengan logika agregasi cerdas untuk mixed carts.

## Fitur

- **Menu**:
  - Helpdesk -> Tickets
- **Model**: `helpdesk.ticket`.
- **Integrasi**:
  - Link otomatis ke **Sale Order** (asal transaksi).
  - Link otomatis ke **Multi AI Logs** (agregasi dari order lines).
- **Workflow Status**:
  - Draft -> Open -> Done.
- **Logika Agregasi Unik**:
  - Tiket dibuat otomatis saat **Sale Order Confirm**.
  - **Satu Tiket per Order**: Jika order berisi produk dari beberapa sesi AI berbeda (atau campuran), sistem hanya membuat satu tiket.
  - **Deskripsi Komprehensif**: Deskripsi tiket menggabungkan semua pertanyaan/konteks dari berbagai sesi AI yang terlibat dalam order tersebut.

## Cara Pakai

1. Lakukan transaksi penjualan via Website/Backend (yang melibatkan produk rekomendasi AI).
2. Confirm Order.
3. Cek menu **Helpdesk**.
4. Tiket baru akan muncul otomatis dengan:
   - Referensi Order.
   - Daftar AI Log terkait (Many2many).
   - Deskripsi lengkap (Gabungan konteks AI + Produk yang dibeli).


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\security\ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_helpdesk_ticket_user,helpdesk.ticket.user,model_helpdesk_ticket,base.group_user,1,1,1,1
access_helpdesk_ticket_manager,helpdesk.ticket.manager,model_helpdesk_ticket,base.group_system,1,1,1,1


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\views\helpdesk_menu.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Top Level Menu inside Sales app -->
        <menuitem id="menu_helpdesk_root"
                  name="Helpdesk"
                  parent="sale.sale_menu_root"
                  sequence="60"/>

        <!-- Action defined later, but referenced here. 
             Ideally should define action first or in same file. 
             I'll assume action_helpdesk_ticket is in ticket_views.xml 
             and rely on Odoo loading order or just put definition here if separate.
             Actually, better style: define logic in views file, menu here. -->
        
        <menuitem id="menu_helpdesk_ticket"
                  name="Tickets"
                  parent="menu_helpdesk_root"
                  action="action_helpdesk_ticket"
                  sequence="10"/>
    </data>
</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\views\helpdesk_ticket_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        
        <!-- Action -->
        <record id="action_helpdesk_ticket" model="ir.actions.act_window">
            <field name="name">Helpdesk Tickets</field>
            <field name="res_model">helpdesk.ticket</field>
            <field name="view_mode">list,form</field>
        </record>

        <!-- List View -->
        <record id="view_helpdesk_ticket_tree" model="ir.ui.view">
            <field name="name">helpdesk.ticket.list</field>
            <field name="model">helpdesk.ticket</field>
            <field name="arch" type="xml">
                <list string="Helpdesk Tickets">
                    <field name="name"/>
                    <field name="create_date"/>
                    <field name="partner_id"/>
                    <field name="sale_order_id"/>
                    <field name="company_id" groups="base.group_multi_company"/>
                    <field name="state" widget="badge" decoration-info="state == 'open'" decoration-success="state == 'done'" decoration-muted="state == 'draft'"/>
                </list>
            </field>
        </record>

        <!-- Form View -->
        <record id="view_helpdesk_ticket_form" model="ir.ui.view">
            <field name="name">helpdesk.ticket.form</field>
            <field name="model">helpdesk.ticket</field>
            <field name="arch" type="xml">
                <form string="Helpdesk Ticket">
                    <header>
                        <button name="action_open" string="Open Ticket" type="object" invisible="state != 'draft'" class="oe_highlight"/>
                        <button name="action_done" string="Mark Done" type="object" invisible="state != 'open'" class="oe_highlight"/>
                        <field name="state" widget="statusbar"/>
                    </header>
                    <sheet>
                        <div class="oe_title">
                            <h1>
                                <field name="name"/>
                            </h1>
                        </div>
                        <group>
                            <group>
                                <field name="partner_id"/>
                                <field name="sale_order_id"/>
                                <field name="ai_log_ids" widget="many2many_tags"/>
                            </group>
                            <group>
                                <field name="create_date"/>
                                <field name="company_id" groups="base.group_multi_company"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Description">
                                <field name="description"/>
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

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_helpdesk\views\sale_order_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="view_order_form_inherit_helpdesk" model="ir.ui.view">
            <field name="name">sale.order.form.inherit.helpdesk</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                <div name="button_box" position="inside">
                    <button name="action_view_tickets"
                            type="object"
                            class="oe_stat_button"
                            icon="fa-life-ring"
                            invisible="helpdesk_ticket_count == 0">
                        <field name="helpdesk_ticket_count" widget="statinfo" string="Tickets"/>
                    </button>
                </div>
            </field>
        </record>
    </data>
</odoo>


```
