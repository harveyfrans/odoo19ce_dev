from odoo import models, fields, api
from datetime import timedelta

class RcPayrollRun(models.Model):
    _name = 'rc.payroll.run'
    _description = 'Payroll Simulation Run'

    name = fields.Char(string='Name', required=True, default='New Payroll Run')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft')
    line_ids = fields.One2many('rc.payroll.adjustment', 'run_id', string='Adjustment Lines')
    
    def action_compute(self):
        self.ensure_one()
        # Clear existing lines
        self.line_ids.unlink()
        
        # Get all employees
        employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id)])
        
        # Get active rules
        rules = self.env['rc.payroll.rule'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True)
        ])
        
        adjustment_vals = []
        
        for employee in employees:
            # Count attendance days
            # Simplest: count distinct date(check_in)
            # Need to convert date_to to datetime end of day to include full day for search if fields were datetime, 
            # but attendance check_in is datetime.
            
            start_dt = fields.Datetime.to_datetime(self.date_from)
            end_dt = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1, seconds=-1)
            
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt)
            ])
            
            # Distinct days
            worked_days = len(set(att.check_in.date() for att in attendances if att.check_in))
            
            # Apply rules
            applied_rule = None
            amount = 0.0
            note = ''
            
            # Find first matching rule? Or specific logic?
            # Goal: If attendance days >= min_attendance_days -> apply bonus
            # If attendance days < min_attendance_days -> apply penalty?
            # User requirement: "If attendance days >= min_attendance_days -> apply bonus. If attendance days < min_attendance_days -> apply penalty (depending on type)"
            # This implies rules define conditions.
            
            # Let's iterate rules and see if any match.
            # But conflicting rules? "Apply the first matching rule" as per requirement.
            
            for rule in rules:
                if rule.rule_type == 'bonus':
                    if worked_days >= rule.min_attendance_days:
                        applied_rule = rule
                        amount = rule.amount
                        note = f"Bonus applied: Worked {worked_days} days (>= {rule.min_attendance_days})"
                        break
                elif rule.rule_type == 'penalty':
                    if worked_days < rule.min_attendance_days:
                        applied_rule = rule
                        amount = -rule.amount # Penalty is negative adjustment
                        note = f"Penalty applied: Worked {worked_days} days (< {rule.min_attendance_days})"
                        break
            
            if applied_rule:
                adjustment_vals.append({
                    'run_id': self.id,
                    'employee_id': employee.id,
                    'attendance_days': worked_days,
                    'rule_id': applied_rule.id,
                    'amount': amount,
                    'note': note,
                })
        
        self.env['rc.payroll.adjustment'].create(adjustment_vals)
        self.state = 'computed'

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

    def action_reset_draft(self):
        self.ensure_one()
        self.state = 'draft'
