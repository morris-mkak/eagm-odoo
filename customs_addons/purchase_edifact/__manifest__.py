# -*- coding: utf-8 -*-
{
    'name': "purchase_edifact",

    'summary': """
        Export purchase orders in EDIFACT format""",


    'description': """
        Export purchase orders in EDIFACT format. Mostly used for EDI with suppliers.
    """,

    'author': "John Komu",
    'website': "https://code.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product.xml',
        'views/purchase_views.xml',
        'views/res_partner_views.xml',
        'views/uom_uom_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
