# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'EAGM Stock Inventory Line',
    'version' : '1.0',
    'author':'INNOVUS Group',
    'category': 'Stock',
    'maintainer': 'INNOVUS Group',
    'summary': """Update Cartons field on Stock Inventory Line.""",
    'description': """

        This module updates Cartons field on Stock Inventory Line

    """,
    'website': 'https://innovus.co.ke/',
    'license': 'LGPL-3',
    'support':'info@innovus.co.ke',
    'depends' : ['stock'],
    'data': [
       'views/stock_picking.xml',
       'views/stock_move.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,

}
