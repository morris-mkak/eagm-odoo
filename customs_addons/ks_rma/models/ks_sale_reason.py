from odoo import models, fields, api, _


class KsSaleInherit(models.Model):
    _inherit = 'sale.order'

    def get_data_return(self):
        res = self.env['ks.return.reasons'].search([])
        return res

    def get_data_refund(self):
        res = self.env['ks.refund.reasons'].search([])
        return res

    def get_data_replace(self):
        res = self.env['ks.replace.reasons'].search([])
        return res


