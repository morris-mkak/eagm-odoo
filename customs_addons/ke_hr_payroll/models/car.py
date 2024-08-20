# -*- coding: utf-8 -*-

from odoo import models, fields


class KECarBenefit(models.Model):
    """ Car benefits model"""
    _name = "ke.cars"
    _description = "Car Benefit"
    _inherit = ["mail.thread"]

    name = fields.Char('Car Registration Number:', required=True)
    make = fields.Char('Make', required=True)
    body = fields.Selection(
        [
            ('saloon',
             'Saloon Hatch Backs and Estates'),
            ('pickup',
             'Pick Ups,Panel Vans Uncovered'),
            ('cruiser',
             'Land Rovers/Cruisers(excluding Range Rover and similar cars)')],
        required=True,
        default='saloon',
        string="Body Type:")
    cc_rate = fields.Integer('CC Rating:', required=True)
    cost_type = fields.Selection([('Owned',
                                   'Owned'),
                                  ('Hired',
                                   'Hired')],
                                 required=True,
                                 string="Type of Car Cost:",
                                 default='Owned')
    cost_hire = fields.Float('Cost of Hire:', dp=(32, 2))
    cost_own = fields.Float('Cost of Owned Car:', dp=(32, 2))
    contract_id = fields.Many2one('hr.contract', 'Contract')
