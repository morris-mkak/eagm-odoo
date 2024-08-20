# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as Eval


class KEDeductions(models.Model):
    _name = "ke.deductions"
    _description = "After Tax Deduction"
    _inherit = ["mail.thread"]
    _order = "id, name asc"

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.deduction_id.name) + \
                       ' (' + str(rec.employee_id.name) + ')'

    @api.depends('computation', 'fixed')
    def compute_deduction(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed

            elif rec.computation == 'formula':
                baselocaldict = {
                    'result': None,
                    'employee': rec.employee_id,
                    'deduction': rec}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Error in the formula defined for this\
                          deduction: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']
            else:
                rec.amount = 0.00

    def _default_formula(self):
        return """
# Available variables for use in formula:
# --------------------------------------
# employee: selected employee record
# deduction: current deduction record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=_default_company_id,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Currency",
        required=True)
    name = fields.Char(
        'Name',
        compute='compute_name',
        store=True,
        help="Name of the after-tax deduction")
    deduction_id = fields.Many2one(
        'ke.deductions.type',
        'Type of Deduction',
        required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        related='deduction_id.rule_id',
        string='Payslip Rule',
        help="The Payslip or salary rule used to compute the value of \
        this deduction")
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name')
    fixed = fields.Float(
        'Fixed Amount',
        digits=dp.get_precision('Account'),
        help="Fixed value of this deduction as opposed to a changing value \
        based on formula")
    computation = fields.Selection([('fixed',
                                     'Fixed Amount'),
                                    ('formula',
                                     'Use a Formula'),
                                    ],
                                   'Computation Method',
                                   required=True,
                                   help="Select a method to use to compute \
                                   this deduction.")
    amount = fields.Float(
        'Amount to Deduct',
        compute='compute_deduction',
        digits=dp.get_precision('Account'),
        store=True,
        help="This is the computed amount to be deducted after tax, \
        this amount is equal to the fixed amount if the computation \
        method is set to 'Fixed Amount'")
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="The Formula to use in computing the dedcutions. \
        The variables containing useful data is stated within \
        the text inside the formula ")
