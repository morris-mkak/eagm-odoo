# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_restricted = fields.Boolean(string="Restrict Price List", help="Restrict Price List for users")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        is_restricted = params.get_param('eagm_custom_addons.is_restricted')
        res.update(is_restricted=is_restricted,
                   )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "eagm_custom_addons.is_restricted",
            self.is_restricted)


class ResUsers(models.Model):
    _inherit = 'res.users'

    pricelist_ids = fields.Many2many('product.pricelist', 'rel_user_pricelist', string="Price Lists")
    is_restricted = fields.Boolean(string="Restricted", compute="_compute_is_pricelist_restricted")

    def _compute_is_pricelist_restricted(self):
        params = self.env['ir.config_parameter'].sudo()
        pricelist_restricted = params.get_param('eagm_custom_addons.is_restricted')

        for rec in self:
            rec.is_restricted = True if pricelist_restricted else False
