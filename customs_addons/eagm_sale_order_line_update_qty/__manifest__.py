# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'EAGM Sale Order Line Product Qty Update',
    'version' : '1.0',
    'author':'INNOVUS Group',
    'category': 'Sales',
    'maintainer': 'INNOVUS Group',
    'summary': """Update Product quantity field on sale order line from SKUs studio field.""",
    'description': """

        This module updates product quantity field on sale order line from SKUs studio field

    """,
    'website': 'https://innovus.co.ke/',
    'license': 'LGPL-3',
    'support':'info@innovus.co.ke',
    'depends' : ['sale_management','stock'],
    'data': [
#         'partner.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,

}
