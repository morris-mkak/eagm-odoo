# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    sale_warehouse_id = fields.Many2one('stock.warehouse',string="Sale Warehouse" ,store = True , related = 'product_tmpl_id.sale_warehouse_id' )
