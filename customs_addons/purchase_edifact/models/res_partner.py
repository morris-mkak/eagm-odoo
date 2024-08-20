# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    edifact_sender_id = fields.Char(
        string='EDI Sender ID',
        help='The Sender ID of the partner. Provided by the Supplier.',
    )
    edifact_sender_name = fields.Char(
        string='EDI Sender Name',
        help='The sender identifier, assigned by the EDI service provider.',
    )
    edifact_supplier_address_id = fields.Char(
        string='EDI Supplier Address ID',
        help='The Supplier Address ID, assigned by the EDI service provider.',
    )
    edifact_buyer_address_id = fields.Char(
        string='EDI Buyer Address ID',
        help='The Buyer Address ID, assigned by the EDI service provider.',
    )