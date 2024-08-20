# -*- coding:utf-8 -*-
# Copyright (C) 2020 Dishon Kadoh (<mail@dishonkadoh.com>).
{
    'name': 'EAGM Sale Order Customization',
    'category': 'Sale',
    'version': '14.0.0.1',
    'summary': '''->Increase Tree View Header width
                  ->Domain Customer product using codes
    ''',
    'description': "",
    'author': 'Dishon Kadoh',
    "website": "http://dishonkadoh.com/",
    "license": "LGPL-3",
    'depends': ['base',
                'sale_management',
                'sh_product_customer_code'],
    'data': [
        'views/sale_order.xml',
        'views/template.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'insallable': True

}
