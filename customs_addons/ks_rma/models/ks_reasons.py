from odoo import models, fields, api, _


class KsReturn(models.Model):
    _name = "ks.return.reasons"
    _description = "Reasons for returning products"
    _rec_name = 'ks_return_reason'

    ks_return_reason = fields.Char(string="Reason for return")


class KsRefund(models.Model):
    _name = "ks.refund.reasons"
    _description = "Reasons for refunding products"
    _rec_name = 'ks_refund_reason'

    ks_refund_reason = fields.Char(string="Reason for refund")


class KsReplace(models.Model):
    _name = "ks.replace.reasons"
    _description = "Reasons for replacing products"
    _rec_name = 'ks_replace_reason'

    ks_replace_reason = fields.Char(string="Reason for replace")
