from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_ug_invoice_signer_path = fields.Char(related='company_id.l10n_ug_invoice_signer_path', readonly=False)
    l10n_ug_log_path = fields.Char(related='company_id.l10n_ug_log_path', readonly=False)
    l10n_ug_invoice_key_path = fields.Char(related='company_id.l10n_ug_invoice_key_path', readonly=False)
    l10n_ug_invoice_key_password = fields.Char(related='company_id.l10n_ug_invoice_key_password', readonly=False)
    l10n_ug_invoice_key_entity = fields.Char(related='company_id.l10n_ug_invoice_key_entity', readonly=False)
    l10n_ug_invoice_tin = fields.Char(related='company_id.l10n_ug_invoice_tin', readonly=False)
    l10n_ug_invoice_device_no = fields.Char(related='company_id.l10n_ug_invoice_device_no', readonly=False)



    l10n_ug_invoice_production_env = fields.Boolean(related='company_id.l10n_ug_invoice_production_env', readonly=False)
    l10n_ug_invoice_invoicing_threshold = fields.Float(related='company_id.l10n_ug_invoice_invoicing_threshold', readonly=False)
