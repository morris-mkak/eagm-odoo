# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search(
            [('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.interest_amount - total_paid
            loan.total_amount = loan.interest_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today(),
                       readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  required=True)
    department_id = fields.Many2one('hr.department',
                                    related="employee_id.department_id",
                                    readonly=True,
                                    string="Department")
    installment = fields.Integer(string="No Of Installments", default=1)
    rate = fields.Float(string="Interest Rate(%)", required=True)
    payment_date = fields.Date(string="Payment Start Date", required=True,
                               default=fields.Date.today())
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line",
                                 index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True,
                                  default=lambda
                                      self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id",
                                   readonly=True, string="Job Position")
    loan_amount = fields.Float(string="Loan Amount", required=True)
    interest_amount = fields.Float(string="Payable Amount", required=False,
                                   store=True,
                                   compute='_compute_payable_amount')

    @api.depends('rate', 'loan_amount')
    def _compute_payable_amount(self):
        for rec in self:
            if rec.rate and rec.loan_amount:
                payable_amount = ((rec.rate + 100) / 100) * rec.loan_amount
                rec.interest_amount = payable_amount

    total_amount = fields.Float(string="Total Amount", readonly=True,
                                store=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", store=True,
                                  compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True,
                                     compute='_compute_loan_amount')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('hr', 'HR'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')], default='draft', string='Status',
        track_visibility='onchange', )

    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count(
            [('employee_id', '=', values['employee_id']),
             ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        if loan_count:
            raise UserError(
                _('The employee has already a pending installment.'))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res

    def loan_approval(self):
        for rec in self:
            if rec.loan_amount <= 0:
                raise UserError('Amount requested cannot be less than 0')
            elif rec.rate <= 0:
                raise UserError('Interest Rate cannot be less than 0')
            else:
                rec.state = 'hr'

    def loan_disapproved(self):
        """ disapproves the loan request """
        for record in self:
            record.state = 'rejected'

    def loan_reset(self):
        """ Resets an loan request currently waiting approval"""
        for record in self:
            record.state = 'draft'

    def loan_approved(self):
        for data in self:
            contract_obj = self.env['hr.contract'].search(
                [('employee_id', '=', data.employee_id.id),
                 ('state', '=', 'open')], limit=1)
            if not contract_obj:
                raise UserError(_('You must Define a contract for employee.'))
            if not data.loan_lines:
                raise UserError(_('Please Compute installment.'))
            else:
                self.write({'state': 'approved'})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'rejected'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.interest_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
        return True


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"
    _rec_name = "loan_id"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
