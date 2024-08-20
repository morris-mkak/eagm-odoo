# -*- coding: utf-8 -*-
{
    'name': "Face Attendance",

    'summary': """Using camera to check in and check out""",

    'author': "TDT",
    'website': "http://tdtrung17693.me",

    # Categories can be used to filter modules in modules listing
    # Check
    # https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],
    'qweb': [
        'static/src/xml/templates.xml'
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/actions_n_menus.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
