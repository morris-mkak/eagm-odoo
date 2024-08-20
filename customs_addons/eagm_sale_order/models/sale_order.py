# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    same_client_order_ref = fields.Boolean('')



    def action_confirm(self):
        partner_id = self.partner_id.id
        client_order_ref = self.client_order_ref
        order = self.env['sale.order'].search([('partner_id', '=', partner_id),
                                               ('client_order_ref', '=',
                                                client_order_ref)])
        if order:
            self.same_client_order_ref = True
        res = super(SaleOrderInherit, self).action_confirm()
        return res

    @api.onchange('partner_id')
    def _get_partners_product(self):
        if self.partner_id:
            if self.order_line:
                self.order_line = [(5, 0, 0)]


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    product_code_id = fields.Many2one('sh.product.customer.info')
    product_id = fields.Many2one('product.product')

    @api.onchange('order_partner_id')
    def _get_partners_product_code(self):
        order_partner_id = self.order_partner_id.id
        if self.order_partner_id:
            return {'domain': {
                'product_code_id': [('name', '=', order_partner_id)]}}

    @api.onchange('product_code_id')
    def _get_partner_id(self):
        product = self.product_code_id.product_tmpl_id.name
        all_products = self.env['product.product'].search(
            [('name', '=', product)], limit=1)
        self.product_id = all_products.id