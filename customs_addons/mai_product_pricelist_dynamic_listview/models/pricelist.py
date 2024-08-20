# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from lxml import etree
from odoo.tools.safe_eval import test_python_expr
import xml.etree.ElementTree as ET
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _name = 'final.product.pricelist.item'
    _description = 'Final Product Pricelist Item'
    _rec_name = "pricelist_item_id"

    pricelist_id = fields.Many2one('product.pricelist')
    pricelist_item_id = fields.Many2one('product.pricelist.item')
    label = fields.Char('Discount')
    final_price = fields.Float('Price')
    product_id =  fields.Many2one('product.product')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pricelist_item_ids = fields.Many2many(
        'product.pricelist.item', 'Pricelist Items', compute='_get_pricelist_items')

    final_pricelist_item_ids = fields.One2many(
        'final.product.pricelist.item', 'product_id', compute='_get_pricelist_items_price')

    pricelist_name = fields.Char('Pricelist Name', compute='_get_pricelist_items_price')

    def _get_display_price(self, product, pricelist_id, item_id):
        if pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.env.user.partner_id.id, date=fields.Datetime.now(), uom=self.product_uom.id)

        final_price, rule_id = pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.env.user.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist_id.id)
        if currency != pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, pricelist_id.currency_id, self.env.company, fields.Date.today())
        return max(base_price, final_price)

    def _get_pricelist_items_price(self):
        fppi_obj = self.env['final.product.pricelist.item']
        new_rec_list = []
        for rec in self:
            pricelist_name = []
            if not rec.pricelist_item_ids:
                rec.final_pricelist_item_ids = [(6,0, [])]
                rec.pricelist_name = ''
            else:    
                count = 1
                pricelist_list_check = []
                for new_rec in rec.pricelist_item_ids:
                    if new_rec.pricelist_id.name not in pricelist_name:
                        pricelist_name.append(new_rec.pricelist_id.name)
                    final_price = self._get_display_price(rec, new_rec.pricelist_id, new_rec)
                    new_fppi_id = fppi_obj.create({
                        'pricelist_id': new_rec.pricelist_id.id,
                        'label': new_rec.price,
                        'product_id': rec.id,
                        'final_price': final_price,
                        'pricelist_item_id': new_rec.id
                        })
                    new_rec_list.append(new_fppi_id.id)
                    if new_rec.pricelist_id.id not in pricelist_list_check and new_rec.pricelist_id.allow_in_product_view:
                        name = 'x_pricelist_' + str(count)
                        field_id = self.env['ir.model.fields'].search([('model', '=', 'product.product'), ('name', '=', name)])
                        if field_id:
                            rec.write({name: new_rec.pricelist_id.name + ' - ' + str(round(final_price, 3))})
                        count += 1
                        pricelist_list_check.append(new_rec.pricelist_id.id)
                rec.final_pricelist_item_ids = new_rec_list
                rec.pricelist_name = ', '.join(pricelist_name)

    def _get_pricelist_items(self):
        ppi_obj = self.env['product.pricelist.item']
        for rec in self:
            pricelist_item_product_templ_ids = ppi_obj.search([
                '|',
                ('product_id', '=', rec.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('pricelist_id.allow_in_product_view', '=', True),
                ]).ids

            pricelist_item_global_ids = ppi_obj.search([
                ('applied_on', '=', '3_global'),
                ('pricelist_id.allow_in_product_view', '=', True),
                ]).ids

            pricelist_item_categ_ids = ppi_obj.search([
                ('applied_on', '=', '2_product_category'),
                ('pricelist_id.allow_in_product_view', '=', True),
                ('categ_id', '=', rec.categ_id.id)
                ]).ids

            final_list = pricelist_item_product_templ_ids + pricelist_item_global_ids + pricelist_item_categ_ids
            rec.pricelist_item_ids = final_list


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    allow_in_product_view = fields.Boolean('Allwed this Pricelist in Product Tree view?')

    def delete_common_dynamic(self):
        count = 1
        # for pricelist_id in self.search([('allow_in_product_view', '=', True)]):
        for pricelist_id in self.search([]):
            field_name = 'x_pricelist_' + str(count)
            label_name = 'Pricelist ' + str(count)
            view_id = self.env['ir.ui.view'].search([('model', '=', 'product.product'), ('type', '=', 'tree'), ('name', '=', str(pricelist_id.id))])
            if view_id:
                view_id.unlink()
            count += 1

        count = 1
        # for pricelist_id in self.search([('allow_in_product_view', '=', True)]):
        for pricelist_id in self.search([]):
            field_name = 'x_pricelist_' + str(count)
            field_id = self.env['ir.model.fields'].search([('model_id.model', '=', 'product.product'), ('name', '=', field_name)])
            if field_id:
                field_id.unlink()
            count += 1

    def create_common_dynamic(self):

        count = 1
        for pricelist_id in self.search([('allow_in_product_view', '=', True)]):
            field_name = 'x_pricelist_' + str(count)
            label_name = 'Pricelist ' + str(count)
            pricelist_id.action_add(field_name, label_name)
            count += 1

    @api.model
    def create(self, vals):
        res = super(ProductPricelist, self).create(vals)
        res.delete_common_dynamic()
        res.create_common_dynamic()
        return res

    def write(self, vals):
        res = super(ProductPricelist, self).write(vals)
        self.delete_common_dynamic()
        self.create_common_dynamic()
        return res

    # def unlink(self):
    #     res = super(ProductPricelist, self).unlink()
    #     for rec in self:
    #         rec.delete_common_dynamic()
    #         rec.create_common_dynamic()
    #     return res

    def add_new_dynamic_fields(self, field_name, label_name):
        model_id = self.env['ir.model'].search([('model', '=', 'product.product')])
        ir_model_fields_obj = self.env['ir.model.fields']
        values = {
            'model_id': model_id.id,
            'ttype': 'char',
            'name': field_name,
            'field_description': label_name,
            'model': 'product.product',
            'column1': str(self.id),
        }
        try:
            ir_model_fields_obj.create(values)
        except Exception as e:
            raise ValidationError(e)

    def xml_field_arch(self, field_name, label_name):
        xpath = etree.Element('xpath')
        name = 'product_template_attribute_value_ids'
        expr = '//' + 'field' + '[@name="' + name + '"]'
        xpath.set('expr', expr)
        xpath.set('position', 'before')
        field = etree.Element('field')
        field.set('name', field_name)
        field.set('groups', 'mai_product_pricelist_dynamic_listview.group_product_pricelist')
        field.set('options', "{'digits':[16,2]}")
        xpath.set('expr', expr)
        xpath.append(field)
        return etree.tostring(xpath).decode("utf-8")

    def action_add(self, field_name, label_name):
        self.add_new_dynamic_fields(field_name, label_name)
        arch = '<?xml version="1.0"?>' + str(self.xml_field_arch(field_name, label_name))
        vals = {
            'type': 'tree',
            'model': 'product.product',
            'inherit_id': self.env.ref('product.product_product_tree_view').id,
            'mode': 'extension',
            'arch_base': arch,
            'name': str(self.id),
        }
        ir_model = self.env['ir.model'].search([
            ('model', '=', 'product.product')])
        if hasattr(ir_model, 'module_id'):
            vals.update({'module_id': ir_model.module_id.id})
        self.env['ir.ui.view'].sudo().create(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }