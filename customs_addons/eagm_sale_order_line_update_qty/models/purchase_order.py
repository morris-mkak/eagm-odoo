from odoo import api, fields, models,exceptions


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    total_skus = fields.Float(compute='_compute_total_skus', inverse='_inverse_skus',
        string='SKUs', 
        digits='Reserved Cartons', 
        required=True, readonly=False, default=1.0)

    @api.onchange("product_qty")
    @api.depends("product_uom", "product_template_id", "product_qty")
    def _compute_total_skus(self):
        for record in self:
            if record.product_qty and record.product_template_id:
                record.total_skus = (record.product_template_id.uom_po_id.factor_inv/record.product_template_id.uom_id.factor_inv)*record.product_qty
 
    @api.onchange("total_skus")
    def _inverse_skus(self):
        for record in self:
            if record.total_skus and record.product_template_id:
                record.product_qty = (record.product_template_id.uom_id.factor_inv/record.product_template_id.uom_po_id.factor_inv)*record.total_skus
