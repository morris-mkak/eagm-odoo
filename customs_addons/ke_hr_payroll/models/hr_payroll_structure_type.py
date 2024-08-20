# -*- coding: utf-8 -*-
from odoo import models, fields


class HrPayrollStructureType(models.Model):
    """ inherited types of contracts to add more """
    _name = "hr.payroll.structure.type"
    _inherit = "hr.payroll.structure.type"

    wage_type = fields.Selection(
        selection_add=[('daily',
             'Daily Wage')],
        required=True,
	ondelete={'daily':'cascade'},
        help="""You specify which remuneration model that is used in this contract.\n
                                [Monthly] - Employee is paid a predetermined monthly Salary\n
                                [Hourly] - Employee is paid based on number of hours worked\n
                                [Daily] - Employee is paid based on number of days worked""")

    tax_applicable = fields.Selection(
        [
            ('paye',
             'P.A.Y.E - Pay As You Earn'),
            ('wht',
             'Withholding Tax')],
        'Applicable Tax',
        required=True,
	ondelete={'paye':'cascade'},
        default='paye',
        help="""Select the applicable Taxation rate based on the type of contract given \n
        to the employee [PAYE] - Applies to all employments but it does not include \
                earnings from 'casual\n
        employment' which means any engagement with any one employer which is made for a period\n
        of less than one month, the emoluments of which are calculated by reference to the\n
        period of the engagement or shorter intervals\n
        [Withholding Tax] - Applies to both resident and non resident individuals hired on\n
        consultancy agreements or terms and is deducted from consultancy fees or contractual \n
        fees and paid to KRA on monthly basis.""")
