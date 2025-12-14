from odoo import models, fields

class RcPayrollAdjustment(models.Model):
    _name = 'rc.payroll.adjustment'
    _description = 'Payroll Adjustment Line'

    run_id = fields.Many2one('rc.payroll.run', string='Payroll Run', ondelete='cascade', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    attendance_days = fields.Integer(string='Attendance Days', readonly=True)
    rule_id = fields.Many2one('rc.payroll.rule', string='Applied Rule')
    amount = fields.Float(string='Adjustment Amount', readonly=True)
    note = fields.Text(string='Note')
