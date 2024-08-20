# -*- coding: utf-8 -*-
{
    'name': 'EAGM Custom Reports',
    'version': '14.0.1.0.0',
    'summary': 'EAGM Custom Reports',
    'description': """EAGM Custom Reports""",
    'category': 'Product',
    'author': 'Dishon Kadoh',
    "website": "http://dishonkadoh.com/",
    'depends': ['base',
                'account'],
    'data': [
        'reports/account_move.xml',
        'views/account_move.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}