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
