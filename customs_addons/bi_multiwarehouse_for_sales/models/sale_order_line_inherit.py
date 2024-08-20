# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    warehouses_id = fields.Many2one('stock.warehouse',string="Warehouse")
    is_warehouse = fields.Boolean()

    @api.onchange('product_id')
    def set_required_warehouse(self):
        allow_warehouse = self.env['ir.config_parameter'].sudo().get_param('bi_multiwarehouse_for_sales.allow_warehouse')
        self.is_warehouse = allow_warehouse
        if self.product_id:
            self.warehouses_id = self.product_id.sale_warehouse_id.id





    def _prepare_procurement_values(self,group_id):
        res = super(SaleOrderLineInherit, self)._prepare_procurement_values(group_id=group_id)
        
        res_config= self.env['res.config.settings'].sudo().search([],order="id desc", limit=1)
        if res_config.allow_warehouse:
            res.update({
                'warehouse_id':self.warehouses_id,
                })
            
        return res