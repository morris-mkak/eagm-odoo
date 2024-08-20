# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'


    reserved_availability = fields.Float(
            'Quantity Reserved', compute='_compute_reserved_availability',
            digits='Product Unit of Measure',
            readonly=False, help='Quantity that has already been reserved for this move')