# -*- coding: utf-8 -*-
# Part of Aktiv Software
# See LICENSE file for full copyright & licensing details.
# Author: Aktiv Software PVT. LTD.
# mail:   odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
#           Aktiv Software:
#              - Kinjal Lalani
#              - Surabh Yadav
#              - Tanvi Gajera

{
    'name': "Sale Order Excel Report",
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'summary': """Print sale excel report SO action""",
    'description': """This module will print excel report of sale.""",
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '14.0.1.0.0',
    'depends': [
        'sale_management',
    ],
    'data': [
        'report/menu_sale_xlsx.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
