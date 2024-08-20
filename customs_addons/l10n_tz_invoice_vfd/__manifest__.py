# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tanzania VFD Invoice',
    'version': '1.0.1',
    'author': 'John Komu',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'description': """
    Invoices for the Republic of Tanzania, Using the Total VFD, introduces send to TRA button
""",
    'depends': ['account'],

    'data': [
        'views/view_move_form.xml',
        # 'views/report_invoice_eagm_tz.xml',
        'views/res_config_settings_view.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
    ],
}
