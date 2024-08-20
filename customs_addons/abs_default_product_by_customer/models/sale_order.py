# -*- coding: utf-8 -*-
#################################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api,fields,models,_

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.product_ids:
            order_lines = [(5, 0, 0)]
            for line in self.partner_id.product_ids:
                data = self._compute_line_data_for_template_change(line)
                if line.product_id:
                    price = line.product_id.lst_price
                    discount = 0
                    if self.pricelist_id:
                        pricelist_price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id, 1, False)
                        if self.pricelist_id.discount_policy == 'without_discount' and price:
                            discount = max(0, (price - pricelist_price) * 100 / price)
                        else:
                            price = pricelist_price
                    data.update({
                        'price_unit': price,
                        'discount': discount,
                        'product_uom_qty': line.product_uom_qty,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom_id.id,
                        'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                    })
                order_lines.append((0, 0, data))
            self.order_line = order_lines
            self.order_line._compute_tax_id()
        return super(SaleOrder, self).onchange_partner_id()
