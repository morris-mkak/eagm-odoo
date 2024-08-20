# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import csv
from datetime import datetime

from odoo import api, fields, models

from .efris_connect import EfrisAPI
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr
import logging


def trunc(num):
    return str(round(num, 2))
    sp = str(num).split('.')
    return '.'.join([sp[0], sp[1][:2]])


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_get_efris_categories(self):
        for product in self:
            print('l10n_ug_invoice_signer_path')
            print(self.env.company.sudo().l10n_ug_invoice_signer_path)

            # api = EfrisAPI((self.env.user.company_id.sudo()))
            api = EfrisAPI(self.env.company.sudo())
            response = api.get_system_dictionary()
            print('------api-response-------')
            print(response)
        return True

    def action_update_product_quantity_to_ura(self):
        for product in self:
            print('l10n_ug_invoice_signer_path')
            print(self.env.company.sudo().l10n_ug_invoice_signer_path)

            # api = EfrisAPI((self.env.user.company_id.sudo()))
            api = EfrisAPI(self.env.company.sudo())

            stock_in_efris = float(self.get_sock_in_ura(product))
            print('stock_in_efris')
            print(stock_in_efris)
            stock_in_odoo = product.qty_available
            # stock_in_efris = 0
            # stock_in_odoo = 1000
            stock_adjustment = stock_in_efris - stock_in_odoo

            if stock_adjustment == 0:
                continue
            ura_product = {
                'item': product.name,
                'itemCode': product.default_code,
                'goodsCategoryId': product.default_code,
                "goodsCategoryName": product.l10n_ug_category_name,
                'category': product.categ_id.name,
                'unitPrice': trunc(product.standard_price),
                'qty': product.qty_available,
                'merchant': ''
            }
            merchant = ''
            if product.seller_ids:
                supplier = product.seller_ids[0]
                merchant = supplier.name.name

            if not merchant:
                merchant = 'Default'
                # raise UserError('No supplier found for product %s' % product.name)

            status = self.update_stock_in_ura(ura_product, stock_in_efris, stock_in_odoo, merchant, api)
            print('-----update_stock_response-----')
            print(status)
            for prod_resp in status:
                if prod_resp['returnCode'] != '00':
                    raise UserError(prod_resp['returnMessage'])

        return True

    def update_stock_in_ura(self, ura_product, stock_in_efris, stock_in_odoo, merchant, api):
        if stock_in_efris < stock_in_odoo:
            # increate stock
            #     get the difference betwen thre etwo and update the stock
            stock_adjustment = stock_in_odoo - stock_in_efris
            ura_product['qty'] = stock_adjustment
            # get the product supplier
            ura_product['merchant'] = merchant
            print('increase stock')
            response = api.increase_stock(ura_product)

            print('increase stock response')
            print(response)
            if response:
                if response['returnCode'] != '00':
                    raise UserError(response['returnMessage'])
        else:
            # decrease stock
            print('decrease stock')
            stock_adjustment = abs(stock_in_odoo - stock_in_efris)
            ura_product['qty'] = stock_adjustment
            response = api.reduce_stock(ura_product)

        return response

    def action_zero_qty_in_ura(self):
        for product in self:
            print('l10n_ug_invoice_signer_path')
            print(self.env.company.sudo().l10n_ug_invoice_signer_path)

            # api = EfrisAPI((self.env.user.company_id.sudo()))
            api = EfrisAPI(self.env.company.sudo())

            stock_in_efris = float(self.get_sock_in_ura(product))
            ura_product = {'item': product.name, 'itemCode': product.default_code,
                           'goodsCategoryId': product.default_code, "goodsCategoryName": product.l10n_ug_category_name,
                           'category': product.categ_id.name, 'unitPrice': trunc(product.standard_price),
                           'qty': stock_in_efris, 'merchant': ''}
            response = api.reduce_stock(ura_product)

        return True

    def action_check_product_quantity_in_ura(self):
        for product in self:
            stock = self.get_sock_in_ura(product)
            product.message_post(body="Stock in Efris: %s" % stock)

        return True

    def action_swap_id_in_ura(self):
        for product in self:
            stock = self.get_sock_in_ura(product)
            product.message_post(body="Stock in Efris: %s" % stock)

        return True

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

    def _efris_synchronise_quantities(self):
        print('_efris_get_products')
        api = EfrisAPI(self.env.company.sudo())
        products = self.env['product.template'].search([
            ('default_code', 'in', self.get_ura_stock_codes()),
        ])
        for product in products:
            print('---working on product---' + product.name)
            stock_in_efris = self.get_sock_in_ura(product, fetch_efris_id=True)
            stock_in_odoo = product.qty_available
            stock_adjustment = stock_in_efris - stock_in_odoo
            ura_product = {
                'item': product.name,
                'itemCode': product.default_code,
                'goodsCategoryId': product.default_code,
                "goodsCategoryName": product.l10n_ug_category_name,
                'category': product.categ_id.name,
                'unitPrice': trunc(product.standard_price),
                'qty': product.qty_available,
                'merchant': '',
                'remarks': 'Synchonised from Odoo'
            }
            merchant = ''
            if product.seller_ids:
                supplier = product.seller_ids[0]
                merchant = supplier.name.name
            self.update_stock_in_ura(ura_product, stock_in_efris, stock_in_odoo, merchant, api)

    def _get_invoice(self):
        companies = self.env['res.company'].search([('id', '=', 3)])
        for company in companies:
    #         get  account.move where l10n_ug_invoice_number is null and is posted

            moves = self.env['account.move'].search([
                ('l10n_ug_invoice_number', '=', False),
                ('state', '=', 'posted'),
                # +/- 1 day  of posted date
                ('date', '>=', datetime.today().replace(day=1).strftime('%Y-%m-%d')),
                ('company_id', '=', company.id),
            ])
            print('======== moves ========')
            print(len(moves))

            for move in moves:
                print(move)

            print('======== moves ========')
            print(len(moves))


    def _test_efris(self):
        # get the company in country UG
        companies = self.env['res.company'].search([('id', '=', 3)])
        for company in companies:
            print('_efris_get_products')
            api = EfrisAPI(company.sudo())
            api.test()

    #         get invoice details

    def action_send_product_to_ura(self):
        print("action_send_product_to_ura")
        print(self)
        for product in self:
            print(product)

            api = EfrisAPI(self.env.company.sudo())
            unit_price_net = product.list_price
            print(unit_price_net)
            unit_price_gross = unit_price_net * 1.18
            ura_product = {
                'item': product.name,
                'itemCode': product.default_code,
                'goodsCategoryId': product.l10n_ug_invoice_category_id,
                "goodsCategoryName": product.l10n_ug_category_name,
                'category': product.categ_id.name,
                'unitPrice': trunc(unit_price_gross),
            }
            response = api.upload_product(ura_product)
            print('------goods upload-------')
            print(response)
            print('------goods upload-------')
            # if  not empty list
            if response:
                if response[0]['returnCode'] != '00':
                    raise ValidationError(_('Error: %s') % response[0]['returnMessage'])
            else:
                good_query = {"goodsCode": product.default_code}
                good_query_response = api.query_good(good_query)
                good_id = good_query_response["records"][0]['id']
                product.write({'l10n_ug_invoice_efris_id': good_id})
                product.message_post(body="URA Product ID: %s" % good_id)
        return True

    def get_ura_stock_codes(self):
        codes = ['10322/SX-123', '10770', '11037', '11047', '11874', '12063', '12148', '13426/N1106', '13735', '13840',
                 '14193', '14611', '14630', '15018', '15706', '180120', '180B000/7146', '180BC00/1146', '181B000/3046',
                 '181B000/7146', '2006AP/1006AP', '20551', '20561', '208A000/7343', '210PH00/7146', '212PH00/7144',
                 '21347/SX-132', '214PH00/7145', '215PC00/1046', '215PH00/7145', '22670', '22712', '22720',
                 '230B000/3046', '23216AE', '232B000/3046', '241P000/7046', '242P000/6146', '25269', '25285', '25873',
                 '25875', '263B000/7146', '27754', '282PG00/7345', '286PG00/7046', '28891', '295B005/7145',
                 '295B008/7145', '30629', '31320', '333S703/7044', '343P000/3046', '344B000/3046', '36341', '36E1151',
                 '36E2151', '407B000/7146', '41884', '42439', '42440', '46256', '46912', '47019', '48024', '49027',
                 '49030', '50029', '50033', '50065', '50124', '50229', '50540', '50640', '50920', '50924', '50928',
                 '51620', '51624', '51628', '52049A', '58833', '61024', '61066', '61071', '61107', '61109', '62447',
                 '62661', '62664', '62821', '62933', '62955', '62981', '63141', '63355', '63371', '63373', '63376',
                 '63377', '63379', '63391', '63558', '63573', '63585', '65', '66215H', '66220H', '66310H', '66320H',
                 '66353', '66415H', '68978', '69205', '69214', '69217', '69225', '69226', '69236', '69237', '7131',
                 '7132', '72388', '75201', '79923', '81240R', '833B000/7244', '835B000/7244', '888B000/7146', '98906',
                 'ACRG09', 'ACSP01', 'ACTS01', 'ADC33401', 'AR28BW4/7044', 'AS26HA0/6146', 'ASBR07A', 'ASBW18',
                 'ASCR15A', 'ASCS02A', 'ASCU09A', 'ASDP23A', 'ASDP26A', 'ASFP15A', 'ASFP17A', 'ASFP21A', 'ASFP24A',
                 'ASFP25', 'ASFP27A', 'ASFP29', 'ASFP31A', 'ASGB25A', 'ASMG30A', 'ASOP34A', 'ASPS01A', 'ASSA13',
                 'ASSA15A', 'ASSC23', 'ASSM36', 'ASSP27', 'ASSS01A', 'ASSU23A', 'AUOB20', 'AURPN33', 'AUSP11', 'AUSP33',
                 'BAAT03', 'BABD11', 'BABR01', 'BABR03', 'BABW12', 'BABW14', 'BACH01', 'BACP35', 'BACR05', 'BACR15',
                 'BACS01', 'BACS02D54', 'BACS30', 'BACU09', 'BACU09D54', 'BACU20D54', 'BACU23', 'BADP26', 'BADP26D54',
                 'BAEG01', 'BAFP15', 'BAFP17', 'BAFP17D54', 'BAFP20', 'BAFP24D54', 'BAFP25', 'BAFP27', 'BAFP29',
                 'BAFP30D54', 'BAFP31', 'BAFV01', 'BAGB15', 'BAMG36', 'BAMG36D20', 'BAMH01', 'BANC22', 'BANC28',
                 'BAPP32', 'BAPS01', 'BAPS01D54', 'BASA13', 'BASA13D54', 'BASA15', 'BASA15D54', 'BASB16', 'BASH01D54',
                 'BASM30', 'BASP14', 'BASS01', 'BASS01D54', 'BAST01', 'BAST01D54', 'BASU27', 'BATH01', 'BATH01D54',
                 'BATP40', 'BATPLD1', 'BUBA22', 'BUBA29', 'BUBS23', 'BUGN1.1', 'BUGN1.2', 'BUGN1.3', 'BUGN39', 'BURT41',
                 'BX14503', 'BX17128', 'BX2101', 'BX2103', 'BX2104', 'BX2105', 'BX8508', 'BX8512', 'BX8622', 'BX8623',
                 'BX8624', 'BX8625', 'BX8626', 'BX8627', 'BX8628', 'C03001', 'C06054', 'C1320', 'C1360', 'C9687',
                 'CBABOS', 'CBADEF', 'CBADEKMB', 'CBADES', 'CBADIF', 'CBADIKMB', 'CBADIS', 'CBAFIF', 'CBAFIK', 'CBAMOS',
                 'CBGDEKMB', 'CCTBOS', 'CCTBUK', 'CCTCAF', 'CCTCOS', 'CCTDEF', 'CCTDEKMB', 'CCTDES', 'CCTDIF',
                 'CCTDIKMB', 'CCTDIS', 'CCTFIK', 'CCTLES', 'CDR20201', 'CLCP35', 'CLCU09', 'CLCU23', 'CLPS01', 'CLRP33',
                 'CLRP38', 'CLSA13', 'CLSA15', 'CLSP24', 'CLSP27', 'CLSS01', 'CLTP40', 'CSLCOS', 'CSLDEF', 'CSLDEK',
                 'CSLDES', 'CSLDIK', 'D2376', 'D7361', 'DM06BU6/3046', 'DM25BA6/3046', 'DM25BL6/3046', 'DM26BS6/3046',
                 'DM26SR6/3046', 'DM32BZ6/3046', 'DM32RR6/3046', 'DM34RR6/3046', 'DM42RR6/3046', 'E5358', 'E9293',
                 'E9296', 'E9304', 'E9305', 'EAG22DK', 'FDFP16', 'FDFP25', 'FDOP36', 'FDPS01', 'G2613', 'G3322',
                 'G3367', 'G3573', 'G3666', 'G3745', 'G3749', 'G3751', 'G3871', 'G4394', 'G4395', 'G4396', 'G7864',
                 'H3672', 'H3951', 'H4124', 'H4130', 'H4132', 'H4368', 'H4531', 'H4668', 'H4703', 'H4717', 'H5564',
                 'H5591/N1308', 'H5701', 'H5702', 'H5704', 'H8918/J5388', 'H9218', 'H9984', 'HM-BA05 (12P)', 'HM-BA06',
                 'HM-BA07', 'HM-BA08', 'HM-BA101', 'HM-BA102', 'HM-BA103', 'HM-BA11', 'HM-BA119R', 'HM-BA120R',
                 'HM-BA120S', 'HM-BA121R', 'HM-BA121S', 'HM-BA122', 'HM-BA123', 'HM-BA125', 'HM-BA135', 'HM-BA136',
                 'HM-BA140', 'HM-BA-142', 'HM-BA144', 'HM-BA146', 'HM-BA147', 'HM-BA148', 'HM-BA150', 'HM-BA164',
                 'HM-BA165', 'HM-BA166', 'HM-BA167', 'HM-BA168', 'HM-BA182', 'HM-BA183', 'HM-BA184', 'HM-BA185',
                 'HM-BA186', 'HM-BA187', 'HM-BA200', 'HM-BA204', 'HM-BA205', 'HM-BA209', 'HM-BA210', 'HM-BA211',
                 'HM-BA22', 'HM-BA220', 'HM-BA221', 'HM-BA222', 'HM-BA225', 'HM-BA228', 'HM-BA23', 'HM-BA230',
                 'HM-BA232', 'HM-BA236', 'HM-BA237', 'HM-BA239', 'HM-BA24', 'HM-BA253', 'HM-BA254', 'HM-BA255',
                 'HM-BA256', 'HM-BA258', 'HM-BA259', 'HM-BA26', 'HM-BA260', 'HM-BA261', 'HM-BA262', 'HM-BA263',
                 'HM-BA264', 'HM-BA265', 'HM-BA266', 'HM-BA267', 'HM-BA268', 'HM-BA27', 'HM-BA277', 'HM-BA278',
                 'HM-BA28', 'HM-BA32', 'HM-BA33', 'HM-BA34', 'HM-BA35', 'HM-BA36', 'HM-BA38', 'HM-BA39', 'HM-BA40',
                 'HM-BA41', 'HM-BA42', 'HM-BA43', 'HM-BA44', 'HM-BA45', 'HM-BA46BR', 'HM-BA47BR', 'HM-BA47BR',
                 'HM-BA48BR', 'HM-BA49BR', 'HM-BA51C', 'HM-BA52C', 'HM-BA55', 'HM-BA56', 'HM-BA58', 'HM-BA59',
                 'HM-BA61', 'HM-BA62B', 'HM-BA62G', 'HM-BA62R', 'HM-BA62Y', 'HM-BA67', 'HM-BA69', 'HM-BA70', 'HM-BA73',
                 'HM-BA76', 'HM-BA83', 'HM-BA85B', 'HM-BA85BLU', 'HM-BA85Y', 'HM-BA86B', 'HM-BA86G', 'HM-BA98', 'J0592',
                 'J1582', 'J1583', 'J1584', 'J2601', 'J2995', 'J3000', 'J3001', 'J4161', 'J4169', 'J4170', 'J4239',
                 'J4687', 'J4724', 'J4726', 'J4728', 'J5185', 'J5387', 'J6691', 'J8488', 'J8492', 'J8535', 'K0752',
                 'K3535', 'K6022', 'K6036', 'K6302', 'K6589', 'KRAURPN33', 'L0499', 'L0529', 'L0530', 'L1323', 'L1839',
                 'L2421', 'L2427', 'L2434', 'L2437', 'L2762', 'L2785', 'L2786', 'L2968', 'L2969', 'L3204',
                 'L3218/N1522', 'L3263', 'L3696', 'L3697', 'L3751', 'L4066', 'L4604', 'L4985', 'L4986', 'L4991',
                 'L4992', 'L5304', 'L5831', 'L5939', 'L5941', 'L6689', 'L6691', 'L6755', 'L7254', 'L7255', 'L7330',
                 'L7335', 'L7339', 'L7340', 'L7351', 'L7353', 'L7354', 'L7425', 'L7426', 'L7554', 'L7610', 'L7611',
                 'L7612', 'L7613', 'L7614', 'L7790', 'L7848', 'L7849', 'L7850', 'L7956', 'L8163', 'L8230', 'L8233',
                 'L8344', 'L8531', 'L8535', 'L8805', 'L8904', 'L9816', 'L9817', 'L9818', 'L9918', 'L9942', 'L9943',
                 'L9944', 'L9947', 'L9948', 'L9950', 'M0089', 'M0091', 'M0092', 'M1812BM/KHS', 'MC25BA6/1046',
                 'MC26BS6/1046', 'MC26SR6/1046', 'MC32RR6/1046', 'MC42RR6/1046', 'MG06BU6/7146', 'MG12BU6/7146',
                 'MG20BA6/7046', 'MG20BS6/7044', 'MG26BA6/7146', 'MG26BL6/7146', 'MG26BS6/7244', 'MG27BN6/7146',
                 'MG30BN6/7046', 'MG30RR6/7046', 'MG33BV6/7146', 'MG35RR6/7046', 'MPE1216', 'MPE1600/KHS', 'MRGP30',
                 'MSSA14', 'MVP2000M', 'N0226', 'N0755', 'N0756', 'N0757', 'N0759', 'N0762', 'N0769', 'N0781', 'N0782',
                 'N0789', 'N0792', 'N0793', 'N1023', 'N1102', 'N1103', 'N1104', 'N1105', 'N1214', 'N1229', 'N1230',
                 'N1233', 'N1235', 'N1236', 'N1237', 'N1238', 'N1239', 'N1240', 'N1241', 'N1242', 'N1244', 'N1246',
                 'N1287', 'N1288', 'N1309', 'N1310', 'N1311', 'N1312', 'N1314', 'N1318', 'N1319', 'N1320', 'N1321',
                 'N1508', 'N1512', 'N1577', 'N1627', 'N1739', 'N1838', 'N1839', 'N1840', 'N2055', 'N2077', 'N2142',
                 'N2317', 'N2321', 'N2322', 'N2329', 'N2330', 'N2331', 'N2332', 'N2333', 'N2334', 'N2335', 'N2336',
                 'N2337', 'N2338', 'N2379', 'N2381', 'N2603', 'N2605', 'N2613', 'N2615', 'N3083', 'N3114', 'N3214',
                 'N3216', 'N3295', 'N3600', 'N3603', 'N3606', 'N3619', 'N3620', 'N3621', 'N3622', 'N3645', 'N3648',
                 'N3654', 'N3695', 'N4136', 'N4574', 'N4580', 'N4582', 'N4583', 'N4584', 'N4585', 'N4594', 'N4781',
                 'N4907', 'N5418', 'N5609', 'N5610', 'N5622', 'N5751', 'N5829', 'N6233', 'N6253', 'N6613', 'N6802',
                 'N6803', 'N6804', 'N6815', 'N6818', 'N6820', 'N6887', 'N6900', 'N6953', 'N7451', 'N7850', 'N8018',
                 'N8019', 'N8109', 'N8406', 'N8728', 'N9065', 'N9066', 'N9067', 'N9524', 'NBSA15', 'NFCLRP33BK',
                 'NFCLSP30BK', 'NFNNPR21BK', 'NFNNPR21TB', 'NFNNPR24CY', 'NFNNPR27BK', 'NFNNPR29TB', 'NFNNPR31BK',
                 'NFOPNB15TO', 'NNBW09', 'NP/DK', 'NP/DS', 'NP/TS', 'ONOP32A', 'ONPR18A', 'ONPR24', 'ONPR27A', 'OPSD01',
                 'OPSP14', 'P0703', 'P0704', 'P0705', 'P0786', 'P0787', 'P0789', 'P0790', 'P0867', 'P1186', 'P1286',
                 'P1669', 'P1842', 'P2019', 'P2021', 'P2611', 'P2612', 'P3200', 'P3380', 'P3546', 'P3547', 'P3548',
                 'P3549', 'P3550', 'P3551', 'P3552', 'P3978', 'P4040', 'P4082', 'P4126', 'P4127', 'P4164', 'P4246',
                 'P4250', 'P4251', 'P4396', 'P4428', 'P4467', 'P4468', 'P4469', 'P4571', 'P4573', 'P4578', 'P4579',
                 'P4580', 'P4788', 'P4789', 'P4817', 'P4818', 'P4820', 'P5247', 'P5248', 'P5279', 'P5282', 'P5401',
                 'P5404', 'P5406', 'P5409', 'P5516', 'P5517', 'P5518', 'P5519', 'P5520', 'P5522', 'P5536', 'P5597',
                 'P6016', 'P6017', 'P6019', 'P6029', 'P6033', 'P6037', 'P6039', 'P6040', 'P6103', 'P6203', 'P6550',
                 'P6552', 'P6553', 'P6554', 'P6558', 'P6728', 'P7659', 'P7669', 'P8454', 'P8457', 'P9194', 'P9391',
                 'P9542', 'P9639', 'P9918', 'P9921', 'PXCU30', 'PXCU35', 'Q0156', 'Q0433', 'Q0434', 'Q0436', 'Q0569',
                 'Q0859', 'Q0925', 'Q1579', 'Q1580', 'Q1582', 'Q1583', 'Q1584', 'Q1585', 'Q1586', 'Q1587', 'Q1588',
                 'Q1589', 'Q1590', 'Q1591', 'Q1824', 'Q1871', 'Q1872', 'Q1873', 'Q1874', 'Q2160', 'Q2161', 'Q2162',
                 'Q2163', 'Q2456', 'Q3335', 'Q3337', 'Q3338', 'Q3340', 'Q3341', 'Q3342', 'Q3343', 'Q3344', 'Q3392',
                 'Q3395', 'Q3396', 'Q3403', 'Q3650', 'Q3653', 'Q3654', 'Q3727', 'Q4817', 'Q5362', 'Q5508', 'Q5509',
                 'Q5511', 'Q5552', 'Q6531', 'Q6532', 'Q6630', 'Q8644', 'R0735', 'R0739', 'R0744', 'R0745', 'RKCU09',
                 'RKMG33', 'RKPS01', 'RKSA13', 'RKSS01', 'RP18AP4/7344', 'RP24BF4/7346', 'RP28AE4/7342', 'RP28BF4/7346',
                 'RP28BW4/7344', 'SG30RR8/7146', 'SG35RR8/7144', 'SKCPLD1', 'SKPS01', 'SKSA16', 'SKSFP19', 'SKSFP24',
                 'SKSFP27', 'SKSS01', 'SKTH01', 'SKTP40', 'SKTPLD1', 'SL/DF', 'SLSP25', 'SLSP30', 'SL/TK', 'SPRP30',
                 'SPSP27', 'SU30RR5/7246', 'SU31OR5/7246', 'SU33RR5/7244', 'T2601', 'T2602', 'T2604', 'T2612', 'T2613',
                 'T2615', 'T3001', 'T3004', 'T3005', 'T3006', 'T3008', 'T3009', 'T3010', 'T3116', 'T3126', 'T3202',
                 'T3204', 'T3205', 'T3206', 'T3208', 'T3209', 'T7531', 'T9202', 'TPX2067', 'TPX-2072', 'TPX5501',
                 'TPX5502', 'TPX5503', 'TPX5504', 'TPX5506', 'TPX5507', 'TPX5508', 'TPX6005', 'TPX6006', 'TPX6007',
                 'TPX7006', 'TPX9001', 'TPX9002', 'U09-1000', 'U1009', 'V1249', 'V1252', 'V1253', 'V1254', 'V1255',
                 'V1256', 'V1259', 'V1302', 'V1304', 'V1324', 'w36300', 'X21581', 'X23677/SX-918']
        return codes

    l10n_ug_invoice_category_id = fields.Char('EFRIS Category ID', default='52152004')
    l10n_ug_invoice_efris_id = fields.Char('EFRIS Commodity ID')
    l10n_ug_invoice_measure_unit = fields.Char('Efris Measure Unit', default="PP")
    l10n_ug_category_name = fields.Char('Efris Category Name', default="Domestic plates")


class ProductProduct(models.Model):
    _inherit = "product.product"

    l10n_ug_invoice_category_id = fields.Char('Commodity category ID', copy=False,
                                              help="Efris Category ID. ")
    l10n_ug_invoice_measure_unit = fields.Char('Measure Unit Code', copy=False,
                                               help="Efris Measure unit Code. ")
    l10n_ug_category_name = fields.Char('Category Name', copy=False,
                                        help="Efris Measure unit Code. ")
    l10n_ug_efris_id = fields.Char(string="Efris ID", )
