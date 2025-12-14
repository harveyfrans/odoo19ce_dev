from odoo import models, fields, api
import hashlib

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_lat = fields.Float(string='Check-in Latitude', readonly=True)
    check_in_lng = fields.Float(string='Check-in Longitude', readonly=True)
    check_out_lat = fields.Float(string='Check-out Latitude', readonly=True)
    check_out_lng = fields.Float(string='Check-out Longitude', readonly=True)
    geo_source = fields.Selection([
        ('dummy', 'Dummy'),
        ('manual', 'Manual'),
        ('sim_api', 'Sim API')
    ], string='Geolocation Source', default='dummy')
    geo_note = fields.Char(string='Geolocation Note')

    def _get_dummy_coordinates(self, employee_id):
        """Generate dummy coordinates based on employee ID hash to be stable per employee."""
        if not employee_id:
            return 0.0, 0.0

        emp_hash = int(hashlib.sha256(str(employee_id).encode('utf-8')).hexdigest(), 16)

        # Base coordinates (Jakarta roughly)
        base_lat = -6.2
        base_lng = 106.8

        # Generate offset (-0.05 to +0.05)
        lat_offset = (emp_hash % 1000) / 10000.0 - 0.05
        lng_offset = ((emp_hash >> 10) % 1000) / 10000.0 - 0.05

        return base_lat + lat_offset, base_lng + lng_offset

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('geo_source', 'dummy') != 'dummy':
                continue

            employee_id = vals.get('employee_id')
            if not employee_id:
                continue

            lat, lng = self._get_dummy_coordinates(employee_id)

            # check-in coords (existing behavior)
            if vals.get('check_in') and not vals.get('check_in_lat'):
                vals['check_in_lat'] = lat
                vals['check_in_lng'] = lng

            # NEW: if check_out is already provided at create time (backfill), fill check-out coords too
            if vals.get('check_out') and not vals.get('check_out_lat'):
                vals['check_out_lat'] = lat
                vals['check_out_lng'] = lng

        return super().create(vals_list)

    def write(self, vals):
        # Guard to prevent recursion when we write geo fields ourselves
        if self.env.context.get('skip_rc_geo'):
            return super().write(vals)

        res = super().write(vals)

        # After check_out is set, backfill dummy check-out coordinates if missing
        if vals.get('check_out'):
            for record in self:
                if record.geo_source == 'dummy' and (not record.check_out_lat or not record.check_out_lng):
                    lat, lng = self._get_dummy_coordinates(record.employee_id.id)
                    record.with_context(skip_rc_geo=True).write({
                        'check_out_lat': lat,
                        'check_out_lng': lng,
                    })

        return res
