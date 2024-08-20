import json

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    edifact_uom_code = fields.Char("EDIFACT UOM Code")
