# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def set_access_for_sale_order_line(self):
        if self.product_id:
            if self.env.user.has_group \
                        ('eagm_custom_addons.group_restrict_sale_order_line'):
                self.restrict_sale_order_line = True
            else:
                self.restrict_sale_order_line = False
    restrict_sale_order_line = fields.Boolean(
        compute=set_access_for_sale_order_line,
        string='Is user able to access sale order line?')
