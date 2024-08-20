# -*- coding: utf-8 -*-
{
	'name': 'RMA (Return Merchandise Authorization)',

	'summary': """
RMA is a part of the process of returning a product to receive a refund, replacement, or return during the 
        products warranty period.
""",

	'description': """
Expedite the process of merchandise replace/return process and faster resolution of refund process with the 
       RMA app of Ksolves.
        
        Odoo RMA,
        Odoo RMA module,
        odoo rma process,
        RMA odoo apps,
        Odoo RMA App,
        Return Merchandise Authorization in Odoo,
        return merchandise authorization process,
        return merchandise authorization software,
        rma module,
        module rma,
        odoo rma module,
        openerp rma module
""",

	'author': 'Ksolves India Ltd.',

	'license': 'OPL-1',

	'website': 'https://www.ksolves.com',

	'maintainer': 'Ksolves India Ltd.',

	'version': '14.0.1.0.1',

	'support': 'sales@ksolves.com',

	'currency': 'EUR',

	'live_test_url': 'https://rma14.kappso.com/web/demo_login',

	'price': '49',

	'category': 'Tools',

	'depends': ['crm', 'stock', 'sale_management', 'account', 'purchase', 'sale_stock', 'base', 'web'],

	'images': ['static/description/list_screenshot.gif'],

	'data': ['security/ir.model.access.csv', 'security/ks_rma_security_groups.xml', 'report/ks_report.xml', 'report/ks_report_rma.xml', 'data/ks_rma_sequence.xml', 'data/ks_rma_email_template.xml', 'report/ks_rma_report_views.xml', 'views/ks_res_config_settings_views.xml', 'views/ks_stock.xml', 'views/ks_rma_views.xml', 'views/ks_rma_menus.xml', 'views/ks_rma_portal.xml', 'views/ks_sale_order_rma.xml', 'views/ks_rma_reasons.xml', 'views/ks_assets.xml'],

	'installable': True,

	'auto_install': False,
}
