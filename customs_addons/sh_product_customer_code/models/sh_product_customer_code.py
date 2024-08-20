# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class ShProductCustomerCode(models.Model):
    _name = 'sh.product.customer.info'
    _description = "Sh Product Customer Code"

    name = fields.Many2one(
        'res.partner', 'Customer',
        ondelete='cascade', required=True,
        help="Customer of this product")

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade')

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        help="If not set, the vendor price will apply to all variants of this product.")

    product_name = fields.Char(
        'Customer Product Name',
        help="This vendor's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
    product_code = fields.Char(
        'Customer Product Code',
        help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
    
#     product_template_id = fields.Many2one(
#         'product.template', string='Product Template',
#         related="product_id.product_tmpl_id", 
#         domain=[('sale_ok', '=', True), ('sh_customer_product_ids.name', '=', lambda self: self.env['sh.product.customer.info'].sudo().search([('name', '=', self.order_id.partner_id)]))])

    
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
#     product_template_id = fields.Many2one(
#         'product.template', string='Product Template',
#         related="product_id.product_tmpl_id", 
#         domain=[('sale_ok', '=', True), ('sh_customer_product_ids.name', '=', lambda self: self.order_id.partner_id.id)])

    
#     @api.onchange("order_id.partner_id")
#     def _onchange_partner_id(self):
#         for record if self:
#             record.product_template_id = 

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        partner = self.env['res.partner'].sudo().search(
            [('id', '=', self._context.get('partner_id'))], limit=1).name

        sale_product = self.product_id.product_tmpl_id.name

        customer_code = self.env['sh.product.customer.info'].sudo().search(
            [('name', '=', partner), ('product_tmpl_id', '=', sale_product)], limit=1)
        # customer_products = self.env['product.template'].sudo().search(
        #     [('sale_ok', '=', True), ('sh_customer_product_ids.name', '=', self.env['sh.product.customer.info'].sudo().search([('name', '=', self.order_id.partner_id)]))]
        # )

        des = " "
        if self.product_id.product_tmpl_id and customer_code:
            if customer_code.product_code :
                des +="[" + customer_code.product_code+"]" 
            if customer_code.product_name:
                des += customer_code.product_name
            vals.update(name=des)
        else:
            vals.update(
                name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result
