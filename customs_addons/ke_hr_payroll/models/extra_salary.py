# -*- coding: utf-8 -*-

from odoo import models, fields


class ExtraSalary(models.Model):
    _name = "extra.salary"
    _description = "Extra Salary"

    name = fields.Float("Extra Salary")
