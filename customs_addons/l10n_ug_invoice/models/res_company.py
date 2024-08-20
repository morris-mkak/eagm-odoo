# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ug_invoice_signer_path = fields.Char('Java Signer Path', groups="base.group_erp_manager")
    l10n_ug_invoice_key_path = fields.Char('JKS Path', groups="base.group_erp_manager")
    l10n_ug_log_path = fields.Char('Log Path', groups="base.group_erp_manager")
    l10n_ug_invoice_key_password = fields.Char('JKS Password', groups="base.group_erp_manager")
    l10n_ug_invoice_key_entity = fields.Char('Entity Name', groups="base.group_erp_manager")
    l10n_ug_invoice_tin = fields.Char('TIN', groups="base.group_erp_manager")
    l10n_ug_invoice_device_no = fields.Char('Device No', groups="base.group_erp_manager")
    l10n_ug_invoice_production_env = fields.Boolean('In Production Environment')

    l10n_ug_invoice_invoicing_threshold = fields.Float('Invoicing Threshold', default=0.0,
                                                       help="Threshold at which you are required to give the VAT "
                                                            "number "
                                                            "of the customer. ")
