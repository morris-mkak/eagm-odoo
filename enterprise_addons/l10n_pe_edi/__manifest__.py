# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'EDI for Peru',
    'version': '0.1',
    'summary': 'Electronic Invoicing for Peru (OSE method) and UBL 2.1',
    'category': 'Localization',
    'author': 'Vauxoo',
    'license': 'OEEL-1',
'description': """
EDI Peru Localization
======================
Allow the user to generate the EDI document for Peruvian invoicing.

By default, the system uses the IAP proxy.  This has the advantage that you
can use the system immediately the moment you choose Digiflow as your OSE
in the SUNAT portal.

You can also directly send it to Digiflow if you bought an account from them
and even to SUNAT in case of contingency.

We support sending and cancelling of customer invoices.
    """,
    'depends': [
        'iap',
        'l10n_pe',
        'l10n_latam_invoice_document',
        'product_unspsc',
        'account_debit_note',
        'account_edi_extended',
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/l10n_latam_document_type_data.xml',
        'data/2.1/edi_common.xml',
        'data/2.1/edi_signature.xml',
        'data/2.1/edi_invoice.xml',
        'data/2.1/edi_refund.xml',
        'data/2.1/edi_debit_note.xml',
        'data/2.1/edi_void_documents.xml',
        'data/uom_data.xml',
        'data/account_tax_data.xml',
        'data/ir_sequence_data.xml',
        'data/res_bank.xml',
        'wizards/account_invoice_refund_views.xml',
        'wizards/account_debit_note_views.xml',
        'wizards/account_cancel_wizard_views.xml',
        'views/res_company_views.xml',
        'views/uom_uom_views.xml',
        'views/account_move_views.xml',
        'views/account_tax_views.xml',
        'views/l10n_pe_edi_certificate_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_invoice.xml',
        'views/account_menuitem.xml',
        'views/product_views.xml',
        'data/ir_cron.xml',
        'data/account_edi_data.xml',
    ],
    'demo': [
        'demo/l10n_pe_edi_demo.xml',
        'demo/product_product_demo.xml',
    ],
    'external_dependencies': {
        'python': ['pyOpenSSL']
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
}
