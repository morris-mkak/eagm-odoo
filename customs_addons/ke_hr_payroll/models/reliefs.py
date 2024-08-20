# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as Eval


class KETaxRelief(models.Model):
    """ Kenya's tax reliefs model"""
    _name = "ke.reliefs"
    _description = "Tax Relief"
    _inherit = ["mail.thread"]
    _order = "employee_id, name asc"

    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.depends('write_date')
    def compute_name(self):
        self.name = str(self.relief_id.name) + \
                    ' (' + str(self.employee_id.name) + ')'

    def _default_formula(self):
        return """
# Available variables for use in formula:
# -----------------------------------------
# employee: selected employee record.
# relief: the current relief  record.
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    @api.depends('computation', 'fixed')
    def compute_relief(self):
        if self.computation == 'fixed':
            self.amount = self.fixed
        elif self.computation == 'formula':
            baselocaldict = {
                'result': None,
                'employee': self.employee_id,
                'relief': self}
            localdict = dict(baselocaldict)
            try:
                Eval(self.formula, localdict, mode='exec', nocopy=True)
            except BaseException:
                raise ValidationError(
                    _('Wrong formula defined for this \
                      Tax Relief: %s\n [%s].') % (self.name, self.formula))
            self.amount = localdict['result']
        else:
            self.amount = 0.00

    name = fields.Char('Name of Relief', compute='compute_name', store=True)
    relief_id = fields.Many2one(
        'ke.relief.type',
        'Type of Relief',
        required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        related='relief_id.rule_id',
        string='Salary Rule')
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name')
    fixed = fields.Float('Fixed Value', digits=dp.get_precision('Account'))
    amount = fields.Float(
        'Computed value',
        compute='compute_relief',
        digits=dp.get_precision('Account'),
        store=True,
        help="This is computed value of the relief if you are using a formula\
        else it is the fixed value of the relief")
    computation = fields.Selection(
        [
            ('fixed',
             'Use a Fixed Value'),
            ('formula',
             'Use a Formula')],
        'Computation Method',
        required=True,
        help="Choose a method to use to arrive at a value for the relief")
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="Define a formula to use to arrive at the tax relief if its \
        based on certain variables. Available variables are stated in the\
        text area of the formula")
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
