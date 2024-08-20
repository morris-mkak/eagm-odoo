from odoo import models, api, fields


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def check_attendance(self):

