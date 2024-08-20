# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval as Eval


class KECashAllowances(models.Model):
    _name = "ke.cash_allowances"
    _description = "Cash Allowances"
    _inherit = ["mail.thread"]
    _order = "contract_id asc"

    @api.depends('computation', 'fixed')
    def compute_cash_allowance(self):
        for rec in self:
            if rec.computation == 'fixed':
                rec.amount = rec.fixed
            elif rec.computation == 'formula':
                baselocaldict = {'result': None, 'contract': rec.contract_id}
                localdict = dict(baselocaldict)
                try:
                    Eval(rec.formula, localdict, mode='exec', nocopy=True)
                except BaseException:
                    raise ValidationError(
                        _('Wrong formula defined for Cash Allowances: %s\n [%s].') %
                        (rec.name, rec.formula))
                rec.amount = localdict['result']

            else:
                rec.amount = 0.00

    @api.depends('write_date')
    def compute_name(self):
        for rec in self:
            rec.name = str(rec.cash_allowance_id.name) + \
                       ' (' + str(rec.contract_id.name) + ')'

    def _default_company_id(self):
        return self.env.user.company_id.id

    def _default_formula(self):
        return """
# Available variables for use in formula:
# ----------------------------------------
# contract: the current contract record
# Note: returned value have to be set in the variable 'result'
result = 0.00
"""

    name = fields.Char('Name', compute='compute_name', store=True)
    cash_allowance_id = fields.Many2one(
        'ke.cash.allowances.type',
        'Type of Cash Allowance',
        required=True)
    rule_id = fields.Many2one(
        related='cash_allowance_id.rule_id',
        store=True,
        string="Salary Rule")
    contract_id = fields.Many2one('hr.contract', 'Contract')
    amount = fields.Float(
        'Taxable Value',
        compute='compute_cash_allowance',
        digits=dp.get_precision('Account'),
        store=True)
    computation = fields.Selection([('fixed',
                                     'Use Fixed Value'),
                                    ('formula',
                                     'Use Predefined Formula')],
                                   'Computation Method',
                                   required=True)
    fixed = fields.Float('Fixed Value', digits=dp.get_precision('Account'))
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
    formula = fields.Text('Formula', default=_default_formula)