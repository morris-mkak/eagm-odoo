# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class QuotationOrderLine(models.Model):
    _inherit = 'sale.order.line'

    so_order_date = fields.Datetime(
        related="order_id.date_order", string="Sales order date")
    is_delivered = fields.Boolean(
        "Is Delivered", store=True, compute="_compute_delivered")

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_delivered(self):
        if self:
            for rec in self:
                if rec.product_id and rec.product_id.type != 'service' and rec.product_uom_qty > rec.qty_delivered:
                    rec.is_delivered = False
                else:
                    rec.is_delivered = True
