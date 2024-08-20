# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json

import pytz

from .efris_connect import EfrisAPI
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_repr
import logging

_logger = logging.getLogger(__name__)


def trunc(num):
    # if str the floatvar
    if isinstance(num, str):
        num = float(num)

    return str(round(num, 2))

    sp = str(num).split('.')
    return '.'.join([sp[0], sp[1][:2]])


class AccountMove(models.Model):
    _inherit = 'account.move'
    device_id = '1000020972_01'
    l10n_ug_antifake_code = fields.Char(string='Verification Code', readonly=True, copy=False)
    l10n_ug_reference_no = fields.Char(string='Reference Number', readonly=True, copy=False)
    l10n_ug_invoice_id = fields.Char(string='URA ID', readonly=True, copy=False)
    l10n_ug_invoice_number = fields.Char(string='Fiscal Document Number', readonly=True, copy=False)
    l10n_ug_credit_note_number = fields.Char(string='CreditNote Number', readonly=True, copy=False)
    l10n_ug_send_datetime = fields.Datetime(string='Date Send to URA', readonly=True, copy=False)

    l10n_ug_delivery_date = fields.Date(string='Delivery Date', default=fields.Date.context_today, copy=False,
                                        readonly=True, states={'draft': [('readonly', False)]},
                                        help="In case of multiple deliveries, you should take the date of the latest "
                                             "one. ")
    l10n_ug_show_delivery_date = fields.Boolean(compute='_compute_show_delivery_date')
    l10n_ug_qr_code_str = fields.Char(string='URA QR Code', readonly=True, copy=False)
    l10n_ke_qrcode = fields.Char(string='Unused QR Code', readonly=True, copy=False)
    l10n_ke_cu_qr_code_str = fields.Char(string='l10n_ke_cu_qr_code_str', readonly=True, copy=False)
    l10n_ke_cu_invoice_number = fields.Char(string='KRA Invoice Number', readonly=True, copy=False)
    l10n_ke_json = fields.Char(string='TIMS JSON', readonly=True, copy=False)
    l10n_ke_cu_confirmation_datetime = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)
    l10n_ke_cu_serial_number = fields.Char(string='CU Serial Number', readonly=True, copy=False)
    l10n_ke_cu_pin_number = fields.Char(string='CU PIN Number', readonly=True, copy=False)
    l10n_ke_cu_sys_datetime = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)

    l10n_ug_confirmation_datetime = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)

    def l10n_ug_action_upload_invoice_items(self):
        for move in self:
            api = EfrisAPI(move.company_id.sudo())
            for line in move.invoice_line_ids:
                product = line.product_id
                product_template = product.product_tmpl_id
                print('------------------product_template------------------', product_template)
                product_template.action_send_product_to_ura()
                product_template.action_update_product_quantity_to_ura()
            move.write({'l10n_ug_send_datetime': datetime.datetime.now()})

    def l10n_ug_action_post_sign_invoices(self):
        # raise UserError(
        #     _('Could not upload Invoice to eFris. Got error.'))
        print('------------------action_post_sign_invoices------------------')
        ivoice_data = self._compute_ura_invoice_qr(self)

    def l10n_ug_action_check_ura_status(self):

        for move in self:
            api = EfrisAPI(move.company_id.sudo())


            return_data = api.query_invoice_by_ref(move.name)
            print('------------------action_query_credit_note------------------', return_data)
            if return_data:
                move.write({
                    'l10n_ug_antifake_code': return_data['basicInformation']['antifakeCode'],
                    'l10n_ug_invoice_id': return_data['basicInformation']['invoiceId'],
                    'l10n_ug_invoice_number': return_data['basicInformation']['invoiceNo'],
                    'l10n_ug_qr_code_str': return_data['summary']['qrCode'],

                })
                move.message_post(body=_("antifakeCode: %s") % return_data['basicInformation']['antifakeCode'])
                move.message_post(body=_("invoiceId: %s") % return_data['basicInformation']['invoiceId'])
                move.message_post(body=_("invoiceNo: %s") % return_data['basicInformation']['invoiceNo'])

    def l10n_ug_action_query_credit_note(self):
        for move in self:
            api = EfrisAPI(move.company_id.sudo())
            print('------------------action_query_credit_note------------------')
            print(move.l10n_ug_reference_no)
            payload = {
                "referenceNo": move.l10n_ug_reference_no,
                "queryType": "1",
                "invoiceApplyCategoryCode": "101",
                "pageNo": "1",
                "pageSize": "10",
                "creditNoteType": "1"
            }
            return_data = api.query_credit_note(payload)
            if return_data.get("returnCode", '00') != "00":
                raise UserError(
                    _('Could not upload Invoice to eFris. Got error.') + "\n" + return_data.get(
                        "returnMessage"))

            move.l10n_ug_antifake_code = return_data['basicInformation']['antifakeCode']
            move.l10n_ug_invoice_id = return_data['basicInformation']['invoiceId']
            move.l10n_ug_invoice_number = return_data['basicInformation']['invoiceNo']
            move.l10n_ug_qr_code_str = return_data['summary']['qrCode']

            self.write({
                'l10n_ug_antifake_code': return_data['basicInformation']['antifakeCode'],
                'l10n_ug_invoice_id': return_data['basicInformation']['invoiceId'],
                'l10n_ug_invoice_number': return_data['basicInformation']['oriInvoiceNo'],
                'l10n_ug_credit_note_number': return_data['basicInformation']['invoiceNo'],
                'l10n_ug_qr_code_str': return_data['summary']['qrCode'],

            })
            move.message_post(body=_("antifakeCode: %s") % return_data['basicInformation']['antifakeCode'])
            move.message_post(body=_("invoiceId: %s") % return_data['basicInformation']['invoiceId'])
            move.message_post(body=_("l10n_ug_credit_note_number: %s") % return_data['basicInformation']['invoiceNo'])
            move.message_post(body=_("invoiceNo: %s") % return_data['basicInformation']['oriInvoiceNo'])
        return True

    @api.depends('country_code', 'move_type')
    def _compute_show_delivery_date(self):
        for move in self:
            move.l10n_ug_show_delivery_date = move.country_code in ('UG') and move.move_type in (
                'out_invoice', 'out_refund')

    def _compute_ura_invoice_qr(self, move):
        api = EfrisAPI(move.company_id.sudo())
        # efris_data = api.mock_upload()
        if move.partner_id.is_company and move.partner_id.vat == False:
            raise UserError(_('Please enter TIN number for company %s') % move.partner_id.name)

        # return invoice_data
        if move.move_type in 'out_invoice':
            invoice_data = self._generate_efris_invoice(move)
            return_data = api.upload_invoice(invoice_data, False)
            print('------------------return_data------------------', return_data)
            if return_data.get("returnCode", '00') != "00":
                raise UserError(
                    _('Could not upload Invoice to eFris. Got error.') + "\n" + return_data.get(
                        "returnMessage"))

            move.l10n_ug_antifake_code = return_data['basicInformation']['antifakeCode']
            move.l10n_ug_invoice_id = return_data['basicInformation']['invoiceId']
            move.l10n_ug_invoice_number = return_data['basicInformation']['invoiceNo']
            move.l10n_ug_qr_code_str = return_data['summary']['qrCode']

            self.write({
                'l10n_ug_antifake_code': return_data['basicInformation']['antifakeCode'],
                'l10n_ug_invoice_id': return_data['basicInformation']['invoiceId'],
                'l10n_ug_invoice_number': return_data['basicInformation']['invoiceNo'],
                'l10n_ug_qr_code_str': return_data['summary']['qrCode'],

            })
            move.message_post(body=_("antifakeCode: %s") % return_data['basicInformation']['antifakeCode'])
            move.message_post(body=_("invoiceId: %s") % return_data['basicInformation']['invoiceId'])
            move.message_post(body=_("invoiceNo: %s") % return_data['basicInformation']['invoiceNo'])
        else:
            invoice_data = self._generate_efris_credit_note(move)
            return_data = api.upload_invoice(invoice_data, False, 'credit_note')
            if return_data.get("returnCode", '00') != "00":
                raise UserError(
                    _('Could not upload Invoice to eFris. Got error.') + "\n" + return_data.get(
                        "returnMessage"))
            move.message_post(body=_("referenceNo: %s") % return_data['referenceNo'])
            self.write({
                'l10n_ug_reference_no': return_data['referenceNo'],

            })

    def _generate_efris_invoice(self, record):
        invoice_type = 1
        if record.move_type in 'out_invoice' and record.country_code in 'UG':
            invoice_type = 1
            amount_multiplier = 1
        elif record.move_type in 'out_refund' and record.country_code in 'UG':
            invoice_type = 2
            amount_multiplier = -1
        seller_name = record.company_id.display_name
        tin = record.company_id.vat
        # odoo get invoice lien items from move
        # currenttime_str = fields.Datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        currenttime_str = fields.Datetime.now().strftime("%Y%d%m%H%M%S")
        sellerDetails = {
            "tin": record.company_id.vat,
            "legalName": record.company_id.display_name,
            "businessName": record.company_id.name,
            "address": record.company_id.street,
            "mobilePhone": record.company_id.phone,
            "linePhone": record.company_id.phone,
            "emailAddress": record.company_id.email,
            "placeOfBusiness": record.company_id.base_onboarding_company_state,
            # "referenceNo": str(record.id)+"_"+currenttime_str,
            "referenceNo": record.name,
            "isCheckReferenceNo": "0"
        }
        basicInformation = {
            "invoiceId": record.name,
            "deviceNo": self.device_id,
            "issuedDate": "{:%Y-%m-%d}".format(record.date),
            "operator": record.invoice_user_id.login,
            "currency": "UGX",
            "oriInvoiceId": record.l10n_ug_invoice_id,
            "oriInvoiceNo": record.l10n_ug_invoice_number,
            "invoiceType": invoice_type,  # 1 invoice 2 credit note
            "invoiceKind": "1",
            "dataSource": "103",
            "invoiceIndustryCode": "101",
            "isBatch": "0"
        }
        # rverse
        print('------------------country_code------------------')
        print(record.country_code)
        if record.move_type in 'out_refund' and record.country_code in 'UG':
            basicInformation['oriInvoiceId'] = record.reversed_entry_id.l10n_ug_invoice_id
            basicInformation['oriInvoiceNo'] = record.reversed_entry_id.l10n_ug_invoice_number
            basicInformation['reasonCode'] = 102
            basicInformation['reason'] = "Oder Canceled"
            #     remove invoiceId
            basicInformation['invoiceId'] = False

        buyerDetails = {
            "buyerLegalName": record.partner_id.name,
            "buyerType": "1",
            "buyerCitizenship": "1",
            "buyerSector": "1",
            "buyerReferenceNo": record.name
        }
        if record.partner_id.vat:
            buyerDetails['buyerTin'] = record.partner_id.vat
        if record.partner_id.is_company:
            buyerDetails['buyerReferenceNo'] = record.name
            buyerDetails['buyerType'] = 0

        buyerExtend = {}
        goods_details = []

        invoice_line_ids = record.invoice_line_ids
        # TODO ignore the tax line
        # python push goodsDetail to goodsDetails
        invoice_gross_amount = 0
        invoice_net_amount = 0
        invoice_tax_amount = 0

        line_count = -1
        for idx, invoice_line in enumerate(invoice_line_ids):
            print('invoice_line', invoice_line)
            # print(invoice_line)
            discount_amount = 0
            discount_tax_amount = 0
            discount_net_amount = 0
            qty = invoice_line.quantity
            unit_price_net = invoice_line.price_unit
            unit_price_gross = float(trunc(unit_price_net * 1.18))  # TODO get tax rate from tax
            sub_total = unit_price_net * qty
            gross_total = unit_price_gross * qty
            tax_amount = gross_total - sub_total

            line_count += 1

            goods_detail = {
                "merchant": "",
                "deemedFlag": "2",
                "discountFlag": "2",
                "exciseFlag": "2",
                "exciseTax": "0",
                "goodsCategoryId": invoice_line.product_id.product_tmpl_id.l10n_ug_invoice_category_id,
                # TODO get from product
                "goodsCategoryName": invoice_line.product_id.product_tmpl_id.l10n_ug_category_name,
                # TODO get from product
                "item": invoice_line.product_id.name,
                "itemCode": invoice_line.product_id.default_code,
                "orderNumber": line_count,
                "qty": trunc(qty),
                "tax": trunc(tax_amount * amount_multiplier),
                "taxRate": str(0.18),  # TODO get tax rate from tax
                "total": trunc(gross_total * amount_multiplier),
                "unitOfMeasure": "PP",  # TODO get unit from product
                "unitPrice": trunc(unit_price_gross),
                "vatApplicableFlag": "1"
            }

            # if item has a discount

            if invoice_line.discount:
                # copy goods_detail
                # Whether the product line is discounted
                # Dictount this line
                goods_detail_discount = goods_detail.copy()
                line_count += 1
                goods_detail_discount['orderNumber'] = line_count
                goods_detail['discountFlag'] = 1
                goods_detail_discount['discountFlag'] = 0
                # goods_detail_discount['deemedFlag'] = 1
                # "item": invoice_line.product_id.name,
                goods_detail_discount['item'] = invoice_line.product_id.name + ' (Discount)'

                discount_amount = (invoice_line.discount / 100 * gross_total) * -1
                discount_net_amount = (invoice_line.discount / 100 * sub_total) * -1
                goods_detail['discountTotal'] = trunc(discount_amount)
                goods_detail_discount['total'] = trunc(discount_amount)
                discount_tax_amount = (tax_amount * (invoice_line.discount / 100)) * -1
                goods_detail_discount['tax'] = trunc(discount_tax_amount)

                goods_detail['discountTaxRate'] = trunc(invoice_line.discount / 100)
                goods_detail_discount.pop('qty')
                goods_detail_discount.pop('unitPrice')
                # goods_detail_discount.pop('total')

                goods_details.append(goods_detail)
                goods_details.append(goods_detail_discount)
            else:
                goods_details.append(goods_detail)

            #  counld be product or tax
            invoice_gross_amount += gross_total + round(discount_amount, 2)
            invoice_net_amount += sub_total + round(discount_net_amount, 2)
            invoice_tax_amount += tax_amount + round(discount_tax_amount, 2)

            taxDetails = [{
                "grossAmount": trunc(invoice_gross_amount * amount_multiplier),
                "netAmount": trunc(invoice_net_amount * amount_multiplier),
                "taxAmount": trunc(invoice_tax_amount * amount_multiplier),
                "taxCategory": "A: Standard",  # TODO get tax category from tax
                "taxCategoryCode": "01",  # TODO get tax category code from tax
                "taxRate": "0.18",  # TODO get tax rate from tax
                "taxRateName": "18%"  # TODO get tax rate name from tax
            }]
            summary = {
                "grossAmount": trunc(invoice_gross_amount * amount_multiplier),
                "itemCount": str(len(invoice_line_ids)),
                "modeCode": "1",
                "netAmount": trunc(invoice_net_amount * amount_multiplier),

                "taxAmount": trunc(invoice_tax_amount * amount_multiplier),
            }
            _logger.info("_generate_efris_invoice: invoice_line:\n%s", invoice_line)
        upload_item = {
            "sellerDetails": sellerDetails,
            "basicInformation": basicInformation,
            "buyerDetails": buyerDetails,
            "buyerExtend": buyerExtend,
            "summary": summary,
            "taxDetails": taxDetails,
            "goodsDetails": goods_details

        }
        print('==============invoice==========')
        print(upload_item)
        print('==============invoice==========')
        _logger.info("invoice_data_whole: :\n%s", upload_item)
        return upload_item

    def _generate_efris_credit_note(self, record):

        invoice_type = 2
        amount_multiplier = -1
        currenttime_str = fields.Datetime.now().strftime("%Y%d%m%H%M%S")

        basicInformation = {
            "operator": record.invoice_user_id.login,
            "invoiceKind": "1"}
        buyerDetails = {
            "buyerLegalName": record.partner_id.name,
            "buyerType": "1",
            "buyerCitizenship": "1",
            "buyerSector": "1",
            "buyerReferenceNo": record.name
        }
        if record.partner_id.vat:
            buyerDetails['buyerTin'] = record.partner_id.vat
        if record.partner_id.is_company:
            buyerDetails['buyerReferenceNo'] = record.name
            buyerDetails['buyerType'] = 0
        buyerExtend = {}
        goods_details = []
        invoice_line_ids = record.invoice_line_ids
        invoice_gross_amount = 0
        invoice_net_amount = 0
        invoice_tax_amount = 0
        for idx, invoice_line in enumerate(invoice_line_ids):
            print('invoice_line', invoice_line)
            # print(invoice_line)
            qty = invoice_line.quantity
            unit_price_net = invoice_line.price_unit
            unit_price_gross = unit_price_net * 1.18  # TODO get tax rate from tax
            sub_total = unit_price_net * qty
            gross_total = unit_price_gross * qty
            tax_amount = gross_total - sub_total
            invoice_gross_amount += gross_total
            invoice_net_amount += sub_total
            invoice_tax_amount += tax_amount

            goods_detail = {
                "merchant": "",
                "deemedFlag": "2",
                "discountFlag": "2",
                "exciseFlag": "2",
                "exciseTax": "0",
                "goodsCategoryId": "52152004",  # TODO get from product
                "goodsCategoryName": "Domestic plates",  # TODO get from product
                "item": invoice_line.product_id.name,
                "itemCode": invoice_line.product_id.x_studio_eagm_code,
                "orderNumber": idx,
                "qty": trunc(qty * amount_multiplier),
                "tax": trunc(tax_amount * amount_multiplier),
                "taxRate": str(0.18),  # TODO get tax rate from tax
                "total": trunc(gross_total * amount_multiplier),
                "unitOfMeasure": "PP",  # TODO get unit from product
                "unitPrice": trunc(unit_price_gross),
                "vatApplicableFlag": "1"
            }

            #  counld be product or tax
            goods_details.append(goods_detail)
            taxDetails = [{
                "grossAmount": trunc(invoice_gross_amount * amount_multiplier),
                "netAmount": trunc(invoice_net_amount * amount_multiplier),
                "taxAmount": trunc(invoice_tax_amount * amount_multiplier),
                "taxCategory": "A: Standard",  # TODO get tax category from tax
                "taxCategoryCode": "01",  # TODO get tax category code from tax
                "taxRate": "0.18",  # TODO get tax rate from tax
                "taxRateName": "18%"  # TODO get tax rate name from tax
            }]
            summary = {
                "grossAmount": trunc(invoice_gross_amount * amount_multiplier),
                "itemCount": str(len(invoice_line_ids)),
                "modeCode": "1",
                "netAmount": trunc(invoice_net_amount * amount_multiplier),

                "taxAmount": trunc(invoice_tax_amount * amount_multiplier),
            }
            _logger.info("_generate_efris_invoice: invoice_line:\n%s", invoice_line)

        ura_timezone = pytz.timezone('Africa/Kampala')
        current_time = datetime.datetime.now(ura_timezone)
        request_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        upload_item = {
            "oriInvoiceId": record.reversed_entry_id.l10n_ug_invoice_id,
            "oriInvoiceNo": record.reversed_entry_id.l10n_ug_invoice_number,
            "reasonCode": "102",
            "reason": "Oder Canceled",
            "applicationTime": request_time,
            "invoiceApplyCategoryCode": "101",
            "currency": "UGX",
            "source": "103",
            "sellersReferenceNo": record.name,
            "basicInformation": basicInformation,
            "buyerDetails": buyerDetails,
            "buyerExtend": buyerExtend,
            "summary": summary,
            "taxDetails": taxDetails,
            "goodsDetails": goods_details

        }
        return upload_item

    def _post(self, soft=True):
        res = super()._post(soft)
        for record in self:
            if record.country_code in ('UG', 'KE', 'US') and record.move_type in ('out_invoice', 'out_refund'):
                # self._compute_ura_invoice_qr(record)
                # if not record.l10n_ug_show_delivery_date:
                #     raise UserError(_('Delivery Date cannot be empty'))
                self.write({
                    'l10n_ug_confirmation_datetime': fields.Datetime.now()
                })
        return res
