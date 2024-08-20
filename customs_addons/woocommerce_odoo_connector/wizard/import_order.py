# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
##########H#########Y#########P#########N#########O#########S##################

from dateutil.parser import parse

import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class ImportWoocommerceOrders(models.TransientModel):
    _name = 'import.woocommerce.orders'
    _inherit = 'import.orders'
    _description = "Import Woocommerce Orders"

    def _get_order_by_id(self, woocommerce, channel_id, **kwargs):
        order = woocommerce.get(f"orders/{kwargs.get('woocommerce_object_id')}").json()
        if "message" in order:
            raise UserError(f'Error in getting Order : {order["message"]}')
        return [self._process_order(woocommerce, channel_id, order)]

    def import_now(self, **kwargs):
        woocommerce = self._context.get('woocommerce')
        channel = self._context.get("channel_id")
        if kwargs.get('woocommerce_object_id'):
            data_list = self._get_order_by_id(woocommerce, channel, **kwargs)
        elif kwargs.get('woocommerce_import_date_from'):
            data_list = self._filter_order_using_date(
                woocommerce, channel, **kwargs)
        else:
            data_list = self._get_order_all(woocommerce, channel, **kwargs)
        return data_list

    def _get_woocommerce_discount_lines(self, woocommerce, data):
        amount = sum([float(line.get('discount')) for line in data["coupon_lines"]])
        tax_ids = [{"id": tax_line["rate_id"]} for tax_line in data["tax_lines"]]
        vals = {
            'line_name': "Discount",
            'line_price_unit': float(amount),
            'line_product_uom_qty': 1,
            "line_source": "discount",
            "line_taxes": self._process_taxes(woocommerce, tax_ids)
        }
        return vals

    def _get_woocommerce_order_line(self, woocommerce, channel, data):
        order_lines = []
        prod_env = self.env["import.woocommerce.products"].create({
            "channel_id": channel.id,
            "operation": "import"
        }).woocommerce_create_product_feed
        for line in data["line_items"]:
            product_id = line["product_id"]
            feed_id = prod_env(
                woocommerce, channel, product_id)
            store_variant_id = line['variation_id']
            order_line_dict = {
                'line_name': line['name'],
                'line_price_unit': float(line['subtotal']) / int(line['quantity']),
                'line_product_uom_qty': line['quantity'],
                'line_product_id': product_id,
                'line_taxes': self._process_taxes(woocommerce, line.get("taxes"))
            }
            if store_variant_id != 0:
                order_line_dict["line_variant_ids"] = store_variant_id
            order_lines.append((0, 0, order_line_dict))
        if data.get('shipping_lines'):
            order_lines += self._get_woocommerce_shipping(woocommerce, data['shipping_lines'])
        if data.get("coupon_lines"):
            discount_line = self._get_woocommerce_discount_lines(woocommerce, data)
            order_lines.append((0, 0, discount_line))
        return order_lines

    def _get_order_all(self, woocommerce, channel, **kwargs):

        url = 'orders?page={}&per_page={}&order=asc'.format(kwargs.get("page"), kwargs.get("page_size"))
        orders = woocommerce.get(url).json()

        if "message" in orders:
            raise UserError(f'Error in Getting Orders : {orders["message"]}')
        return list(map(lambda x: self._process_order(woocommerce, channel, x), orders))

    def _filter_order_using_date(self, woocommerce, channel, **kwargs):
        vals_list = []

        import_order_date = kwargs.get("woocommerce_import_date_from").isoformat()
        url = 'orders?after={}&page={}&per_page={}&order=asc'.format(import_order_date, kwargs.get("page"), kwargs.get("page_size"))
        orders = woocommerce.get(url).json()
        try:
            vals_list = list(map(lambda x: self._process_order(woocommerce, channel, x), orders))
            if kwargs.get("from_cron"):
                channel.import_order_date = parse(orders[-1].get("date_created_gmt"))
        except:
            message = "Error while importing orders : {}".format(orders["message"])
            _logger.info(message)
            if not kwargs.get("from_cron"):
                raise UserError(message)
        return vals_list

    def _get_woocommerce_shipping(self, woocommerce, shipping_line):
        return [(0, 0, {
            'line_name': "Shipping",
            'line_price_unit': shipping["total"],
            'line_product_uom_qty': 1,
            'line_source': 'delivery',
            'line_taxes': self._process_taxes(woocommerce, shipping.get("taxes"))
        }) for shipping in shipping_line]

    def _process_order(self, woocommerce, channel, order):
        order_lines = self._get_woocommerce_order_line(
            woocommerce, channel, order)
        method_title = 'Delivery'
        if order['shipping_lines']:
            method_title = order['shipping_lines'][0]['method_title']
        store_partner_id = order['customer_id']
        order_dict = {
            'store_id': order['id'],
            'channel_id': channel.id,
            "channel": channel.channel,
            'partner_id': store_partner_id or order['billing']['email'],
            'payment_method': order['payment_method'],
            'line_type': 'multi',
            'carrier_id': method_title,
            'line_ids': order_lines,
            'currency': order['currency'],
            'customer_name': order['billing']['first_name'] + " " + order['billing']['last_name'],
            'customer_email': order['billing']['email'],
            'order_state': order['status'],
        }
        if order['billing']:
            order_dict.update({
                'invoice_partner_id': store_partner_id and f'billing_{store_partner_id}' or order['billing']['email'],
                'invoice_name': order['billing']['first_name'] + " " + order['billing']['last_name'],
                'invoice_email': order['billing']['email'],
                'invoice_phone': order['billing']['phone'],
                'invoice_street': order['billing']['address_1'],
                'invoice_street2': order['billing']['address_2'],
                'invoice_zip': order['billing']['postcode'],
                'invoice_city': order['billing']['city'],
                'invoice_state_code': order['billing']['state'],
                'invoice_country_code': order['billing']['country'],
            })
        if order['shipping']:
            order_dict['same_shipping_billing'] = False
            order_dict.update({
                'shipping_partner_id': store_partner_id and f'shipping_{store_partner_id}' or order['billing']['email'],
                'shipping_name': order['shipping']['first_name'] + " " + order['billing']['last_name'],
                'shipping_street': order['shipping']['address_1'],
                'shipping_street2': order['shipping']['address_2'],
                'shipping_email': order['billing']['email'],
                'shipping_zip': order['shipping']['postcode'],
                'shipping_city': order['shipping']['city'],
                'shipping_state_code': order['shipping']['state'],
                'shipping_country_code': order['shipping']['country'],
            })
        return order_dict

    def _process_taxes(self, woocommerce, taxes):
        tax_data = []
        for tax in taxes:
            data = woocommerce.get(f"taxes/{tax.get('id')}").json()
            if "message" in data:
                _logger.info("Error in getting Taxes  %r", data["message"])
                continue
            tax_data.append(
                {
                    'rate': data.get("rate"),
                    'name': data.get('name'),
                    'type': "percent"
                }
            )
        return tax_data
