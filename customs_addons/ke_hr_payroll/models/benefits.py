# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as Eval

LOGGER = logging.getLogger(__name__)


class KEBenefits(models.Model):
    _name = "ke.benefits"
    _description = "Benefits"
    _inherit = ["mail.thread"]
    _order = "contract_id, name asc"

    @api.depends('computation', 'fixed')
    def compute_benefit(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed
            elif rec.computation == 'formula':
                baselocaldict = {
                    'result': None,
                    'contract': rec.contract_id,
                    'benefit': rec}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Wrong formula defined for this benefit: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']
            else:
                rec.amount = 0.00

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.benefit_id.name) + \
                       ' (' + str(rec.contract_id.name) + ')'

    def _default_company_id(self):
        return self.env.user.company_id.id

    def _default_formula(self):
        return """
# Available variables for use in formula:
# --------------------------------------
# contract: the current contract record
# benefit: the current benefit record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    name = fields.Char(
        'Name',
        compute='compute_name',
        store=True,
        help="The name of this benefit as would appear in \
        the employee contract.")
    benefit_id = fields.Many2one(
        'ke.benefit.type',
        'Type of Benefit',
        required=True)
    rule_id = fields.Many2one(
        related='benefit_id.rule_id',
        store=True,
        string="Salary Rule",
        help="The Payslip rule used to compute this benefit")
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        help="The contract of the employee in which the benefit is given")
    amount = fields.Float(
        'Computed Value',
        compute='compute_benefit',
        digits=dp.get_precision('Account'),
        store=True,
        help="This is the computed value of the benefit if you are using \
        a formula else this value is equal to the fixed value if there \
        is not formula to apply ")
    computation = fields.Selection([('fixed',
                                     'Use the fixed value'),
                                    ('formula',
                                     'Use a Formula')],
                                   'Computation Method',
                                   required=True,
                                   help="Select a method to use to compute the\
                                   benefit")
    fixed = fields.Float(
        'Fixed Value',
        digits=dp.get_precision('Account'),
        help="This is a fixed value of the benefit as opposed to a changing \
        value based on formula")
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
    formula = fields.Text(
        'Formula',
        default=_default_formula,
        help="Define a formula to use to compute the value of the benefit \
        if the value depends on certain variables. The available variables are listed in the formula area.")