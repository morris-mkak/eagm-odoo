# -*- coding: utf-8 -*-
from odoo import models, fields


class KEPayrollSettings(models.Model):
    _inherit = ["res.company"]

    employer_nssf = fields.Char('Employer NSSF No.', size=9, required=True)
    employer_nhif = fields.Char('Employer NHIF Code', size=6, required=True)
    employer_kra = fields.Char('Employer KRA PIN.', size=11, required=True)
