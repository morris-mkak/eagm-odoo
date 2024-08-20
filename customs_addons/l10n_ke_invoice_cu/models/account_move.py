# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import json
import base64
import io
import json
import re
from datetime import datetime

import pyqrcode as pyqrcode

from .tims_connect import TimsAPI
from .tims_scrapper import Timsscrapper
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    l10n_tz_tvfd_verification_link = fields.Char(string='TZ link', readonly=True, copy=False)
    l10n_ke_cu_invoice_number = fields.Char(string='KRA Invoice Number', readonly=True, copy=False)
    l10n_ke_cu_qr_code_str = fields.Char(string='QR Code', readonly=True, copy=False)
    l10n_ke_json = fields.Char(string='SEND TIMS JSON', readonly=True, copy=False)
    l10n_ke_response_json = fields.Char(string='RESPONSE TIMS JSON', readonly=True, copy=False)
    l10n_ke_cu_confirmation_datetime = fields.Datetime(string='Confirmation Time', readonly=True, copy=False)
    l10n_ke_cu_serial_number = fields.Char(string='CU Serial Number', readonly=True, copy=False)
    l10n_ke_cu_pin_number = fields.Char(string='CU PIN Number', readonly=True, copy=False)
    l10n_ke_cu_sys_datetime = fields.Datetime(string='CU System Time', readonly=True, copy=False)

    def _l10n_ke_fmt(self, string, length, ljust=True):
        """ Function for common formatting behaviour

        :param string: string to be formatted/encoded
        :param length: integer length to justify (if enabled), and then truncate the string to
        :param ljust:  boolean representing whether the string should be justified
        :returns:      string justified/truncated, with all non-alphanumeric characters removed
        """
        if not string:
            string = ''
        cleaned_string = re.sub('[^A-Za-z0-9 ]+', '', str(string))
        justified_string = cleaned_string.ljust(length if ljust else 0)
        return justified_string[:length]

    def _l10n_ke_cu_lines_messages(self):
        """ Serialise the data of each line on the invoice

        This function transforms the lines in order to handle the differences
        between the KRA expected data and the lines in odoo.

        If a discount line (as a negative line) has been added to the invoice
        lines, find a suitable line/lines to distribute the discount accross

        :returns: List of dictionaries representing each command <CMD> and the
                  <DATA> of the line, which will be sent to the fiscal device
                  in order to add a line to the opened invoice.
        """

        def is_discount_line(line):
            return line.price_unit < 0.0

        def is_candidate(discount_line, other_line):
            """ If the of one line match those of the discount line, the discount can be distributed accross that line """
            discount_taxes = discount_line.tax_ids.flatten_taxes_hierarchy()
            other_line_taxes = other_line.tax_ids.flatten_taxes_hierarchy()
            return set(discount_taxes.ids) == set(other_line_taxes.ids)

        for line in self.invoice_line_ids:
            print('line')
            print(line.display_type)

        lines = self.invoice_line_ids.filtered(lambda l: l.quantity and l.price_total)
        # The device expects all monetary values in Kenyan Shillings
        if self.currency_id == self.company_id.currency_id:
            currency_rate = 1
        else:
            currency_rate = abs(lines[0].balance / lines[0].price_subtotal)

        discount_dict = {line.id: line.discount for line in lines if line.price_total > 0}
        for line in lines:
            print('---checking line---')
            print(line)
            if not is_discount_line(line):
                print('---not discount line---', line.name)
                continue
            # Search for non-discount lines
            candidate_vals_list = [l for l in lines if not is_discount_line(l) and is_candidate(l, line)]
            candidate_vals_list = sorted(candidate_vals_list, key=lambda x: x.price_unit * x.quantity, reverse=True)
            line_to_discount = abs(line.price_unit * line.quantity)
            for candidate in candidate_vals_list:
                still_to_discount = abs(
                    candidate.price_unit * candidate.quantity * (100.0 - discount_dict[candidate.id]) / 100.0)
                if line_to_discount >= still_to_discount:
                    discount_dict[candidate.id] = 100.0
                    line_to_discount -= still_to_discount
                else:
                    rest_to_discount = abs((line_to_discount / (candidate.price_unit * candidate.quantity)) * 100.0)
                    discount_dict[candidate.id] += rest_to_discount
                    break

        vat_class = {16.0: 'A', 8.0: 'B'}
        msgs = []
        for line in self.invoice_line_ids.filtered(
                lambda l: l.quantity and l.price_total > 0 and not discount_dict.get(
                    l.id) >= 100):
            # Here we use the original discount of the line, since it the distributed discount has not been applied in the price_total
            price = round(line.price_total / line.quantity * 100 / (100 - line.discount), 2) * currency_rate
            print('---tax_ids---')
            print(line.tax_ids)
            if line.tax_ids:
                percentage = line.tax_ids[0].amount
            else:
                percentage = 0.0

            # Letter to classify tax, 0% taxes are handled conditionally, as the tax can be zero-rated or exempt
            letter = ''
            if percentage in vat_class:
                letter = vat_class[percentage]
            else:
                if line.tax_ids:
                    report_line_ids = line.tax_ids.invoice_repartition_line_ids.tag_ids._get_related_tax_report_expressions().report_line_id
                    if report_line_ids:
                        # "Zero Rated Supplies" and "Zero Rated Purchases" tax line
                        if 'zero' in report_line_ids[0].name.lower():
                            letter = 'Z'
                        else:
                            letter = 'E'
            # Append the line to the message list
            uom = line.product_uom_id and line.product_uom_id.name or ''
            discount_amount = discount_dict.get(line.id) or 0.0
            msgs.append({
                'item_name': line.name[:40] if line.name else '',  # Description
                'item_price': str(price),  # Price
                # 'measurement_unit': self._l10n_ke_fmt(uom, 3),  # Price
                'measurement_unit': 'PP',  # Price
                'item_quantity': round(line.quantity, 3),  # Quantity
                'discount': str(discount_amount),  # Discount
                'vat_class': letter,  # Tax classification
                'tax_rate': str(percentage),  # Tax classification
                "unitPrice": str(round(line.price_total / line.quantity, 2)),
                "tax": str(round(line.price_total - line.price_subtotal, 2)),

            })
        print('---msgs---')
        print(msgs)
        return msgs

    def _compute_kra_invoice_qr(self, move):

        # tims_data = api.mock_upload()
        invoice_data = self._generate_tims_invoice(move)
        # json dump to file
        # with open('invoice_data.json', 'w') as outfile:
        #     json.dump(invoice_data, outfile, indent=4)

        api = TimsAPI(move.company_id.sudo())

        return_data = api.upload_invoice(invoice_data)
        print('---return_data---')
        print(return_data)
        if not return_data.get("kra_invoice_number", False):
            raise UserError(
                _('Could not upload Invoice to tims. Got error.') + "\n" + return_data.get(
                    "message"))
        # save this by appending to file kra.json

        c = pyqrcode.create(return_data['kra_invoice_qr'])
        s = io.BytesIO()
        c.png(s, scale=6)
        qr_code = base64.b64encode(s.getvalue()).decode("ascii")
        self.write({
            'l10n_ke_cu_invoice_number': return_data['kra_invoice_number'],
            'l10n_ke_cu_confirmation_datetime': return_data['kra_invoice_date'],
            'l10n_ke_cu_qr_code_str': qr_code,
            'l10n_ke_cu_serial_number': return_data['cu_serial_number'],
            'l10n_ke_cu_pin_number': return_data['cu_pin_number']
        })
        # get oddo base path

        # with open('kra.json', 'a') as f:
        #     # add a new line
        #     f.write('\n')
        #     data_to_save = return_data
        #     data_to_save['kra_invoice_date'] = str(return_data['kra_invoice_date'])
        #     f.write(json.dumps(data_to_save, indent=4, default=str))
        move.message_post(body=_("cu_invoice_number: %s") % return_data['kra_invoice_number'])

    def _generate_tims_invoice(self, record):

        invoice_line_ids = record.invoice_line_ids

        goods_details = self._l10n_ke_cu_lines_messages()
        invoice_details = {
            "vat_no": record.company_id.vat,
            "legalName": record.company_id.display_name,
            "company_name": record.company_id.name,
            "address": record.company_id.partner_id.city,
            "mobilePhone": record.company_id.phone,
            "linePhone": record.company_id.phone,
            "emailAddress": record.company_id.email,
            "address_line_1": record.company_id.partner_id.street,
            "address_line_2": record.company_id.partner_id.street2,
            "postal_code": "00100",
            "doc_type": "invoice",
            "invoice_number": record.name,
            "line_items": goods_details,

        }
        # if credit note
        if record.move_type == 'out_refund':
            invoice_details['doc_type'] = 'credit_note'
            invoice_details['original_invoice_number'] = record.reversed_entry_id.l10n_ke_cu_invoice_number

        print('----invoice_details--')
        print(invoice_details)
        print('----invoice_details--')
        return invoice_details

    def l10n_ke_action_get_json(self):
        for record in self:
            invoice_data = self._generate_tims_invoice(record)
            record.l10n_ke_json = json.dumps(invoice_data, indent=4, default=str)
            record.write({'l10n_ke_json': json.dumps(invoice_data, indent=4, default=str)})

    def l10n_ke_action_post_send_invoices(self):

        #  just do it here
        ivoice_data = self._compute_kra_invoice_qr(self)

    def _check_tims_amounts(self):
        api = Timsscrapper()
        print('---_check_tims_amounts---')
        # search for incoices with tims data
        invoices = self.env['account.move'].search([('l10n_ke_cu_invoice_number', '!=', False)])
        # file name as time
        file_name = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'tims_data.csv'

        with open(file_name, 'a') as f:
            #     add headers
            f.write('cu_invoice_number,trader_invoice,invoice_no,invoice_date,invoice_amount,tax_amount,'
                    'pre_tax_amount,kra_total_amount'
                    ',kra_tax_amount,kra_total_taxable_amount')

        checked_invoices = []

        for invoice in invoices:

            cu_invoice_number = invoice.l10n_ke_cu_invoice_number
            if cu_invoice_number not in checked_invoices:
                checked_invoices.append(cu_invoice_number)
                # kra_data ={'cu_invoice_number': '0110600320000000063', 'trader_invoice_number': '2022IN13386', 'invoice_date': '02/11/2022', 'total_taxable_amount': '297216', 'total_tax_amount': '47554', 'total_invoice_amount': '344770', 'supplier_name': 'EAST AFRICA GLASSWARE MART LIMITED'}
                kra_data = api.get_data(cu_invoice_number)
                invoice_amount = invoice.amount_total
                tax_amount = invoice.amount_tax
                pretax_amount = invoice.amount_untaxed
                print(pretax_amount)
                # save in csv file
                if kra_data:
                    with open(file_name, 'a') as f:
                        # add a new line
                        f.write('\n')
                        f.write(
                            str(cu_invoice_number) + ',' + kra_data['trader_invoice_number'] + ',' + kra_data[
                                'invoice_date'] + ','
                            + invoice.name
                            + ',' + str(invoice_amount) + ',' + str(tax_amount) + ',' + str(pretax_amount)
                            + ',' + kra_data['total_invoice_amount'] + ','
                            + kra_data['total_tax_amount'] + ',' + kra_data['total_taxable_amount']

                        )

            print(cu_invoice_number)
        # check amounts
        # check vat
        # check total
        pass

    def _post(self, soft=True):
        res = super()._post(soft)
        for record in self:
            if record.country_code in 'KE' and record.move_type in ('out_invoice', 'out_refund'):
                self.write({
                    'l10n_ke_cu_sys_datetime': fields.Datetime.now()
                })

        return res
