# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    class StockMoveLine(models.Model):
        _inherit = 'stock.move.line'

        sale_price = fields.Float(compute='_compute_sale_price')

        @api.depends('qty_done', 'product_uom_id', 'product_id', 'move_id.sale_line_id',
                     'move_id.sale_line_id.price_reduce_taxinc', 'move_id.sale_line_id.product_uom')
        def _compute_sale_price(self):
            for move_line in self:
                if move_line.move_id.sale_line_id:
                    unit_price = move_line.move_id.sale_line_id.price_reduce_taxinc
                    qty = move_line.product_uom_id._compute_quantity(move_line.qty_done,
                                                                     move_line.move_id.sale_line_id.product_uom)
                else:
                    unit_price = move_line.product_id.list_price
                    qty = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
                move_line.sale_price = unit_price * qty
            super(StockMoveLine, self)._compute_sale_price()