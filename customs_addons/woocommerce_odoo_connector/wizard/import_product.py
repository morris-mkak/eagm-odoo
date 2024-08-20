#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H########Y#########P#########N#########O##########S##################
from dateutil.parser import parse

import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.addons.multi_channel_sale.tools import remove_tags


class ImportWoocommerceProducts(models.TransientModel):
    _name = "import.woocommerce.products"
    _inherit = 'import.templates'
    _description = "Import Woocommerce Products"

    def _get_product_basics(self, woocommerce, channel, product_data):
        feed_vals = dict(
            name=product_data["name"],
            channel_id=channel.id,
            channel=channel.channel,
            store_id=product_data["id"],
            list_price=product_data.get("price"),
            extra_categ_ids=self._get_category_string(woocommerce, channel, product_data['categories']),
            weight=product_data.get("weight"),
            description_sale=remove_tags(product_data.get("short_description")),
            description_purchase=remove_tags(product_data.get("description")),
            default_code=product_data.get("sku"),
            qty_available=product_data.get("stock_quantity"),
        )
        try:
            feed_vals['image_url'] = product_data.get("images")[0].get('src')
        except:
            pass
        return feed_vals

    def _get_category_string(self, woocommerce, channel, categories):
        str_ids = ','.join([str(category["id"]) for category in categories])
        if str_ids:
            cat_list = woocommerce.get(f'products/categories?include={str_ids}').json()
            self._woocommerce_create_product_categories(
                woocommerce, channel, cat_list)
        return str_ids

    def _get_product_all(self, woocommerce, channel, **kwargs):
        url = 'products?page={}&per_page={}&order=asc'.format(kwargs.get("page"), kwargs.get("page_size"))
        products = woocommerce.get(url).json()

        if "message" in products:
            message = "Error in getting products : {}".format(products["message"])
            _logger.info(message)
            raise UserError(message)
        return list(map(lambda x: self._get_product_dict(woocommerce, channel, x), products))

    def _woocommerce_create_product_categories(self, woocommerce, channel, datas):
        import_category_obj = self.env['import.woocommerce.categories'].create({
            "channel_id": channel.id,
            "operation": "import"
        })
        [self.env['category.feed'].create(import_category_obj._get_category_vals(data))
         for data in datas]

    def _get_feed_variants(self, woocommerce, channel, product_id, variation_ids):
        variant_list = []
        attribute_list = []
        image = False
        for variant_id in variation_ids:
            variant = woocommerce.get(
                'products/' + str(product_id) + "/variations/" + str(variant_id)).json()
            if "message" in variant:
                _logger.info("Error in getting Variants : %r", variant["message"])
                continue
            if variant['attributes']:
                attribute_list = [{
                    'name': attribute['name'],
                    'value': attribute['option'],
                    'attrib_name_id': attribute["id"],
                    'attrib_value_id': attribute['option']
                } for attribute in variant['attributes']]
                if isinstance(variant['image'], list):
                    image = variant['images'][0]['src']
                else:
                    image = variant['image']['src']
            variant_list.append({
                'image_url': image,
                'name_value': attribute_list,
                'store_id': variant['id'],
                'list_price': float(variant['price']),
                'qty_available': variant['stock_quantity'],
                'weight': variant.get("weight"),
                'default_code': variant.get('sku'),
            })
        return variant_list

    def _get_product_dict(self, woocommerce, channel, product):
        vals = self._get_product_basics(
            woocommerce, channel, product)
        if product['type'] == 'variable':
            vals.update(variants=self._get_feed_variants(
                woocommerce, channel, product['id'], product['variations']))
        return vals

    def woocommerce_create_product_feed(self, woocommerce, channel_id, product_id):
        vals = {}
        url = 'products/%s' % product_id
        product = woocommerce.get(url).json()
        if "message" in product:
            _logger.info("Error in getting Product : %r", product['message'])
            return False
        product_basics = self._get_product_basics(
            woocommerce, channel_id, product)
        vals.update(product_basics)
        if product['type'] == 'variable':
            variation_ids = product['variations']
            variants = self._get_feed_variants(
                woocommerce, channel_id, product['id'], variation_ids)
            variants = [(0, 0, variant) for variant in variants]
            vals.update(feed_variants=variants)

        match = self.channel_id.match_product_feeds(vals['store_id'])
        if not match:
            return self.env['product.feed'].create(vals)
        else:
            match.write(vals)
            return match

    def _get_product_by_id(self, woocommerce, channel_id, **kwargs):
        product = woocommerce.get(f"products/{kwargs.get('woocommerce_object_id')}").json()
        if "message" in product:
            raise UserError(f"Error in getting products : {product['message']}")
        return [self._get_product_dict(woocommerce, channel_id, product)]

    def import_now(self, **kwargs):
        woocommerce = self._context.get('woocommerce')
        channel = self._context.get('channel_id')
        if kwargs.get('woocommerce_object_id'):
            data_list = self._get_product_by_id(woocommerce, channel, **kwargs)
        elif kwargs.get('woocommerce_import_date_from'):
            data_list = self._filter_product_using_date(
                woocommerce, channel, **kwargs)
        else:
            data_list = self._get_product_all(woocommerce, channel, **kwargs)
        return data_list

    def _filter_product_using_date(self, woocommerce, channel, **kwargs):
        vals_list = []

        product_import_date = kwargs.get("woocommerce_import_date_from").isoformat()
        url = 'products?after={}&page={}&per_page={}&order=asc'.format(product_import_date,kwargs.get("page"),kwargs.get("page_size") )
        products = woocommerce.get(url).json()

        try:
            vals_list = list(map(lambda x: self._get_product_dict(woocommerce, channel, x), products))
            if kwargs.get("from_cron"):
                channel.import_product_date = parse(products[-1].get("date_created_gmt"))
        except:
            msg = f"Error in getting product data :{products['message']}"
            _logger.info(msg)
            if not kwargs.get("from_cron"):
                raise UserError(msg)
        return vals_list
