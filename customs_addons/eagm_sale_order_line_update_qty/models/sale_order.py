from odoo import api, fields, models, exceptions


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_order_ref = fields.Char(string='Customer Reference', copy=False)

    _sql_constraints = [
        ('client_order_ref_unique', 'unique(client_order_ref)',
         'client order ref already exists!')
    ]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cartons = fields.Float(compute='_compute_cartons',
                           inverse='_inverse_cartons',
                           string='Cartons',
                           digits='Reserved Cartons',
                           required=True, readonly=False, default=1.0)
    order_customer_id = fields.Many2one(related='order_id.partner_id',
                                        store=True,
                                        string='Sale Order Customer',
                                        readonly=False)

    # product_template_id = fields.Many2one(
    #     'product.template', string='Product Template',
    #     related="product_id.product_tmpl_id",
    #     domain=[('sale_ok', '=', True), ('sh_customer_product_ids.name', '=', lambda self: self.order_customer_id)])

    # product_template_id = fields.Many2one(
    #     'product.template', string='Product Template',
    #     related="product_id.product_tmpl_id",
    #     domain=[('sale_ok', '=', True), ('sh_customer_product_ids.name', 'in', lambda self: self.order_customer_id)])

    @api.onchange('order_customer_id')
    def _onchange_order_customer_id(self):
        res = {}
        res['domain'] = {'product_template_id': [('sale_ok', '=', True), (
        'sh_customer_product_ids.name', 'in', self.order_customer_id)]}
        # for record in self:
        #     record.product_template_id = self.env['product.template'].search([('sale_ok', '=', True), ('sh_customer_product_ids.name', 'in', record.order_customer_id)])
        return res

    @api.onchange("x_studio_many2one_field_zjCGw")
    def _onchange_customer_product_code(self):
        for record in self:
            if record.x_studio_many2one_field_zjCGw:
                record.product_template_id = record.x_studio_many2one_field_zjCGw.product_id
                record.product_uom = record.product_template_id.uom_id
                record.qty_available_today = record.product_template_id.qty_available
                record.price_unit = record.product_template_id.list_price
                record.tax_id = record.product_template_id.taxes_id

    @api.onchange("product_uom_qty", "product_uom")
    @api.depends("product_uom", "product_template_id", "product_uom_qty")
    def _compute_cartons(self):
        for record in self:
            if record.product_uom_qty and record.product_template_id:
                record.cartons = (
                                             record.product_uom.factor_inv / record.product_template_id.uom_po_id.factor_inv) * record.product_uom_qty

    @api.onchange("cartons")
    def _inverse_cartons(self):
        for record in self:
            if record.cartons and record.product_template_id:
                record.product_uom_qty = (
                                                     record.product_template_id.uom_po_id.factor_inv / record.product_uom.factor_inv) * record.cartons