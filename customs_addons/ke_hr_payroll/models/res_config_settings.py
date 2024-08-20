# -*- coding: utf-8 -*-
from odoo import models, fields


class KEPayrollSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    employer_nssf = fields.Char(
        'Employer NSSF NO.',
        related='company_id.employer_nssf',
        required=True,
        size=9, readonly=False)
    employer_nhif = fields.Char(
        'Employer NHIF CODE.',
        related='company_id.employer_nhif',
        required=True,
        size=6, readonly=False)
    employer_kra = fields.Char(
        'Employer KRA PIN.',
        related='company_id.employer_kra',
        required=True,
        size=11, readonly=False)
