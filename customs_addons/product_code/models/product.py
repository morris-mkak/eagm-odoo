# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    partner_id = fields.Many2one("res.partner", "Partner")
    product_code_id = fields.Char("Partner Code")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    partner_id = fields.Many2one("res.partner", "Partner")
    product_code_id = fields.Char("Partner Code")
