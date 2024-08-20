# -*- coding: utf-8 -*-
from odoo import models, fields


class KEReliefType(models.Model):
    """ Kenya's types of tax relief model"""
    _name = "ke.relief.type"
    _description = "Tax Relief Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Relief', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        required=True,
        domain=[
            ('sequence',
             '>=',
             96),
            ('sequence',
             '<=',
             99),
            ('active',
             '=',
             True)],
        help="""Pick a salary rule that will be used to compute \
                this type of tax relief in the payslip""")
