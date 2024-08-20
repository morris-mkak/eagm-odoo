# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from .efris_connect import EfrisAPI
from odoo.exceptions import UserError, ValidationError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    sent_to_efris = fields.Boolean(string='Sent to Efris', default=False)

    # override the action_validate method
    def _pre_action_done_hook(self):

        print("------UGStockPicking-----")
        res = super()._pre_action_done_hook()
        print(res)
        if res:
            self.action_send_costs_to_efris()
        return res


    def action_send_costs_to_efris(self):
        api = EfrisAPI(self.env.company.sudo())
        for cost in self:
            merchant = 'Merchant'
            print(merchant)
            print('------landing_cost-------')
            sent_products = []

            for adjustment_line in cost.valuation_adjustment_lines:
                new_price = adjustment_line.x_studio_new_value_unit
                quantity = adjustment_line.quantity
                product = adjustment_line.product_id
                # get the supplier name
                if product.seller_ids:
                    supplier = product.seller_ids[0]
                    merchant = supplier.name.name
                else:
                    merchant = 'Merchant'

                if product.default_code not in sent_products:
                    new_price = round(product.standard_price, 2)
                    ura_product = {
                        'item': product.name,
                        'itemCode': product.default_code,
                        'goodsCategoryId': product.default_code,
                        "goodsCategoryName": product.l10n_ug_category_name,
                        'category': product.categ_id.name,
                        'unitPrice': new_price,
                        'qty': quantity,
                        'merchant': merchant,
                    }
                    response = api.increase_stock(ura_product,True)
                    print('------api-response-------')
                    cost.message_post(body=_(product.name + "Sent to Efris with Cost :"+str(new_price) ))
                    product.message_post(body="Increased Efris Stock by :"+str(quantity))
                    sent_products.append(product.default_code)
                    if response:
                        if response[0]['returnCode'] != '00':
                            raise ValidationError(_('Error: %s') % response[0]['returnMessage'])
            if not cost.sent_to_efris:
                cost.message_post(body=_("Sent to Efris"))
                sent_to_efris = True
                cost.write({'sent_to_efris': sent_to_efris})
