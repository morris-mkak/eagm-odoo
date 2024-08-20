# -*- coding: utf-8 -*-

from odoo import models, fields


class KeDepartment(models.Model):
    """ inherited to add overtime related features """
    _inherit = ["hr.department"]

    company_currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id')
    overtime = fields.Monetary(
        'Overtime Hourly rate',
        currency_field='company_currency_id', tracking=True, )