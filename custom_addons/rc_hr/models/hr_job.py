from odoo import models, fields

class HrJob(models.Model):
    _inherit = 'hr.job'

    foreign_language_ids = fields.Many2many(
        'rc.lang', 
        string='Kualifikasi Bahasa Asing'
    )
