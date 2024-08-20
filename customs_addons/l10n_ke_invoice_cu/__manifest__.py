# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Kenya TIMS Invoice',
    'version': '1.0.0',
    'author': 'John Komu',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'description': """
    Invoices for the Republic of kenya, Using the Tremol G03 CU
""",
    'depends': ['account'],
    'data': [
        'views/view_move_form.xml',
        # 'views/report_invoice.xml',
        'views/report_invoice_eagm-ke.xml',
        'views/res_config_settings_view.xml',
        'data/ir_cron_data.xml',
    ],
}
