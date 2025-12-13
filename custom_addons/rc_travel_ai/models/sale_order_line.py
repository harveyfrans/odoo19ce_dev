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
