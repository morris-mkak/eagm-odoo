import inspect
import io
import os
import pprint
import re
import time
import subprocess
import zlib
import gzip
from types import SimpleNamespace

import requests
import datetime

import json
import logging
import pytz
import base64

# import pandas as pd

_logger = logging.getLogger(__name__)


def decode_response(response):
    encoded_data = response['data']['content']
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data


def check_error(response):
    print(response['returnStateInfo'])
    return


class EfrisAPI:
    aes_key = None
    signer_path = None
    key_path = None
    password = None
    entity = None
    tin = None
    device_no = None
    log_path = None
    env = None
    url = "https://efristest.ura.go.ug/efrisws/ws/taapp/getInformation"

    # create a constructor
    # def __init__(self, signer_path, key_path, password, entity, tin, device_no, env):
    def __init__(self, sudo_company):

        self.signer_path = sudo_company.l10n_ug_invoice_signer_path
        self.key_path = sudo_company.l10n_ug_invoice_key_path
        self.password = sudo_company.l10n_ug_invoice_key_password
        self.entity = sudo_company.l10n_ug_invoice_key_entity
        self.tin = sudo_company.l10n_ug_invoice_tin
        self.device_no = sudo_company.l10n_ug_invoice_device_no
        self.env = sudo_company.l10n_ug_invoice_production_env
        self.log_path = sudo_company.l10n_ug_log_path
        if not self.signer_path:
            raise Exception('Signer path not set')

        if self.env:
            self.url = "https://efrisws.ura.go.ug/ws/taapp/getInformation"
        else:
            self.url = "https://efristest.ura.go.ug/efrisws/ws/taapp/getInformation"

    # function to send invoice data to efris
    def send_invoice(self, move_item):
        # get time
        pass

    def initialise_efris(self):
        interface_code = "T102"
        response = self.connect(interface_code, None)
        if response['returnStateInfo']['returnCode'] == '00':
            keys = json.loads(decode_response(response))
            return keys
            pass
        else:
            error = response['returnStateInfo']['returnMessage']

    def check_server_key(self):
        key_file_name = 'efris_key.json'
        bother_file = self.signer_path

        # get base path for a file

        base_path = self.log_path
        # check if file exists
        if os.path.exists(base_path + '/' + key_file_name):
            with open(base_path + '/' + key_file_name, 'r') as f:
                data = f.read()
                f.close()
            if data:
                data_dict = json.loads(data)
                # check if key is expired
                expire_time = datetime.datetime.fromisoformat(data_dict['expire_time'])
                if expire_time > datetime.datetime.now():
                    self.aes_key = data_dict['passowrdDes']
                    return True
                else:
                    return False
        return False

    def get_symetric_key(self):
        if not self.check_server_key():
            interface_code = "T104"
            # save this to file
            response = self.connect(interface_code, None)
            # converts the bytecode into json
            keys = json.loads(decode_response(response))
            passowrdDes = keys.get('passowrdDes')
            self.aes_key = passowrdDes
            # dump keys to file
            # expire after 20 hours
            expire_time = datetime.datetime.now() + datetime.timedelta(hours=20)
            keys['expire_time'] = expire_time.isoformat()
            # file_name = '/'.join(self.signer_path.split('/')[:-1]) + '/efris_key.json'

            file_name = self.log_path + '/efris_key.json'
            with open(file_name, 'w') as f:
                f.write(json.dumps(keys))
                f.close()

            return passowrdDes
        else:
            print('Key already exists')

    def login(self):
        interface_code = "T103"
        response = self.connect(interface_code, None)

        response_content = response['data']['content']

        d1 = base64.b64decode(response_content).decode('utf-8')

        # keys = json.loads(decode_response(response))

    def test(self):
        interface_code = "T101"
        response = self.connect(interface_code, None)
        print(response)

    def get_system_dictionary(self):
        self.get_symetric_key()
        interface_code = "T115"
        response = self.connect(interface_code, None)
        return self.decrypt_data(response)

    def sych_products(self, invoice=None):
        for good in invoice['goodsDetails']:
            self.upload_product(good)
            self.increase_stock(good)

    def upload_invoice(self, payload=None, sync_products=False, op_type='invoice'):
        self.get_symetric_key()
        if op_type in 'invoice':
            interface_code = "T109"
        else:
            interface_code = "T110"
        # sych products before
        if sync_products:
            self.sych_products(payload)

        response = self.connect(interface_code, payload)
        with open(self.log_path + '/' + interface_code + '_invoice_request.json', 'a') as f:
            f.write(json.dumps(payload, indent=4))
            f.write('\n')
            f.close()

        if response.get("returnCode") is not None:
            return response
        else:
            response_data = self.decrypt_data(response)
            # response_data.update({'returnCode': response['returnCode']})
            # save to file
            with open(self.log_path + '/' + interface_code + '_invoice_response.json', 'a') as f:
                f.write(json.dumps(response_data, indent=4))
                f.write('\n')
                f.close()
            return response_data

    # TODO: Good Stock Maintain T131: Update stock after issuance of invoice
    # TODO: Query Tax Payer Information BY TIN T119
    # TODO: Void Credit Note/ Debit Note T120
    # TODO: Credit Note/ Debit Note Application T110

    def query_good(self, payload=None):
        self.get_symetric_key()
        interface_code = "T127"
        response = self.connect(interface_code, payload)

        if 'data' not in response:
            raise ValueError('No data in response')

        return self.decrypt_data(response)

    def query_credit_note(self, payload=None):
        self.get_symetric_key()
        interface_code = "T111"
        response = self.connect(interface_code, payload)
        credit_notes = self.decrypt_data(response)
        credit_note = (credit_notes['records'][0])
        credit_note_id = credit_note['id']

        credit_note_full_details_response = self.connect('T112', {"id": credit_note_id})

        credit_note_full_details = self.decrypt_data(credit_note_full_details_response)

        inv_details = self.connect('T108', {"invoiceNo": credit_note_full_details['refundInvoiceNo']})
        _content = inv_details['data']['content']
        with open(self.log_path + '/' + interface_code + '_invoice_resp.txt', 'a') as f:
            f.write(json.dumps(inv_details, indent=4))
            f.write('\n')
            f.close()
        full_inv_details = self.decrypt_data(inv_details)
        return full_inv_details

    def query_invoice_by_ref(self, invoice_id=None):
        self.get_symetric_key()
        # replace special characters with space
        invoice_id = re.sub('[^A-Za-z0-9]+', ' ', invoice_id)
        payload = {"referenceNo": invoice_id}
        interface_code = "T106"
        response = self.connect(interface_code, payload)
        if 'data' not in response:
            return None
        invoice_details = self.decrypt_data(response)

        if len(invoice_details.get('records')) == 0:
            return None

        efris_invoice_id = invoice_details.get('records')[0].get('id')

        payload = {"id": efris_invoice_id}
        full_invoice_response = self.decrypt_data(self.connect('T108', payload))
        return full_invoice_response


    def query_good_quantity(self, payload):
        self.get_symetric_key()
        interface_code = "T128"
        response = self.connect(interface_code, payload)
        return self.decrypt_data(response)

    def query_tax_payer(self, payload=None):
        self.get_symetric_key()
        interface_code = "T119"
        if payload is None:
            payload = {"tin": "7777777777"}
        response = self.connect(interface_code, payload)
        if response.get("returnCode") is not None:
            if response['returnCode'] != '00':
                return response

        decrypt_data = self.decrypt_data(response)
        decrypt_data['returnCode'] = '00'
        return decrypt_data

    def upload_product(self, payload=None):
        # TODO check first then upload if not exist else modify
        self.get_symetric_key()

        efris_details = self.query_good({'goodsCode': payload['itemCode']})
        good = {
            "goodsName": payload['item'],
            "goodsCode": payload['itemCode'],
            "measureUnit": 'PP',
            "unitPrice": payload['unitPrice'],
            "currency": "101",
            "commodityCategoryId": payload['goodsCategoryId'],
            "haveExciseTax": "102",
            "description": "1",
            "stockPrewarning": "10",
            "goodsTypeCode": "101",
            "haveOtherUnit": "102",
            "havePieceUnit": "102",
            "operationType": "102",

        }
        if len(efris_details['records']) > 0:
            good['operationType'] = '102'
            # return efris_details
        else:
            good['operationType'] = '101'

        goods = [good]

        response = self.connect("T130", goods, False)

        decrypted_data = self.decrypt_data(response)

        return decrypted_data

    def update_good_code(self, payload=None):
        self.get_symetric_key()
        efris_details = self.query_good({'goodsCode': payload['itemCode']})
        good = {
            "operationType": "102",
            "goodsCode": payload['newGoodsCode'],

        }
        goods = [good]

        response = self.connect("T130", goods, False)

        decrypted_data = self.decrypt_data(response)
        return decrypted_data

    def increase_stock(self, payload=None, new_product=False):

        self.get_symetric_key()
        remarks = ""
        if "remarks" in payload:
            remarks = payload['remarks']
        stock = {
            "goodsStockIn": {
                "operationType": "101",
                "supplierName": payload['merchant'],
                "remarks": remarks,
                "stockInType": "101",
                "adjustType": "",
                "isCheckBatchNo": "0",
                "rollBackIfError": "0",
                "goodsTypeCode": "101"
            },
            "goodsStockInItem": [{
                "goodsCode": payload['itemCode'],
                "quantity": abs(payload['qty']),  # number to increase by
                "unitPrice": payload['unitPrice'],
                "remarks": remarks,
                "lossQuantity": "0",
                # "originalQuantity": payload['qty']
            }]
        }
        # check if merchant key exists

        response = self.connect("T131", stock, False)

        if response['returnStateInfo']['returnCode'] != '00':
            return response['returnStateInfo']

        decrypted_data = self.decrypt_data(response)


        return decrypted_data

    def reduce_stock(self, payload=None, new_product=False):
        operation_type = '102'
        stock_in_type = ""
        self.get_symetric_key()
        adjustment_type = "104"
        if "remarks" in payload:
            remarks = payload['remarks']
        else:
            remarks = "104"

        stock = {
            "goodsStockIn": {
                "operationType": operation_type,
                "supplierName": payload['merchant'],
                "remarks": remarks,
                "stockInType": stock_in_type,
                "adjustType": adjustment_type,
                "isCheckBatchNo": "0",
                "rollBackIfError": "0",
                "goodsTypeCode": "101"
            },
            "goodsStockInItem": [{
                "goodsCode": payload['itemCode'],
                "quantity": abs(payload['qty']),  # number of items to reduce by
                "unitPrice": payload['unitPrice'],
                "remarks": remarks,
                "lossQuantity": "0",
                # "originalQuantity": payload['qty']
            }]
        }
        # check if merchant key exists

        response = self.connect("T131", stock, False)

        decrypted_data = self.decrypt_data(response)

        return decrypted_data

    def upload_product_old(self, payload=None):
        self.get_symetric_key()

        if payload is None:
            payload = {"goodsCode": "E-COM07"}
        response = self.connect("T130", payload, False)

        decrypted_data = self.decrypt_data(response)
        if len(decrypted_data) == 0:
            #     success the query to get ids
            efris_details = self.query_good({'goodsCode': payload[0]['goodsCode']})
            good_id = efris_details['records'][0]['id']
            return {
                "returnCode": "00",
                "returnMessage": "Success",
                'id': good_id
            }

        return decrypted_data[0]

    def connect(self, interface_code, payloadData, return_error=True):
        # get current time in EAT   (Eastern Africa Time)
        ura_timezone = pytz.timezone('Africa/Kampala')
        current_time = datetime.datetime.now(ura_timezone)
        request_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        inner_data = {
            "content": "",
            "signature": "",
            "dataDescription": {
                "codeType": "1",
                "encryptCode": "2",
                "zipCode": "0"
            }
        }
        if payloadData is not None:
            json_data = json.dumps(payloadData)
            signed_data = self.encrypt_and_sign(json_data)
            inner_data["signature"] = signed_data['signedcontent']
            inner_data["content"] = signed_data['encryptedcontent']
        datadict = {
            "data": inner_data,
            "globalInfo": {
                "appId": "AP01",
                "version": "1.1.20191201",
                "dataExchangeId": "9230489223014123",
                "interfaceCode": interface_code,
                "requestCode": "TP",
                "requestTime": request_time,
                "responseCode": "TA",
                "userName": "admin",
                "deviceMAC": "FFFFFFFFFFFF",
                "deviceNo": "1000020972_01",  # TODO: change this to the device number
                "tin": "1000020972",  # todo change this to the tin number
                "brn": "",
                "taxpayerID": "1",
                "longitude": "116.397128",
                "latitude": "39.916527",
                "extendField": {
                    "responseDateFormat": "dd/MM/yyyy",
                    "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
                    "referenceNo": "23PL015815444"
                }
            },
            "returnStateInfo": {
                "returnCode": "",
                "returnMessage": ""
            }
        }
        payload = json.dumps(datadict)
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", self.url, headers=headers, data=payload, verify=False)
        _logger.info("_efris_connect: Raw Request:\n%s", payload)
        _logger.info("_efris_connect: Received Raw Response:\n%s", response)

        parsed = json.loads(response.text)
        if return_error:
            _logger.info("_efris_connect: Parsed Response:\n%s", parsed)
            if parsed.get("returnStateInfo") is not None:
                return_state_info = parsed.get("returnStateInfo")
                if return_state_info.get("returnCode") != "00":
                    return parsed.get("returnStateInfo")

            data = decode_response(parsed)

            # _logger.info("_efris_connect: Decoded response:\n%s", data)

        return parsed

        #

    def encrypt_and_sign(self, payload):
        #     run java -jar efris.jar script to encrypt and sign the payload
        # cmd = ["java", "-jar", "/Users/komu/projects/efris/out/artifacts/efris_jar/efris.jar"]
        signed_data = {
            "signedcontent": "",
            "encryptedcontent": ""
        }
        if payload is not None:
            cmd = [
                "java",
                "-jar",
                self.signer_path,
                self.key_path,
                self.password,
                self.entity,
                self.aes_key,
                "sign",
                "0",
                payload
            ]

            if cmd is not None:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
                stdout = process.stdout.decode("utf-8")
                stderr = process.stderr.decode("utf-8")
                print(stderr)
                _logger.info("encrypt_and_sign: stderr: %s", stderr)
                _logger.info("encrypt_and_sign: stdout: %s", stdout)
                signed_data = json.loads(stdout)

        return signed_data

    def decrypt_v2(self, data, key):
        import base64
        import os
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        data = base64.b64decode(data)
        # key = key.encode('utf-8')

        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(data) + decryptor.finalize()
        return decrypted_data.decode('utf-8')

    # decrypt
    def decrypt_data(self, server_response):
        """
        Decrypts the payload given the response from the server
        """

        raw_payload = server_response['data']['content']
        decompress_str = server_response['data']['dataDescription']['zipCode']

        # get the calling function name
        calling = inspect.stack()[1][3]

        #     run java -jar efris.jar script to encrypt and sign the payload
        # decompress_str = "1" if is_compressed else "0"
        cmd = [
            "java",
            "-jar",
            self.signer_path,  # file to be called not part of aruments
            self.key_path,  # 0 java positional arument
            self.password,  # 1
            self.entity,  # 2
            self.aes_key,  # 3
            "decrypt",  # 4
            decompress_str,  # 5
            raw_payload  # 6
        ]
        # signed_data = subprocess.call()
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        stdout = process.stdout.decode("utf-8")
        stderr = process.stderr.decode("utf-8")

        print(stdout)
        with open(self.log_path + '/decrypted_data.json', 'a') as f:
            f.write(stdout)
            f.write('\n')
            f.close()
        if len(stdout) > 0:
            # check if json
            try:
                json_data = json.loads(stdout)
                return json_data
            except ValueError:
                return []
            # return json.loads(stdout)
        if len(stderr) > 0:

            with open(self.log_path + '/stderr.txt', 'a') as f:
                f.write(stderr)
                f.write('\n')
                f.close()
        return {'records': []}


# run the script
if __name__ == "__main__":
    # self.signer_path = sudo_company.l10n_ug_invoice_signer_path
    # self.key_path = sudo_company.l10n_ug_invoice_key_path
    # self.password = sudo_company.l10n_ug_invoice_key_password.strip()
    # self.entity = sudo_company.l10n_ug_invoice_key_entity
    # self.tin = sudo_company.l10n_ug_invoice_tin
    # self.device_no = sudo_company.l10n_ug_invoice_device_no
    # self.env = sudo_company.l10n_ug_invoice_production_env
    class EfrisCompany:
        l10n_ug_invoice_signer_path = "/Users/komu/projects/odoo/efris3/out/artifacts/efris3_jar/efris3.jar"
        l10n_ug_invoice_key_path = "/Users/komu/Desktop/eagm/eagm.jks"
        l10n_ug_log_path = "/Users/komu/Desktop/eagm"
        l10n_ug_invoice_key_password = "Kampala#2022Key"
        l10n_ug_invoice_key_entity = "east africa glassware mart- test"
        l10n_ug_invoice_tin = "1000020972"
        l10n_ug_invoice_device_no = "1000020972_01"
        l10n_ug_invoice_production_env = True


    company = EfrisCompany()
    api = EfrisAPI(company)
    api.get_symetric_key()
    response = api.query_invoice_by_ref('INV 2022 12 0127')
