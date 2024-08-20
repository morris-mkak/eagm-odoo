# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_tz_tvfd_username = fields.Char('TVFD Username', groups="base.group_erp_manager")
    l10n_tz_tvfd_log_dir = fields.Char('Logs Dir', groups="base.group_erp_manager")
    l10n_tz_tvfd_password = fields.Char('TVFD Password', groups="base.group_erp_manager")
    l10n_tz_tvfd_serial_number = fields.Char('TVFD Serial Number', groups="base.group_erp_manager")
    l10n_tz_tvfd_business_id = fields.Char('TVFD Active Business', groups="base.group_erp_manager")
    l10n_tz_tvfd_token = fields.Text('Auth Token', groups="base.group_erp_manager")
    l10n_tz_tvfd_prod = fields.Boolean('InProd', groups="base.group_erp_manager")


