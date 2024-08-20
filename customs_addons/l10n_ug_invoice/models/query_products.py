import pprint

from efris_connect import EfrisAPI
import pandas as pd


class EfrisCompany:
    l10n_ug_invoice_signer_path = "/Users/komu/Desktop/eagm/efris.jar"
    l10n_ug_invoice_key_path = "/Users/komu/Desktop/eagm/eagm.jks"
    l10n_ug_invoice_key_password = "Kampala#2022Key"
    l10n_ug_invoice_key_entity = "east africa glassware mart- test"
    l10n_ug_invoice_tin = "1000020972"
    l10n_ug_invoice_device_no = "1000020972_01"
    l10n_ug_invoice_production_env = True


company = EfrisCompany()
api = EfrisAPI(company)

# import execl file
df = pd.read_excel('/Users/komu/Downloads/stock.quant.xlsx')
print(df)
columns = df.columns
print(columns)

# iterate over the rows in the dataframe skipping the first row

counter = 0
for index, row in df.iterrows():

    item_name = row['Product']
    # print(item_name)
    #  remove like [T2604]
    item_name = item_name.split('] ')[1]
    # print(item_name)
    cost = row['Product/Cost']
    code = row['Product/Internal Reference']
    ura_product = {
        'item': item_name,
        'itemCode': code,
        'goodsCategoryId': 5939030,
        'commodityCategoryId': 5939030,
        'unitPrice': cost,
    }

    response = api.upload_product(ura_product)
    print('------upload-------')
    pprint.pprint(response)
    # increase stock
    # ura_product['qty'] = row['Inventoried Quantity']
    # ura_product['merchant'] = "EAGM"
    # increase_response = api.increase_stock(ura_product)
    # if increase_response:
    # #     add to list of unssucessful
    #     with open('/Users/komu/Desktop/eagm/failed.txt', 'a') as f:
    #         f.write(str(code))
    #         f.write('\n')
    # print('------increase_response-------')
    # pprint.pprint(increase_response)

