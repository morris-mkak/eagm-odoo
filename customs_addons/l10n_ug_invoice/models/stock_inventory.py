from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import OrderedSet
from odoo import models, fields, api, _
from .efris_connect import EfrisAPI
from odoo.exceptions import UserError, ValidationError


def trunc(num):
    return str(round(num, 2))
    sp = str(num).split('.')
    return '.'.join([sp[0], sp[1][:2]])


class Inventory(models.Model):
    _inherit = "stock.inventory"
    sent_to_efris = fields.Boolean(string="Sent to Efris", default=False)

    def action_validate(self):
        res = super().action_validate()
        print('------action_validate-------')
        print(res)
        return res

    def action_adjust_quantity_in_efris(self):
        api = EfrisAPI(self.env.company.sudo())
        # Type hint

        for stock_inventory in self:
            print(stock_inventory)
            merchant = 'Merchant'
            print(merchant)
            print('------landing_cost-------')
            sent_products = []

            for stock_inventory_line in stock_inventory.line_ids:
                print(stock_inventory_line)
                product = stock_inventory_line.product_id
                difference_qty = stock_inventory_line.product_qty - stock_inventory_line.theoretical_qty
                # absoulte value
                # difference_qty = abs(difference_qty)
                ura_product = {
                    'item': product.name,
                    'merchant': "",
                    'itemCode': product.default_code,
                    'goodsCategoryId': product.default_code,
                    "goodsCategoryName": product.l10n_ug_category_name,
                    'category': product.categ_id.name,
                    'unitPrice': trunc(product.standard_price),
                    'qty': abs(difference_qty),
                }
                if difference_qty > 0:
                    api.increase_stock(ura_product)
                    stock_inventory.message_post(
                        body=_(product.name + " Increased in Efris with :" + str(difference_qty)))

                elif difference_qty < 0:
                    ura_product['merchant'] = ""
                    api.reduce_stock(ura_product)

                    stock_inventory.message_post(
                        body=_(product.name + " Reduced in Efris with :" + str(difference_qty)))

                sent_products.append(product.id)
            stock_inventory.sent_to_efris = True
            stock_inventory.message_post(body=_("Sent to Efris"))
            stock_inventory.write({
                'sent_to_efris': True
            })

    def action_synch_quantity_in_efris(self):
        api = EfrisAPI(self.env.company.sudo())
        # Type hint

        for stock_inventory in self:
            if not stock_inventory.sent_to_efris:

                print(stock_inventory)
                merchant = 'Merchant'
                print(merchant)
                print('------landing_cost-------')
                sent_products = []

                for stock_inventory_line in stock_inventory.line_ids:
                    print(stock_inventory_line)
                    product = stock_inventory_line.product_id
                    stock_in_odoo = stock_inventory_line.product_qty
                    # get qunatity in efris
                    stock_in_efris = self.get_sock_in_ura(product)
                    difference_qty = stock_in_odoo - stock_in_efris

                    ura_product = {
                        'item': product.name,
                        'merchant': "",
                        'itemCode': product.default_code,
                        'goodsCategoryId': product.default_code,
                        "goodsCategoryName": product.l10n_ug_category_name,
                        'category': product.categ_id.name,
                        'unitPrice': trunc(product.standard_price),
                        'qty': abs(difference_qty),
                    }
                    self.update_stock_in_ura(ura_product,stock_in_efris,stock_in_odoo,"",api)

                    sent_products.append(product.id)
                stock_inventory.sent_to_efris = True
                stock_inventory.message_post(body=_("Sent to Efris"))
                stock_inventory.write({
                    'sent_to_efris': True
                })
            else:

                stock_inventory.message_post(body=_("Already Sent to Efris"))
                print("Aready Sent to Efris")

    def get_sock_in_ura(self, product, fetch_efris_id=False):

        api = EfrisAPI(self.env.company.sudo())
        if not product.l10n_ug_invoice_efris_id or fetch_efris_id:

            good = {"goodsCode": product.default_code}
            print('------good-------')
            print(good)
            response = api.query_good(good)
            print('------api-response-------')
            print(response)
            if response:
                if not response['records']:
                    # log error
                    product.message_post(body="No stock found in Efris")
                    return 0
                    # raise ValidationError(_('Error: %s') % 'No record found')
                else:
                    good_id = response['records'][0]['id']
                    product.write({'l10n_ug_invoice_efris_id': good_id})
                    product.message_post(body="URA Product ID: %s" % good_id)
        query_request = {
            "id": product.l10n_ug_invoice_efris_id,
        }
        query_response = api.query_good_quantity(query_request)
        print('------query_response-------')
        print(query_response)
        stock = query_response['stock']
        if stock:
            return float(stock)
        return 0


    def update_stock_in_ura(self, ura_product, stock_in_efris, stock_in_odoo, merchant, api):
        if stock_in_efris < stock_in_odoo:
            # increate stock
            #     get the difference betwen thre etwo and update the stock
            stock_adjustment = stock_in_odoo - stock_in_efris
            ura_product['qty'] = stock_adjustment
            # get the product supplier
            ura_product['merchant'] = "EAGM"
            print('increase stock')
            response = api.increase_stock(ura_product)
            print('------increase-stock-response-------')
            print(response)
        else:
            # decrease stock
            print('decrease stock')
            stock_adjustment = abs(stock_in_odoo - stock_in_efris)
            ura_product['qty'] = stock_adjustment
            response = api.reduce_stock(ura_product)

        return response

