import requests
from bs4 import BeautifulSoup

from .FP import FP, Enums
import re


# from FP import FP, Enums


def tims_format(sting):
    # check if string type
    if isinstance(sting, str):
        if sting != '':
            return re.sub('[^A-Za-z0-9]+', '', sting)[:30]
    return sting


class TimsAPI:
    fp = None
    zfp_server_host = None
    zfp_server_port = None
    cu_host = None
    cu_port = None
    cu_password = None

    def __init__(self, sudo_company):

        self.zfp_server_host = sudo_company.l10n_ke_invoice_cu_zfpserver_host
        self.zfp_server_port = sudo_company.l10n_ke_invoice_cu_zfpserver_port
        self.cu_host = sudo_company.l10n_ke_invoice_cu_device_host
        self.cu_port = sudo_company.l10n_ke_invoice_cu_device_port
        self.cu_password = sudo_company.l10n_ke_invoice_cu_device_password
        print("TimsAPI settings")
        print("zfp_server_host:", self.zfp_server_host)
        print("zfp_server_port:", self.zfp_server_port)
        print("cu_host:", self.cu_host)
        print("cu_port:", self.cu_port)
        print("cu_password:", self.cu_password)
        self.init(self.zfp_server_host, int(self.zfp_server_port), self.cu_host, int(self.cu_port), self.cu_password)

    def init(self, server_url, port, device_ip, device_port, device_password, print_status=False):
        # STEP 1: INITIALIZE
        self.fp = FP()
        self.fp.serverSetSettings(server_url, port)  # TODO: use the passed url
        # STEP 2: SETTINGS
        self.fp.serverSetDeviceTcpSettings(device_ip, device_port, device_password)
        # cancel_response = self.fp.CancelReceipt()
        # print(cancel_response)
        # STEP 3: READ STATUS
        read_status_response = self.fp.ReadStatus()
        if print_status:
            print("---------------------------------------read_status_response----------------------------------")
            print("Power_down_in_opened_fiscal_receipt:", read_status_response.Power_down_in_opened_fiscal_receipt)
            print("DateTime_not_set:", read_status_response.DateTime_not_set)
            print("DateTime_wrong:", read_status_response.DateTime_wrong)
            print("RAM_reset:", read_status_response.RAM_reset)
            print("Hardware_clock_error:", read_status_response.Hardware_clock_error)
            print("Opened_Fiscal_Receipt:", read_status_response.Opened_Fiscal_Receipt)
            print("Reports_registers_Overflow:", read_status_response.Reports_registers_Overflow)
            print("Receipt_Invoice_Type:", read_status_response.Receipt_Invoice_Type)
            print("SD_card_near_full:", read_status_response.SD_card_near_full)
            print("SD_card_full:", read_status_response.SD_card_full)
            print("CU_fiscalized:", read_status_response.CU_fiscalized)
            print("CU_produced:", read_status_response.CU_produced)
            print("Paired_with_TIMS:", read_status_response.Paired_with_TIMS)
            print("Unsent_receipts:", read_status_response.Unsent_receipts)
            print("No_Sec_IC:", read_status_response.No_Sec_IC)
            print("No_certificates:", read_status_response.No_certificates)
            print("Service_jumper:", read_status_response.Service_jumper)
            print("Missing_SD_card:", read_status_response.Missing_SD_card)
            print("Wrong_SD_card:", read_status_response.Wrong_SD_card)
            print("---------------------------------------read_status_response-----------------------------------")

    def upload_invoice(self, invoice):
        read_status_response = self.fp.ReadStatus()
        if read_status_response.Opened_Fiscal_Receipt:
            error = True
            return {
                'kra_invoice_number': False,
                'kra_invoice_qr': False,
                'kra_invoice_date': False,
                'cu_serial_number': False,
                'cu_pin_number': False,
                'message': "There is an open Invoice. Try again latter",
            }
        else:

            # STEP 4: OPENRECEIPT/ OPENDEBITNOTEINVOICE / OPENCREDITNOTEINVOICE/ OPENINVOICE
            # truncate to first 30 chars
            # invoice_number = invoice.number[:30]
            print("---------------------------------------upload_invoice----------------------------------")
            print(invoice)
            CompanyName = tims_format(invoice.get('company_name'))[:30]
            ClientPINnum = tims_format(invoice.get('vat_no'))[:14]
            HeadQuarters = tims_format(invoice.get('address'))[:30]
            Address = tims_format(invoice.get('address'))[:30]
            PostalCodeAndCity = tims_format(invoice.get('postal_code'))[:30]
            ExemptionNum = 0
            TraderSystemInvNum = tims_format(invoice.get('invoice_number'))
            print("TraderSystemInvNum:", TraderSystemInvNum)

            invoice_type = invoice.get('doc_type')
            if invoice.get('doc_type') == 'credit_note':

                original_invoice_number = tims_format(invoice.get('original_invoice_number'))
            #
            if invoice_type == 'invoice':
                open_invoice_response = self.fp.OpenInvoiceWithFreeCustomerData(CompanyName, ClientPINnum, HeadQuarters,
                                                                                Address,
                                                                                PostalCodeAndCity, ExemptionNum,
                                                                                TraderSystemInvNum)
            elif invoice_type == 'credit_note':
                open_invoice_response = self.fp.OpenCreditNoteWithFreeCustomerData(CompanyName, ClientPINnum,
                                                                                   HeadQuarters, Address,
                                                                                   PostalCodeAndCity, ExemptionNum,
                                                                                   original_invoice_number,
                                                                                   TraderSystemInvNum)
            # open_invoice_response = self.fp.OpenReceipt(1,2)
            print(
                "---------------------------------------open_invoice_response------------------------------------------")
            print(open_invoice_response)
            print(
                "---------------------------------------open_invoice_response----------------------------------------")
            for item in invoice.get('line_items'):
                print(tims_format(item.get('item_name')),
                                         Enums.OptionVATClass.VAT_Class_A, item.get('unitPrice'),
                                         tims_format(item.get('measurement_unit')), "", "", item.get('tax_rate'),
                                         item.get('item_quantity'))
                self.fp.SellPLUfromExtDB(tims_format(item.get('item_name')),
                                         Enums.OptionVATClass.VAT_Class_A, item.get('unitPrice'),
                                         tims_format(item.get('measurement_unit')), "", "", item.get('tax_rate'),
                                         item.get('item_quantity'),
                                         item.get('discount')
                                         )
            # STEP 6: READ VAT
            current_receipt_info = self.fp.ReadCurrentReceiptInfo()

            print(
                "---------------------------------------current_receipt_info----------------------------------------")
            print(current_receipt_info)
            print("---------------------------------current_receipt_info------------------------------------------")

            # STEP 7: CLOSE RECEIPT
            close_receipt_response = self.fp.CloseReceipt()

            print("---------------------------------close_receipt_response------------------------------------------")
            print(close_receipt_response)
            kra_invoice_number = close_receipt_response.InvoiceNum
            kra_invoice_qr = close_receipt_response.QRcode
            print(kra_invoice_number)
            print(kra_invoice_qr)
            print(
                "---------------------------------------close_receipt_response--------------------------------------------------")

            # STEP 8: READ DATE & TIME
            read_time_response = self.fp.ReadDateTime()

            print(
                "------------------------------------read_time_response--------------------------------------------")

            print(read_time_response)
            print("----------------------------------read_time_response---------------------------------------------")
            # STEP 9: CLOSESERVERCONNECTION

            close_device_response = self.fp.serverCloseDeviceConnection()
            print(
                "---------------------------------------read_time_response--------------------------------------------")
            print(close_device_response)
            print(
                "-------------------------------------read_time_response-------------------------------------------")
            cu_numbers = self.fp.ReadCUnumbers()
            return {
                'kra_invoice_number': kra_invoice_number,
                'kra_invoice_qr': kra_invoice_qr,
                'kra_invoice_date': read_time_response,
                'cu_serial_number': cu_numbers.SerialNumber,
                'cu_pin_number': cu_numbers.PINnumber,
            }

    def get_kra_details(self, invoice):
#        scrape_kra_details(invoice)
        url = 'https://itax.kra.go.ke/KRA-Portal/invoiceChk.htm?actionCode=loadPage&invoiceNo=0110600320000000001'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)

        return {
            'kra_invoice_number': invoice.get('kra_invoice_number'),
        }




#  if is main file then run the code
if __name__ == '__main__':
    print(tims_format('2022/IN08898'))
    invoice = {'vat_no': 'P000618409X', 'legalName': 'East Africa Glassware Mart Ltd',
               'company_name': 'East Africa Glassware Mart Ltd', 'address': 'Mombasa', 'mobilePhone': '0722209723',
               'linePhone': '0722209723', 'emailAddress': 'info@eagm.com', 'address_line_1': 'Nyerere Avenue',
               'address_line_2': 'Tea House, 2nd Floor', 'postal_code': '00100', 'invoice_number': '2022/IN08898',
               'line_items': [
                   {'item_name': '[/KHS] Bonzer Professional Can Opener', 'item_quantity': '1.0', 'tax': '0.32',
                    'tax_rate': '16.00', 'vat_class': 'A', 'item_price': '2.32', 'measurement_unit': 'PP',
                    'unitPrice': '2.32', 'vatApplicableFlag': '1'}]}
    tims_api = TimsAPI()
    # tims_api.init("41.57.100.37", 4444, "192.168.10.63", "8000", "Password", True)
    # tims_api.init("192.168.5.88", 4444, "196.207.27.42", "8000", "Password", True)
    response = tims_api.get_kra_details(invoice)
    print(response)
# python odoo/odoo-bin -c odoo.conf -u l10n_ke_invoice_cu
