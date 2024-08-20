from odoo import api, fields, models,exceptions


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    on_hand_cartons = fields.Float(
        compute='_compute_on_hand_cartons', 
        string='On hand Cartons', store=True,
        readonly=True, states={'confirm': [('readonly', False)]},
        digits='Reserved Cartons', default=0)
    counted_cartons = fields.Float(
        compute='_compute_product_qty', inverse='_inverse_product_qty',
        string='Counted Cartons', store=True,
        digits='Reserved Cartons', 
        readonly=False, default=0)
    
    @api.onchange("product_qty")
    @api.depends("product_qty")
    def _compute_product_qty(self):
        for record in self:
            if record.product_qty and record.product_id and record.product_uom_id:
                record.counted_cartons = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.product_qty
            else:
                record.counted_cartons = 0

    def _inverse_product_qty(self):
        for record in self:
            if record.counted_cartons and record.product_id and record.product_uom_id:
                record.product_qty = (record.product_id.uom_po_id.factor_inv/record.product_uom_id.factor_inv)*record.counted_cartons

    # @api.onchange("theoretical_qty")
    @api.depends("theoretical_qty")
    def _compute_on_hand_cartons(self):
        for record in self:
            if record.theoretical_qty and record.product_id and record.product_uom_id:
                record.on_hand_cartons = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.theoretical_qty
            else:
                record.on_hand_cartons = 0
