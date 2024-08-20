# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ke_invoice_cu_zfpserver_host = fields.Char('ZFPServer Host', groups="base.group_erp_manager")
    l10n_ke_invoice_cu_zfpserver_port = fields.Char('ZFPServer Port', groups="base.group_erp_manager")
    l10n_ke_invoice_cu_device_host = fields.Char('Device Host', groups="base.group_erp_manager")
    l10n_ke_invoice_cu_device_port = fields.Char('Device TCP Port', groups="base.group_erp_manager")
    l10n_ke_invoice_cu_device_password = fields.Char('Device TCP Password', groups="base.group_erp_manager")

