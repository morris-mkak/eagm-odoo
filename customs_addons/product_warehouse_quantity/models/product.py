# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    warehouse_quantity = fields.Char(compute='_get_warehouse_quantity', string='Quantity per warehouse')

    def _get_warehouse_quantity(self):
        for record in self:
            warehouse_quantity_text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
            # multi_uoms = product_id.sales_multi_uom_id.ids
            # uom_set = self.env['wv.sales.multi.uom'].search([('name', '=', 'Set'), ('id', 'in', multi_uoms)]).unit.factor_inv
            # uom_carton = self.env['wv.sales.multi.uom'].search([('name', '=', 'Carton'), ('id', 'in', multi_uoms)]).unit.factor_inv
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id[0].id),('location_id.usage','=','internal')])
                t_warehouses = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in t_warehouses:
                            t_warehouses.update({quant.location_id:0})
                        t_warehouses[quant.location_id] += quant.quantity

                tt_warehouses = {}
                for location in t_warehouses:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in tt_warehouses:
                            tt_warehouses.update({warehouse_id.name:0})
                        tt_warehouses[warehouse_id.name] += t_warehouses[location]

                for item in tt_warehouses:
                    if tt_warehouses[item] != 0 and product_id.uom_po_id and product_id.uom_id:
                        ctns = str(round(tt_warehouses[item]//product_id.uom_po_id.factor_inv, 2))
                        sets = str(round((tt_warehouses[item]%product_id.uom_po_id.factor_inv)//product_id.uom_id.factor_inv, 2))
                        pcs = str(round((tt_warehouses[item]%product_id.uom_po_id.factor_inv)%product_id.uom_id.factor_inv, 2))
                        warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + ctns + " Cartons ," + sets + " Sets ," + pcs + " Pieces "
                record.warehouse_quantity = warehouse_quantity_text
