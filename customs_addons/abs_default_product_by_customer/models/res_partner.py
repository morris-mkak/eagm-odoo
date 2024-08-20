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

class ResPartner(models.Model):
    _inherit = "res.partner"

    product_ids = fields.One2many("product.line", "line_id", string = "Product List")

class Productline(models.Model):
    _name = "product.line"
    _description = 'Productline'

    line_id = fields.Many2one("res.partner")
    product_id = fields.Many2one("product.product", string = "Product")
    company_id = fields.Many2one('res.company', related='line_id.company_id', store=True, index=True)
    name = fields.Text('Description', translate=True)
    price_unit = fields.Float('Unit Price', digits='Product Price')
    discount = fields.Float('Discount (%)', digits='Discount', default=0.0)
    product_uom_qty = fields.Float('Quantity', digits='Product UoS', default=1)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ensure_one()
        if self.product_id:
            name = self.product_id.display_name
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            self.name = name
            self.price_unit = self.product_id.lst_price
            self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    def _onchange_product_uom(self):
        if self.product_id and self.product_uom_id:
            self.price_unit = self.product_id.uom_id._compute_price(self.product_id.lst_price, self.product_uom_id)

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom_id=False)
        return super(Productline, self).create(values)

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_("You cannot change the type of a sale quote line. Instead you should delete the current line and create a new line of the proper type."))
        return super(Productline, self).write(values)
