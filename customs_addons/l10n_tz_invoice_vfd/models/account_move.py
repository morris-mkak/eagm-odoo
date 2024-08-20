# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
import base64
import io
import json

import pyqrcode as pyqrcode

from .tvfd_connect import TvfdAPI
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re
import logging

_logger = logging.getLogger(__name__)


def tims_format(sting):
    # check if string type
    if isinstance(sting, str):
        if sting != '':
            return re.sub('[^A-Za-z0-9]+', ' ', sting)
    return sting


class AccountMove(models.Model):
    _inherit = 'account.move'
    l10n_tz_tvfd_verification_link = fields.Char(string='TRA Verification Link', readonly=True, copy=False)
    l10n_tz_tvfd_verification_code = fields.Char(string='TRA Verification Code', readonly=True, copy=False)
    l10n_tz_tvfd_qr = fields.Char(string='TRA QRCode', readonly=True, copy=False)
    l10n_tz_tvfd_json = fields.Char(string='TRA Response', readonly=True, copy=False)

    def l10n_tz_action_post_send_invoices(self):
        print('Sending to TRA ...')
        for move in self:
            api = TvfdAPI(move.company_id.sudo())
            # get the company
            current_company = move.company_id.sudo()
            items = []
            invoice_line_ids = move.invoice_line_ids
            for idx, invoice_line in enumerate(invoice_line_ids):
                untaxed_amount = invoice_line.price_subtotal

                tax_amount = invoice_line.price_total - invoice_line.price_subtotal
                print('----tax_amount----', tax_amount)
                tax_rate = tax_amount / untaxed_amount
                gross_price = invoice_line.price_unit + (invoice_line.price_unit * tax_rate)

                tax_incusive = invoice_line.price_total
                print('----tax_incusive----', tax_incusive)
                discount_percent = invoice_line.discount / 100
                discount_amount = gross_price * discount_percent
                print('----discount_amount----', discount_amount)
                # ensure 2 decimal places json

                item = {
                    "id": invoice_line.product_id.id,
                    "name": tims_format(invoice_line.product_id.name),  # remove sepecial characters
                    "price": round(gross_price * invoice_line.quantity, 2),
                    "qty": round(invoice_line.quantity, 2),
                    "vatGroup": invoice_line.product_id.product_tmpl_id.l10n_tz_invoice_vfd_tax_class,
                    "discount": round(discount_amount * invoice_line.quantity, 2)
                }
                items.append(item)
            tin = move.partner_id.vat
            if move.partner_id.mobile:

                phone = (tims_format(move.partner_id.mobile)[:10])
            else:
                phone = ''

            if move.partner_id.l10n_tz_invoice_vfd_id_number:
                id_value = move.partner_id.l10n_tz_invoice_vfd_id_number
            else:
                id_value = ''

            payload = {
                "serial": current_company.l10n_tz_tvfd_serial_number,
                "referenceNumber":tims_format(move.name),
		"items": items,
                "customer": {
                    "name": tims_format(move.partner_id.name),
                    "mobile": phone,
                    "idType": move.partner_id.l10n_tz_invoice_vfd_id_type,
                    "idValue": id_value
                    # "idValue": move.partner_id.l10n_tz_invoice_vfd_id_number
                },
                "payments": [
                    {
                        "type": "invoice",
                        "amount": move.amount_total
                    }
                ]
            }
            print(json.dumps(payload, indent=4))

            response_data = api.upload_invoice(payload, tims_format(move.name),
                                               move.partner_id.l10n_tz_invoice_vfd_id_type,
                                               move.partner_id.l10n_tz_invoice_vfd_id_number)
            if response_data[0] != 201:
                raise UserError(response_data[1])

            tra_data = response_data[1]

            if tra_data:
                tra_data_raw = (json.loads(tra_data))
                if 'verificationLink' in tra_data_raw:
                    print(tra_data)
                    verification_code = tra_data_raw.get('rctvnum')
                    verification_link = tra_data_raw.get('verificationLink')
                    c = pyqrcode.create(tra_data_raw['verificationLink'])
                    s = io.BytesIO()
                    c.png(s, scale=6)
                    qr_code = base64.b64encode(s.getvalue()).decode("ascii")
                    self.write({
                        'l10n_tz_tvfd_verification_link': verification_link,
                        'l10n_tz_tvfd_verification_code': verification_code,
                        'l10n_tz_tvfd_qr': qr_code,
                        'l10n_tz_tvfd_json': tra_data
                    })
                    move.message_post(body=_("verification code: %s") % verification_code)
                    move.message_post(body=_("verification link: %s") % verification_link)
                else:
                    raise UserError(
                        _('Could not upload Invoice to TRA. Got error.'))

        return True
