from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_tz_tvfd_username = fields.Char(related='company_id.l10n_tz_tvfd_username', readonly=False)
    l10n_tz_tvfd_log_dir = fields.Char(related='company_id.l10n_tz_tvfd_log_dir', readonly=False)
    l10n_tz_tvfd_password = fields.Char(related='company_id.l10n_tz_tvfd_password', readonly=False)
    l10n_tz_tvfd_serial_number = fields.Char(related='company_id.l10n_tz_tvfd_serial_number', readonly=False)
    l10n_tz_tvfd_business_id = fields.Char(related='company_id.l10n_tz_tvfd_business_id', readonly=False)
    l10n_tz_tvfd_prod = fields.Boolean(related='company_id.l10n_tz_tvfd_prod', readonly=False)
    l10n_tz_tvfd_token = fields.Text(related='company_id.l10n_tz_tvfd_token', readonly=False)

