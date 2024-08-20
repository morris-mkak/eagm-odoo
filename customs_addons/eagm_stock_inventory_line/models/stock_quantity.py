from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    available_cartons = fields.Float(
        compute='_compute_available_cartons', 
        string='Available Cartons', store=True,
        readonly=True, states={'confirm': [('readonly', False)]},
        digits='Reserved Cartons', default=0)
    cartons = fields.Float(
        compute='_compute_cartons',
        string='Cartons', store=True,
        digits='Reserved Cartons', 
        readonly=False, default=0)
    
    @api.depends("quantity")
    def _compute_cartons(self):
        for record in self:
            if record.quantity and record.product_id and record.product_uom_id:
                record.cartons = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.quantity
            else:
                record.cartons = 0
    
    @api.depends("available_quantity")
    def _compute_available_cartons(self):
        for record in self:
            if record.available_quantity and record.product_id and record.product_uom_id:
                record.available_cartons = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.available_quantity
            else:
                record.available_cartons = 0
