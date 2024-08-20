from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_value = fields.Float(
        compute='_compute_tax_value', 
        string='Tax Value', store=True,
        readonly=True, default=0)
    done_ctns = fields.Float(
        compute='_compute_done_ctns', inverse='_inverse_done_ctns',
        string='Done Ctns', store=True,
        digits='Reserved Cartons', 
        readonly=False, default=0)
    
    @api.onchange("tax_ids", "quantity", "price_unit")
    @api.depends("tax_ids", "quantity", "price_unit")
    def _compute_tax_value(self):
        for record in self:
            if record.tax_ids and record.price_unit:
                tax_val = 0
                for tax in record.tax_ids:
                    tax_val = (tax.amount/100)*record.price_unit*record.quantity
                record.tax_value = tax_val
            else:
                record.tax_value = 0
    
    @api.onchange("quantity")
    @api.depends("quantity")
    def _compute_done_ctns(self):
        for record in self:
            if record.quantity and record.product_id and record.product_uom_id:
                record.done_ctns = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.quantity
    
    @api.onchange("done_ctns")
    @api.depends("done_ctns")
    def _inverse_done_ctns(self):
        for record in self:
            if record.done_ctns and record.product_id and record.product_uom_id:
                record.quantity = (record.product_id.uom_po_id.factor_inv/record.product_uom_id.factor_inv)*record.done_ctns