# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr
import logging


class ProductTemplate(models.Model):
    _inherit = "product.template"

    l10n_tz_invoice_vfd_tax_class = fields.Selection([
        ('A', 'A= Standard Rate (18%)'),
        ('B', 'B= Special Rate (0%)'),
        ('C', 'C= Zero rated (0%)'),
        ('D', 'D= Special Relief (0%)'),
        ('E', 'E= Exempt (0%)'),
    ]
        , string='ID Type', default='A')


class ProductProduct(models.Model):
    _inherit = "product.product"

    l10n_tz_invoice_vfd_tax_class = fields.Selection([
        ('A', 'A= Standard Rate (18%)'),
        ('B', 'B= Special Rate (0%)'),
        ('C', 'C= Zero rated (0%)'),
        ('D', 'D= Special Relief (0%)'),
        ('E', 'E= Exempt (0%)'),
    ]
        , string='ID Type', default='A')
