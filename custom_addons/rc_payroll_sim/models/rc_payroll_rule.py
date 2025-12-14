from odoo import models, fields

class RcPayrollRule(models.Model):
    _name = 'rc.payroll.rule'
    _description = 'Payroll Simulation Rule'

    name = fields.Char(string='Rule Name', required=True)
    rule_type = fields.Selection([
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty')
    ], string='Rule Type', required=True, default='bonus')
    amount = fields.Float(string='Amount', required=True, help="Positive value")
    min_attendance_days = fields.Integer(string='Min Attendance Days', default=0)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
