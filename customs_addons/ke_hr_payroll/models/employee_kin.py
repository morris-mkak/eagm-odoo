# -*- coding: utf-8 -*-
from odoo import models, fields


class KEKins(models.Model):
    _description = "Employee Kin"
    _name = "ke.employee.kin"
    _order = "name asc"
    _inherit = ["mail.thread"]

    name = fields.Char('Name', required=True)
    birthday = fields.Date('Date of Birth')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    phone = fields.Char('Phone Number')
    kin = fields.Boolean('Is Next of Kin?', default=False)
    relation = fields.Many2one(
        'ke.relation.type',
        'Type of Relation',
        required=True)
    address = fields.Text('Next of Kin Address')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
