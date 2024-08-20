# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    edifact_file = fields.Char(
        string='EDI File',
        help='The EDI file generated for the purchase order.',
    )
    edifact_file_name = fields.Char(
        string='EDI File Name',
        help='The EDI file name generated for the purchase order.',
    )


    def action_create_edifact(self):
        self.ensure_one()
        for order in self:
            print('====================')
            print("order", order)
            supplier = order.partner_id
            print("supplier", supplier)
            # start edifact message
            sender_id = supplier.edifact_sender_id
            sender_name = supplier.edifact_sender_name
            buyer_address_id = supplier.edifact_buyer_address_id
            supplier_address_id = supplier.edifact_supplier_address_id
            # 00000000000173
            order_id = order.id
            pad_order_id = str(order_id).zfill(14)
            message_id = str(order_id).zfill(9)
            order_date = order.date_order.strftime("%y%m%d")
            print('=========order_date========')
            print(order.date_order)
            print(order_date)
            print('=========order_date========')
            order_time = order.date_order.strftime("%H%M")
            # remove leading zeror from order_time
            dtm_time = order_time.lstrip('0')

            edifact_message = f'UNB+UNOA:3+{sender_name}:14+{sender_id}:14+{order.date_order.strftime("%y%m%d")}:{order.date_order.strftime("%H%M")}+{pad_order_id}'
            # 			new line character
            edifact_message += '\' \r'
            # 			add message reference
            edifact_message += f'UNH+1+ORDERS:D:96A:UN:EAN008'
            edifact_message += '\'\r'
            edifact_message += f'BGM+220::9+{message_id}+9'
            edifact_message += '\'\r'
            edifact_message += f'DTM+137:{order.date_order.strftime("%Y%m%d")}:102'
            edifact_message += '\'\r'
            edifact_message += f'DTM+2:{order.date_order.strftime("%Y%m%d")}:102'
            edifact_message += '\'\r'
            edifact_message += 'FTX+ZZZ+++::::'
            edifact_message += '\'\r'
            edifact_message += f'NAD+BY+{buyer_address_id}::9'
            edifact_message += '\'\r'
            edifact_message += f'NAD+DP+{buyer_address_id}::9'
            edifact_message += '\'\r'
            edifact_message += f'NAD+SU+{supplier_address_id}::9'
            edifact_message += '\'\r'
            # 				Loop through order lines
            count = 0
            for line in order.order_line:
                count += 1
                line_count = str(count).zfill(6)
                item_code = line.product_id.default_code
                qty = line.product_qty
                price = line.price_unit
                # get uom code
                print('====================')
                print("line.product_uom", line.product_uom.edifact_uom_code)
                uom_code = line.product_uom.edifact_uom_code if line.product_uom.edifact_uom_code else '00000000000010'
                # todo create field in product for edifact order quantity unit code
                # 00000000000015

                qty_padded = str(qty)
                # remove the decimal point
                qty_padded = qty_padded.replace('.0', '')
                qty_padded = str(qty_padded).zfill(14)
                edifact_message += f'LIN+{line_count}++:SA'
                edifact_message += '\'\r'
                edifact_message += f'PIA+1+{item_code}:IN'
                edifact_message += '\'\r'
                edifact_message += f'QTY+21:{qty_padded}'
                edifact_message += '\'\r'
                edifact_message += f'PRI+AAA:999'
                edifact_message += '\'\r'
            # 			end loop
            edifact_message += f'UNS+S'
            edifact_message += '\'\r'
            total_lines = (count * 4) + 9
            total_lines = str(total_lines).zfill(6)
            edifact_message += f'UNT+{total_lines}+1'
            edifact_message += '\'\r'
            edifact_message += f'UNZ+1+{pad_order_id}'
# 			save thi    s to file
            file_name = f'EAGM_ODER{pad_order_id}.edi'
            edifact_message += '\''
            # convert to bytes
            edifact_message = bytes(edifact_message, 'utf-8')

            order.write(
                {'edifact_file': edifact_message, 'edifact_file_name': file_name}
            )
#             redirect to controller
            return self.action_view_edifact()

    def action_view_edifact(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/purchase_edifact/purchase_order/%s' % self.id,
            'target': 'self',
        }

