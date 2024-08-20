# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'EAGM Custom CSS',
    'version' : '14.0',
    'author':'INNOVUS Group',
    'category': 'sale',
    'maintainer': 'INNOVUS Group',
    'summary': """Update column width in Sale Order lines.""",
    'description': """

        This module updates Custom CSS

    """,
    'website': 'https://innovus.co.ke/',
    'license': 'LGPL-3',
    'support':'info@innovus.co.ke',
    'depends' : ['sale'],
    'data': [
        'views/custom_css.xml',
        # 'views/sale_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': -99,
}
