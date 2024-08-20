from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_ke_invoice_cu_zfpserver_host = fields.Char(related='company_id.l10n_ke_invoice_cu_zfpserver_host', readonly=False)
    l10n_ke_invoice_cu_zfpserver_port = fields.Char(related='company_id.l10n_ke_invoice_cu_zfpserver_port', readonly=False)
    l10n_ke_invoice_cu_device_host = fields.Char(related='company_id.l10n_ke_invoice_cu_device_host', readonly=False)
    l10n_ke_invoice_cu_device_port = fields.Char(related='company_id.l10n_ke_invoice_cu_device_port', readonly=False)
    l10n_ke_invoice_cu_device_password = fields.Char(related='company_id.l10n_ke_invoice_cu_device_password', readonly=False)
