# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from .efris_connect import EfrisAPI
import threading


def trunc(num):
    return str(round(num, 2))
    sp = str(num).split('.')
    return '.'.join([sp[0], sp[1][:2]])


class Picking(models.Model):
    _inherit = 'stock.picking'
    # dont copy
    sent_to_efris = fields.Boolean(string='Sent to Efirs', default=False,copy=False)

    def button_validate(self):
        res = super().button_validate()
        print('stock.picking button_validate clicked')
        print(res)
        if res is True:
            print('super worked ok')
            self.action_send_picking_to_ura()
        return res

    def s_pre_action_done_hook(self):

        print("------UGStockPicking-----")
        res = super()._pre_action_done_hook()
        print(res)
        sent_products =[]
        if res:
            print("------StockPicking-----")
            for picking in self:
                if not sent_products:
                    picking.sent_to_efris=False
                efris_action = picking.picking_type_id.efirs_action
                if efris_action in ('reduce', 'increase'):
                    picking.message_post(body=_("Sent to efris action"+efris_action))
                    api = EfrisAPI(picking.company_id.sudo())
                    lines = picking.move_line_ids
                    for line in lines:
                        product = line.product_id
                        picking.message_post(body=_("Sent to efris product " + product.name))
                        ura_product = {
                            'item': product.name,
                            'merchant': picking.partner_id.name,
                            'itemCode': product.default_code,
                            'goodsCategoryId': product.default_code,
                            "goodsCategoryName": product.l10n_ug_category_name,
                            'category': product.categ_id.name,
                            'unitPrice': trunc(product.standard_price),
                            'qty': line.qty_done,
                        }

                        if not picking.sent_to_efris:
                            if efris_action == 'reduce':
                                sent_products.append(product.name)
                                print("reducing_stock")
                                ura_product['remarks'] = picking.picking_type_id.name
                                ura_product['merchant'] = ""
                                api.reduce_stock(ura_product)
                                picking.message_post(
                                    body=_(product.name + "Reduced in Efris with :" + str(line.qty_done)))
                                product.message_post(
                                    body=_("Reduced in Efris with :" + str(line.qty_done)))
                            elif efris_action == 'increase':
                                sent_products.append(product.name)
                                print("increasing_stock")
                                api.increase_stock(ura_product)
                                picking.message_post(
                                    body=_(product.name + "Increased in Efris with :" + str(line.qty_done)))
                                product.message_post(
                                    body=_("Increased in Efris with :" + str(line.qty_done)))
                            else:
                                print("Can not Send to Efris")
                        # return False
                    if not picking.sent_to_efris and sent_products:
                        picking.sent_to_efris = True
                        picking.message_post(body=_("Sent to Efris"))
                        sent_to_efris = True
                        picking.write({'sent_to_efris': sent_to_efris})
                    else:
                        picking.message_post(body=_("Not modified in Efris"))

        # return False
        return res

    def action_send_picking_to_ura(self):

        print("------UGStockPicking-----")

        for picking in self:
            efris_action = picking.picking_type_id.efirs_action
            print(efris_action)
            print(picking.picking_type_id.name)
            if efris_action in ('reduce', 'increase'):
                api = EfrisAPI(picking.company_id.sudo())
                lines = picking.move_line_ids
                print(lines)
                for line in lines:
                    product = line.product_id
                    ura_product = {
                        'item': product.name,
                        'merchant': picking.partner_id.name,
                        'itemCode': product.default_code,
                        'goodsCategoryId': product.default_code,
                        "goodsCategoryName": product.l10n_ug_category_name,
                        'category': product.categ_id.name,
                        'unitPrice': trunc(product.standard_price),
                        'qty': line.qty_done,
                    }

                    if not picking.sent_to_efris:
                        if efris_action == 'reduce':
                            ura_product['remarks'] = picking.picking_type_id.name
                            ura_product['merchant'] = ""
                            api.reduce_stock(ura_product)
                            picking.message_post(
                                body=_(product.name + "Reduced in Efris with :" + str(line.qty_done)))
                            product.message_post(
                                body=_("Reduced in Efris with :" + str(line.qty_done)))
                        elif efris_action == 'increase':
                            api.increase_stock(ura_product)
                            picking.message_post(
                                body=_(product.name + "Increased in Efris with :" + str(line.qty_done)))
                            product.message_post(
                                body=_("Increased in Efris with :" + str(line.qty_done)))
                    else:
                        print("Already Sent to Efris")
                    # return False
                if not picking.sent_to_efris:
                    picking.sent_to_efris = True
                    picking.message_post(body=_("Sent to Efris"))
                    sent_to_efris = True
                    picking.write({'sent_to_efris': sent_to_efris})


class PickingType(models.Model):
    _inherit = 'stock.picking.type'
    efirs_action = fields.Selection([
        ('none', 'None'),
        ('reduce', 'Reduce Stock'),
        ('increase', 'Increase Stock'),
    ], string='Efris Action', default='none')
