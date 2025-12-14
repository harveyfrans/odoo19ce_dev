from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    planned_start = fields.Datetime(string='Planned Start')
    planned_end = fields.Datetime(string='Planned End')
    planned_hours = fields.Float(string='Planned Hours')
    planned_role = fields.Selection([
        ('consultant', 'Consultant'),
        ('pm', 'Project Manager'),
        ('dev', 'Developer'),
        ('tester', 'Tester')
    ], string='Planned Role')

    @api.constrains('planned_start', 'planned_end')
    def _check_planned_dates(self):
        for task in self:
            if task.planned_start and task.planned_end:
                if task.planned_end < task.planned_start:
                    raise ValidationError("Planned End Date cannot be before Planned Start Date.")
