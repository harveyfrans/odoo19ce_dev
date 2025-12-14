from odoo import models, fields

class RcLang(models.Model):
    _name = 'rc.lang'
    _description = 'Foreign Language Qualification'

    name = fields.Char(string='Language Name', required=True)
    code = fields.Char(string='Code', size=2)
    active = fields.Boolean(default=True)
