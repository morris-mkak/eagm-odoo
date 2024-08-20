# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KeOvertime(models.Model):
    """ Overtime request model """
    _name = "ke.overtime"
    _description = "Overtime Request"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "id desc"

    def _employee_get(self):
        return self.employee_id.search(
            [('user_id', '=', self.env.user.id)], limit=1).id

    name = fields.Char(
        'Brief Title', required=True, readonly=True, states={
            'draft': [
                ('readonly', False)]}, tracking=True)
    dept_id = fields.Many2one(
        'hr.department',
        'Department',
        related='employee_id.department_id', tracking=True)
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee Name',
        tracking=True,
        default=_employee_get,
        required=True,
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
    request_date = fields.Date('Request Date', default=datetime.today(),states={
            'draft': [
                ('readonly',
                 False)]})
    dept_id = fields.Many2one(
        'hr.department',
        'Department',
        required=True,
        tracking=True,
        related='employee_id.department_id', states={
            'draft': [
                ('readonly',
                 False)]})
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
    extra_salary = fields.Many2one("extra.salary",
                                   string='Overtime Rate',
                                   states={
                                       'draft': [
                                           ('readonly',
                                            False)]},
                                   tracking=True)
    hours = fields.Float(
        'Hours',
        required=False,
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]},
        store=True,
        tracking=True)
    description = fields.Html(
        'Work Details', required=True, readonly=True, states={
            'draft': [
                ('readonly', False)]}, tracking=True)
    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        required=False,
        domain="[('employee_id','=', employee_id)]",
        readonly=True,
        states={
            'draft': [
                ('readonly',
                 False)]}, tracking=True)
    is_fixed = fields.Boolean('Fixed Amount')
    is_hourly = fields.Boolean('Hourly Rate Amount')
    start_date = fields.Datetime(string='Date From')
    end_date = fields.Datetime(string='Date To')
    hours = fields.Float('Number of Hours', readonly=True, store=True,
                         compute='_calculate_timer')
    amount = fields.Float('Total Amount', compute='_compute_totals',
                          inverse='_compute_total', store=True)

    @api.depends('extra_salary', 'hours')
    def _compute_totals(self):
        for rec in self:
            if rec.is_hourly == True:
                rec.amount = rec.hours * rec.extra_salary.name

    def _compute_total(self):
        for rec in self:
            if rec.is_hourly == True:
                print('RECORD'.format(rec.extra_salary.name))
                print('HOURS'.format(rec.hours))
                rec.amount = rec.hours * rec.extra_salary.name

    @api.depends('start_date', 'end_date')
    def _calculate_timer(self):
        if self.start_date and self.end_date:
            t1 = datetime.strptime(self.start_date, '%Y-%m-%d %H:%M:%S')
            t2 = datetime.strptime(self.end_date, '%Y-%m-%d %H:%M:%S')
            t3 = t2 - t1
            self.hours = float(t3.days) * 24 + (float(t3.seconds) / 3600)
            if self.hours < 0:
                raise ValidationError(
                    "'End Date' is older than 'Start Date' in time entry. Please correct this")

    # @api.depends('date_from', 'date_to')
    # def _total_minutes(self):
    #     if self.date_from or self.date_to:
    #         start_dt = fields.Datetime.from_string(self.date_from)
    #         finish_dt = fields.Datetime.from_string(self.date_to)
    #         difference = relativedelta(finish_dt, start_dt)
    #         hours = difference.hours or 0
    #         days = difference.days*24 or 0
    #         minui = difference.minutes/60 or 0
    #         self.hours = hours + days + minui
    #
    #         if self.hours < 0:
    #             raise ValidationError(
    #                     "'End Date' is older than 'Start Date' in time entry. Please correct this")

    def overtime_approval(self):
        """Send a request for approval"""
        for rec in self:
            if not rec.employee_id:
                raise ValidationError('Missing Employee record')
            else:
                return rec.write({'state': 'hr'})

    def hr_approved(self):
        """ Approves the overtime request """
        for rec in self:
            rec.state = 'approved'

    def overtime_disapproved(self):
        """ disapproves the overtime request """
        for record in self:
            record.state = 'rejected'

    def overtime_reset(self):
        """ Resets an overtime request currently waiting approval"""
        for record in self:
            record.state = 'draft'

