# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class KsRmaLine(models.Model):
    """ Model for RMA Order Line """

    _name = "ks.rma.line"
    _description = "RMA Orders Line"

    ks_rma_id = fields.Many2one(comodel_name="ks.rma", string="RMA", help="Relation with the RMA Orders.")
    ks_barcode = fields.Char(string="Barcode", help="Tells the barcode for the particular line.")
    ks_product_id = fields.Many2one(comodel_name="product.product", string="Product", readonly=True,
                                    help="Tells the Product for the particular line.")
    ks_delivered_qty = fields.Integer(string="Demand Quantity", readonly=True,
                                      help="Tells the Delivered/Received Quantity for the particular line.")
    ks_returned_qty = fields.Integer(string="Return Quantity",
                                     help="Tells Returned Quantity for the particular line.")
    ks_refund_qty = fields.Integer(string="Refund Quantity",
                                   help="Tells Refund Quantity for the particular line.")
    ks_replace_qty = fields.Integer(string="Replace Quantity",
                                    help="Tells Replace Quantity for the particular line.")
    ks_price_unit = fields.Float(string='Unit Price', help="Tells Price for the particular Product.")
    tax_ids = fields.Many2many('account.tax', string='Taxes',
                               domain=['|', ('active', '=', False), ('active', '=', True)])
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    ks_company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                    default=lambda self: self.env.user.company_id.id,
                                    readonly=True, help="Tells the Company Information.")
    ks_subtotal_amount = fields.Float(string='Subtotal Amount', compute='calculate_subtotal_amount')

    @api.depends('ks_refund_qty')
    def calculate_subtotal_amount(self):
        for rec in self:
            rec.ks_subtotal_amount = 0.0
            if rec.ks_rma_id.ks_is_refund:
                rec.ks_subtotal_amount += rec.ks_refund_qty * rec.ks_price_unit
