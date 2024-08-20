# -*- coding: utf-8 -*-

from odoo import models, fields


class KEBenefitType(models.Model):
    """ Types of benefits model """
    _name = "ke.benefit.type"
    _description = "Benefit Type"
    _inherit = ["mail.thread"]
    _order = "name asc"

    name = fields.Char('Name of Benefit', required=True)
    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Payroll Rule',
        domain=[
            ('sequence',
             '<=',
             '36'),
            ('sequence',
             '>=',
             '31'),
            ('active',
             '=',
             True)],
        help='Pick a salary rule that will be used to compute this \
        type of benefit in the payslip',
        required=True)