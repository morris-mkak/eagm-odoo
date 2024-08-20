# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def _check_exist_product_in_line(self):
        for sale in self:
            exist_product_list = []
            for line in sale.order_line:
                if line.product_id.id:
                    if line.product_id.id in exist_product_list:
                        raise ValidationError(_('Duplicate products in order line not allowed !'))
                    exist_product_list.append(line.product_id.id)
