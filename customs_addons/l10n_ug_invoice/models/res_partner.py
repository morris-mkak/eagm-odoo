# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .efris_connect import EfrisAPI
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat')
    def _onchange_vat(self):



        for partner in self:
            if partner.country_id and self.env.user.company_id.country_id.code == 'UG':
                if partner.vat and partner.country_id.code in 'UG':
                    efris_api = EfrisAPI(self.env.company.sudo())
                    # validate
                    return_data = efris_api.query_tax_payer({'tin': partner.vat})
                    if return_data.get("returnCode", '00') != "00":
                        raise UserError(
                            _('TIn validation Error.') + "\n" + return_data.get(
                                "returnMessage"))
                    else:

                        #     update customer details

                        partner.name = return_data.get('taxpayer')['legalName']


                    # raise UserError(_('You cant change Vat'))
