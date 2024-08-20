import base64
import json

from .efris_connect import EfrisAPI
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_repr
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.template'
    l10n_ug_efris_id = fields.Char(string="Efris ID")
    l10n_ug_category_id = fields.Char(string="URA Category ID")
    l10n_ug_category_name = fields.Char(string="URA Category Name")
    l10n_ug_unit_of_measure = fields.Char(string="URA Unit Of Measure")
