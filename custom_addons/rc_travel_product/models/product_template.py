from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    travel_destination = fields.Char(string="Travel Destination")
    travel_days = fields.Integer(string="Travel Days")
    travel_type = fields.Selection([
        ("flight", "Flight"),
        ("hotel", "Hotel"),
        ("package", "Package"),
    ], string="Travel Type")
