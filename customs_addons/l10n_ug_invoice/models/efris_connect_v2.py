import inspect
import io
import os
import pprint
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
import base64
import sys
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
# import pandas as pd

_logger = logging.getLogger(__name__)


def decode_response(response):
    encoded_data = response['data']['content']
    decoded_data = base64.b64decode(encoded_data)
    return decoded_data


def check_error(response):
    print(response['returnStateInfo'])
    return




class EfrisAPI2:
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
        self.password = sudo_company.l10n_ug_invoice_key_password.encode('utf-8')
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
        encrypted_content = (response['data']['content'])

        response = self.decrypt_data(encrypted_content())
        return response



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
            print('------------------error------------------')
            print(response)
            print('------------------error------------------')
            return response
        else:
            response_data = self.decrypt_data(response['data']['content'])
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
        print(response)
        if 'data' not in response:
            raise ValueError('No data in response')
        encrypted_content = (response['data']['content'])
        # write to file
        with open(self.log_path + '/' + interface_code + '_good_request.json', 'a') as f:
            f.write(json.dumps(response, indent=4))
            f.write('\n')
            f.close()

        return self.decrypt_data(encrypted_content)

    def query_credit_note(self, payload=None):
        self.get_symetric_key()
        interface_code = "T111"
        response = self.connect(interface_code, payload)
        encrypted_content = (response['data']['content'])

        credit_notes = self.decrypt_data(encrypted_content)
        credit_note = (credit_notes['records'][0])
        credit_note_id = credit_note['id']

        credit_note_full_details_response = self.connect('T112', {"id": credit_note_id})

        credit_note_full_details = self.decrypt_data(credit_note_full_details_response['data']['content'])

        inv_details = self.connect('T108', {"invoiceNo": credit_note_full_details['refundInvoiceNo']})
        _content = inv_details['data']['content']
        with open(self.log_path + '/' + interface_code + '_invoice_resp.txt', 'a') as f:
            f.write(json.dumps(inv_details, indent=4))
            f.write('\n')
            f.close()
        full_inv_details = self.decrypt_data(_content)
        return full_inv_details


    def query_invoice(self, payload=None):
        self.get_symetric_key()
        interface_code = "T108"
        print('-------T108-------')
        response = self.connect(interface_code, payload)
        print('-------T108-response-------')
        print(response)
        print('-------T108-response-------')
        encrypted_content = (response['data']['content'])
        with open(self.log_path + '/' + interface_code + '_invoice_resp.txt', 'a') as f:
            f.write(json.dumps(response, indent=4))
            f.write('\n')
            f.close()
        invoice_details = self.decrypt_data(encrypted_content, False)
        print(invoice_details)

    def query_invoice_by_customer(self, payload=None):
        self.get_symetric_key()
        interface_code = "T107"
        print('-------T107-------')
        response = self.connect(interface_code, payload)
        print('-------T107-response-------')
        print(response)
        print('-------T107-response-------')
        encrypted_content = (response['data']['content'])
        with open(self.log_path + '/' + interface_code + '_invoice_resp.txt', 'a') as f:
            f.write(json.dumps(response, indent=4))
            f.write('\n')
            f.close()
        invoice_details = self.decrypt_data(encrypted_content, False)
        print('-------T107-invoice_details-------')

        for record in invoice_details.get('records'):
            print('-------T107-record-------')
            print(record)
            invoiceNo = record.get('invoiceNo')
            print(invoiceNo)
            full_invoice_details = self.query_invoice({"invoiceNo": invoiceNo})
            print('-------T107-full_invoice_details-------')
            print(full_invoice_details)

    def GetDataContent(data):
        content = data.content
        decoded_content = base64.b64decode(content)

        if data.data_description.zip_code == "1":
            decompressed_stream = io.BytesIO()
            with gzip.GzipFile(fileobj=io.BytesIO(decoded_content), mode='rb') as decompression_stream:
                decompressed_stream.write(decompression_stream.read())
            decoded_content = decompressed_stream.getvalue()

        if data.data_description.encrypt_code == "2":
            decoded_content = EncryptionHelper.decrypt(decoded_content,
                                                       base64.b64decode(open(appConfig.session_aes_key).read()))

        return decoded_content.decode("utf-8")

    def query_good_quantity(self, payload):
        self.get_symetric_key()
        interface_code = "T128"
        response = self.connect(interface_code, payload)
        encrypted_content = (response['data']['content'])

        return self.decrypt_data(encrypted_content)

    def query_tax_payer(self, payload=None):
        self.get_symetric_key()
        interface_code = "T119"
        if payload is None:
            payload = {"tin": "7777777777"}
        response = self.connect(interface_code, payload)
        if response.get("returnCode") is not None:
            if response['returnCode'] != '00':
                return response

        encrypted_content = (response['data']['content'])

        decrypt_data = self.decrypt_data(encrypted_content)
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
        encrypted_content = (response['data']['content'])

        decrypted_data = self.decrypt_data(encrypted_content)

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
        encrypted_content = (response['data']['content'])

        decrypted_data = self.decrypt_data(encrypted_content)
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
        print('T131 response')
        print(response)
        # check response code

        if response['returnStateInfo']['returnCode'] != '00':
            return response['returnStateInfo']
        encrypted_content = (response['data']['content'])

        decrypted_data = self.decrypt_data(encrypted_content)
        print('T131 decrypted_data')
        print(decrypted_data)

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

        encrypted_content = (response['data']['content'])

        decrypted_data = self.decrypt_data(encrypted_content)

        return decrypted_data

    def upload_product_old(self, payload=None):
        self.get_symetric_key()

        if payload is None:
            payload = {"goodsCode": "E-COM07"}
        response = self.connect("T130", payload, False)

        encrypted_content = (response['data']['content'])

        decrypted_data = self.decrypt_data(encrypted_content)
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
            print('========inner_data')
            print(inner_data)
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
                payload
            ]
            _logger.info("encrypt_and_sign: Running command: %s", cmd)
            print(cmd)

            if cmd is not None:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
                stdout = process.stdout.decode("utf-8")
                stderr = process.stderr.decode("utf-8")
                print(stderr)
                _logger.info("encrypt_and_sign: stderr: %s", stderr)
                _logger.info("encrypt_and_sign: stdout: %s", stdout)
                signed_data = json.loads(stdout)

        return signed_data

    def load_pkcs12(self, pfx_path, password):
        with open(pfx_path, "rb") as f:
            pfx = f.read()
        return pkcs12.load_key_and_certificates(pfx, password)

    def decrypt_v2(self, data, key):
        key = key[:16]
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
    def decrypt_data(self, raw_payload,is_compressed=False):
        print('====================decrypt_data====================')
        print('========raw_payload')
        # print(raw_payload)
        decoded_aes_key = base64.b64decode(self.aes_key)
        print(decoded_aes_key)
        private_key, cert, _ = self.load_pkcs12(self.key_path, self.password)
        aes_key_bytes = private_key.decrypt(
            decoded_aes_key,
            padding.PKCS1v15()
        )
        aes_key_ = aes_key_bytes.decode('utf-8')
        # print(raw_payload)
        encrypted_data_bytes = base64.b64decode(raw_payload)

        print('========encrypted_data_bytes')
        decoded_data_ = decrypt_aes(decoded_aes_key, encrypted_data_bytes)
        print('decoded_data_')
        print(decoded_data_)

def unpad_data(padded_data):
    pad_length = padded_data[-1]
    return padded_data[:-pad_length]

def decrypt_aes_2(password, ciphertext):
    password = password[:16]
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(password), modes.CBC(iv))
    decryptor = cipher.decryptor()
    dt = decryptor.update(ciphertext) + decryptor.finalize()
    print('dt====================')
    print(dt)
    print(dt.decode('utf-8'))

def decrypt_aes(password, ciphertext):
    iv = b'\x00' * 16
    password = password[:16]
    cipher = Cipher(algorithms.AES(password), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadded_data = unpad_data(plaintext)
    print('plaintext====================')
    print(plaintext)
    print('unpadded_data====================')
    print(unpadded_data.decode('utf-32'))
    # print(unpadded_data.decode('utf-8'))
    # print('plaintext', plaintext.decode('utf-8'))

    # print('unpadded_data', unpadded_data)
    # return unpadded_data.decode('utf-8')
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
        l10n_ug_invoice_signer_path = "/Users/komu/Desktop/eagm/efris.jar"
        l10n_ug_invoice_key_path = "/Users/komu/Desktop/eagm/eagm.jks"
        l10n_ug_log_path = "/Users/komu/Desktop/eagm"
        l10n_ug_invoice_key_password = "Kampala#2022Key"
        l10n_ug_invoice_key_entity = "east africa glassware mart- test"
        l10n_ug_invoice_tin = "1000020972"
        l10n_ug_invoice_device_no = "1000020972_01"
        l10n_ug_invoice_production_env = False


    company = EfrisCompany()
    api = EfrisAPI2(company)
    api.get_symetric_key()
    payload = {
        'invoiceNo": "122782343338',
    }
    api.query_invoice(payload)


