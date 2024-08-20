# -*- coding: utf-8 -*-
from odoo import models, fields


class KERelationType(models.Model):
    _name = "ke.relation.type"
    _description = "Relation Type"
    _order = "name asc"
    _inherit = ["mail.thread"]

    name = fields.Char('Name')
    medical = fields.Boolean('Medical Beneficiary?', default=False)