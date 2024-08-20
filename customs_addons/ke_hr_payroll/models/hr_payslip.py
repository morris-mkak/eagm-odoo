# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslip(models.Model):
    """ inherits payslip rules model to add more """
    _inherit = 'hr.payslip'

    details_by_salary_rule_category = fields.One2many('hr.payslip.line',
                                                      compute='_compute_details_by_salary_rule_category',
                                                      string='Details by Salary Rule Category')
    basic_wage = fields.Monetary(compute='_compute_basic_net')
    net_wage = fields.Monetary(compute='_compute_basic_net')

    def _compute_details_by_salary_rule_category(self):
        for payslip in self:
            payslip.details_by_salary_rule_category = payslip.mapped(
                'line_ids').filtered(lambda line: line.category_id)

    def _compute_basic_net(self):
        for payslip in self:
            payslip.basic_wage = payslip._get_salary_line_total('P010')
            payslip.net_wage = payslip._get_salary_line_total('P120')

    def compute_overtime(self, employee_id, date_from, date_to):
        amount = 0
        overtime_rec = self.env['ke.overtime'].search(
            [('employee_id', '=', employee_id),
             ('request_date', '>=', date_from),
             ('request_date', '<=', date_to),
             ('state', '=', 'approved')])
        if overtime_rec:
            amount = sum(overtime_rec.mapped('amount'))
        return amount

    def compute_advance(self, employee_id, date_from, date_to):
        amount = 0
        advance_rec = self.env['ke.advance'].search(
            [('employee_id', '=', employee_id),
             ('request_date', '>=', date_from),
             ('request_date', '<=', date_to),
             ('state', '=', 'approved')])
        if advance_rec:
            amount = sum(advance_rec.mapped('amount'))
        return amount

    def compute_loan(self, employee_id, date_from, date_to):
        amount = 0
        loan = self.env['hr.loan'].search(
            [('employee_id', '=', employee_id),
             ('state', '=', 'approved')])
        for line in loan.loan_lines:
            if line.date >= date_from and line.date <= date_to:
                amount = sum(line.mapped('amount'))
        return amount

    def action_payslip_done(self):
        employee_id = self.employee_id.id
        date_from = self.date_from
        date_to = self.date_to
        loan = self.env['hr.loan'].search(
            [('employee_id', '=', employee_id),
             ('state', '=', 'approved')])
        for line in loan.loan_lines:
            if line.date >= date_from and line.date <= date_to:
                line.paid = True
                line.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
