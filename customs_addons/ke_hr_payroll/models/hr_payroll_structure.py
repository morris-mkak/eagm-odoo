# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    _description = 'Salary Structure'


    @api.model
    def _get_default_rule_ids(self):
        return [
            (0, 0, {
                'name': _('Basic Pay'),
                'sequence': 10,
                'code': 'P010',
                'category_id': self.env.ref('ke_hr_payroll.ke_category2').id,
                'condition_select': 'python',
                'condition_python': 'result = categories.C001',
                'amount_select': 'code',
                'amount_python_compute': 'result = categories.C001',
            }),
            (0, 0, {
                'name': _('Gross Pay'),
                'sequence': 30,
                'code': 'P030',
                'category_id': self.env.ref('ke_hr_payroll.ke_category6').id,
                'condition_select': 'python',
                'condition_python': 'result = categories.C005',
                'amount_select': 'code',
                'amount_python_compute': 'result = categories.C005',
            }),
            (0, 0, {
                'name': _('Net Pay'),
                'sequence': 120,
                'code': 'P120',
                'category_id': self.env.ref('ke_hr_payroll.ke_category35').id,
                'condition_select': 'python',
                'condition_python': 'result = categories.C034',
                'amount_select': 'code',
                'amount_python_compute': 'result = categories.C034',
            })
        ]

    rule_ids = fields.One2many(
        'hr.salary.rule', 'struct_id',
        string='Salary Rules', default=_get_default_rule_ids)
