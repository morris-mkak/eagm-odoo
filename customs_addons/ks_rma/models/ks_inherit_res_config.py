from odoo import models, fields, api, _


class KsReason(models.Model):
    _inherit = 'res.company'

    ks_policy = fields.Text(string='Return and Refund Policies')
    ks_terms = fields.Text(string='Terms and Conditions')


class KsSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ks_is_rma_portal_access = fields.Boolean(string='RMA Portal Access',
                                             config_parameter='ks_rma.is_rma_portal_access')
    ks_is_rma_approval_process_access = fields.Boolean(string='RMA Approval Process Access',
                                                       config_parameter='ks_rma.is_rma_approval_process_access')
    ks_rma_user_id = fields.Many2one('res.users', string='Default Assigned User',
                                     config_parameter='ks_rma.ks_rma_user_id')
    ks_rma_team_id = fields.Many2one('crm.team', string='Default Assigned Team',
                                     config_parameter='ks_rma.ks_rma_team_id')
    ks_warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse',
                                      config_parameter='ks_rma.ks_warehouse_id')
    ks_policy = fields.Text(string='Policies ', related='company_id.ks_policy', readonly=False)
    ks_terms = fields.Text(string='Terms and Conditions', related='company_id.ks_terms', readonly=False)
