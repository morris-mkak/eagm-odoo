# -*- coding: utf-8 -*-
from odoo import models, fields


class KECashAllowancesType(models.Model):
    """ Types of Cash allowances model """
    _name = "ke.cash.allowances.type"
    _description = "Cash Allowances Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Cash Allowance', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule', 'Salary Rule', required=True,
        domain=[('sequence', '>=', 11),
                ('sequence', '<=', 24),
                ('active', '=', True)],
        help="""This is the Salary rule that will be used to compute the amount of\
                allowance in the payslip for each applicable employee""")