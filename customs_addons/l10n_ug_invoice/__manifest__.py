# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'UG - Invoice',
    'version': '1.0.0',
    'author': 'Innovus',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'description': """
    Invoices for the Republic of uganda
""",
    'depends': ['account',
                'stock_landed_costs',
                'sale_management',
                'sale_stock',
                'purchase',
                'stock'

                ],
    'data': [
        'views/view_move_form.xml',
        #'views/report_invoice.xml',
        'views/account_move_view.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_view.xml',
        'views/stock_landed_cost_views.xml',
        'views/stock.view_picking_form_views.xml',
        'views/stock.picking_types_form_views.xml',
        'views/stock.view_inventory_form.xml',
        'data/ir_cron_data.xml',


    ],
    'qweb': [
          'static/src/xml/product_buttons.xml',
    ],
    'assets': {
       'web.assets_backend': [
           'l10n_ug_invoice/static/src/js/tree_button.js',
       ],
       'web.assets_qweb': [
           'l10n_ug_invoice/static/src/xml/product_buttons.xml',
       ],
    },
}
