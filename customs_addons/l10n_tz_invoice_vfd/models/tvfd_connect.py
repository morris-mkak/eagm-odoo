import re
import requests
import json


# from FP import FP, Enums


class TvfdAPI:
    username = None
    password = None
    url = 'https://testapi.totalvfd.co.tz/sales'  # todo check if live and switch url
    business_id = None
    log_dir = None

    def __init__(self, sudo_company):

        self.username = sudo_company.l10n_tz_tvfd_username
        self.token = sudo_company.l10n_tz_tvfd_token
        self.password = sudo_company.l10n_tz_tvfd_password
        self.business_id = sudo_company.l10n_tz_tvfd_business_id
        self.log_dir = sudo_company.l10n_tz_tvfd_log_dir

        if sudo_company.l10n_tz_tvfd_prod:
            self.url = 'http://live.totalvfd.co.tz/sales'
            # self.url = 'https://api.totalvfd.co.tz/sales'
        else:
            self.url = 'https://testapi.totalvfd.co.tz/sales'

    def upload_invoice(self, invoice, invoice_number, id_type, id_number):
        if not id_number:
            id_number = ''
        file_prefix = invoice_number + '_' + id_type + '_' + id_number + '_'
        file_prefix = file_prefix.replace(' ', '')

        payload = json.dumps(invoice)
        headers = {
            'Content-Type': 'application/json',
            "Authorization": "Bearer " + self.token,
            'x-active-business': self.business_id
        }
        print('vat classes')
        print(self.get_tax_classes(invoice))

        response = requests.request("POST", self.url, headers=headers, data=payload)

        self.log_json(invoice, file_prefix + 'request.json')
        self.log_json(response.text, file_prefix + 'response.json')

        if response.status_code == 201:
            # append to csv file
            tra_data_raw = (json.loads(response.text))
            verification_code = tra_data_raw.get('rctvnum')
            verification_link = tra_data_raw.get('verificationLink')

        return response.status_code, response.text

    def log_json(self, data, file_name):
        if self.log_dir:
            path = self.log_dir + '/' + file_name
            with open(path, 'w') as outfile:
                json.dump(data, outfile, indent=4)

    def get_tax_classes(self, payload):

        items = payload['items']
        vat_groups = ''
        for item in items:
            vat_groups += item['vatGroup'] + ':'
        return vat_groups
