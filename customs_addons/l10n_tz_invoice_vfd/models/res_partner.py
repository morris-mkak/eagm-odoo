# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    l10n_tz_invoice_vfd_id_type = fields.Selection([
        ('1', 'TIN'),
        ('2', 'Driving License'),
        ('3', 'Voters Number'),
        ('4', 'Passport'),
        ('5', 'NID (National Identity)'),

        ('6', 'NIL (If there is no ID)'),
    ]
        , string='ID Type', default='6')
    l10n_tz_invoice_vfd_id_number = fields.Char(string='ID Number')
    l10n_tz_vat_no = fields.Char(string='VAT Number')
