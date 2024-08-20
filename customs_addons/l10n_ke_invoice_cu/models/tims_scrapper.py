import requests
from bs4 import BeautifulSoup


class Timsscrapper:
    cu_invoice_number = None
    trader_invoice_number = None
    invoice_date = None
    total_taxable_amount = None
    total_tax_amount = None
    total_invoice_amount = None
    supplier_name = None

    def __init__(self,):
        self.url = 'https://itax.kra.go.ke/KRA-Portal/invoiceChk.htm?actionCode=loadPage&invoiceNo='

    def get_data(self, cu_invoice_number):
        full_url = self.url + cu_invoice_number
        self.page = requests.get(full_url)
        self.soup = BeautifulSoup(self.page.content, 'html.parser')

        td_no = 0
        table = self.soup.find('div', class_='templateMainDiv') \
            .find('div', class_='templateContentDiv') \
            .find('table', class_='templateContentDivTable') \
            .find('tr') \
            .find('td', class_='templateContentDivTableMainPanel') \
            .find('div', class_='templateContentDivTableMainPanelDiv') \
            .find('html') \
            .find('body') \
            .find('table', class_='whitepapartdBig')
        trs = table.find_all('tr')
        # self.data = table
        for tr in trs:
            #         check if the td has a table

            if tr.find('td').find('table'):
                inner_table = (tr.find('td').find('table'))
                inner_trs = inner_table.find_all('tr')
                for inner_tr in inner_trs:

                    tds = inner_tr.find_all('td')
                    for td in tds:
                        td_no += 1

                        if td_no == 2:
                            self.cu_invoice_number = td.text
                        if td_no == 4:
                            self.trader_invoice_number = td.text
                        if td_no == 6:
                            self.invoice_date = td.text
                        if td_no == 8:
                            self.total_taxable_amount = td.text
                        if td_no == 11:
                            self.total_tax_amount = td.text
                        if td_no == 14:
                            self.total_invoice_amount = td.text
                        if td_no == 16:
                            self.supplier_name = td.text

        self.data = {
            'cu_invoice_number': self.cu_invoice_number,
            'trader_invoice_number': self.trader_invoice_number,
            'invoice_date': self.invoice_date,
            'total_taxable_amount': self.total_taxable_amount,
            'total_tax_amount': self.total_tax_amount,
            'total_invoice_amount': self.total_invoice_amount,
            'supplier_name': self.supplier_name,
        }
        if self.cu_invoice_number:
            return self.data
        return False


if __name__ == '__main__':
    invoice_number = '0110600320000000063'
    tims = Timsscrapper()
    data = tims.get_data(invoice_number)
    print(data)
