# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields
from odoo.exceptions import ValidationError


class KeSalaryAdvance(models.Model):
    """ Salary Advance request model"""
    _name = "ke.advance"
    _description = "Salary Advance Request"
    _inherit = ["mail.thread", 'mail.activity.mixin', 'portal.mixin']
    _order = "id desc"

    def _employee_get(self):
        return self.employee_id.search(
            [('user_id', '=', self.env.user.id)], limit=1).id

    name = fields.Char(
        'Request details',
        required=True,
        readonly=True,
        tracking=True,
        states={
            'draft': [
                ('readonly',
                 False)]})
    dept_id = fields.Many2one(
        'hr.department',
        'Department',
        tracking=True,
        related='employee_id.department_id', states={
            'draft': [
                ('readonly',
                 False)]})

    request_date = fields.Date('Request Date', default=datetime.today())
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        default=_employee_get,
        required=True,
        tracking=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]})
    user_id = fields.Many2one(
        'res.users',
        related='employee_id.user_id',
        tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('hr', 'HR'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')], default='draft', string='Status',
        track_visibility='onchange', )
    amount = fields.Monetary(
        'Amount',
        currency_field='currency_id',
        tracking=True, readonly=True, states={
            'draft': [
                ('readonly',
                 False)]})
    description = fields.Html(
        'Reasons for Request',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]}, tracking=True)
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        required=True,
        tracking=True,
        domain="[('employee_id','=', employee_id)]",
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]})

    currency_id = fields.Many2one(
        related='employee_id.company_id.currency_id',
        tracking=True)

    def advance_approval(self):
        """ sets the draft salary advance request to waiting approval"""
        for record in self:
            if not record.employee_id:
                raise ValidationError('Missing Employee record')
            else:
                return record.write({'state': 'hr'})

    def advance_approved(self):
        """ approves a salary fadvance request """
        for record in self:
            record.state = 'approved'

    def advance_disapproved(self):
        """ disapproves a salary advance request """
        for record in self:
            record.state = 'rejected'

    def advance_reset(self):
        """ resets a salary advance request currently waiting approval"""
        for record in self:
            record.state = 'draft'
