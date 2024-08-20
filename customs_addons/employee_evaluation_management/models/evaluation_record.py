# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import calendar
import math
from datetime import date, timedelta, datetime
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import float_to_time


def float_time_convert(float_val):
    """convert float to float_time so visible in front end."""
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    hours = factor * int(math.floor(val))
    minutes = round((val % 1) * 60)
    return ("%s H: %s M" % (str(hours).zfill(2), str(minutes).zfill(2)))


class EvaluationRecord(models.Model):
    _name = "evaluation.record"
    _inherit = ['mail.thread']
    _description = "Evaluation Record"
    _order = "id desc"

    def _default_get_start_date(self):
        prev = date.today().replace(day=1) - timedelta(days=1)
        prev = prev.replace(day=1)
        return prev

    def _default_get_end_date(self):
        prev = date.today().replace(day=1) - timedelta(days=1)
        return prev

    def name_get(self):
        res = []
        for rec in self:
            start = rec.start_date.strftime('%Y/%m/%d')
            end = rec.end_date.strftime('%Y/%m/%d')
            res.append((rec.id, "Evaluation report of %s (%s-%s)" % (rec.user_id.name, start, end)))
        return res

    @api.depends('user_id')
    def get_employee_id(self):
        for obj in self:
            if obj.sudo().user_id.employee_ids:
                obj.employee_id = obj.sudo().user_id.employee_ids[0].id
            else:
                obj.employee_id = False

    def _get_is_manager(self):
        for obj in self:
            if obj.department_id.sudo().manager_id.user_id == self.env.user or obj.manager.id == self._uid:
                obj.is_manager = True
            else:
                obj.is_manager = False

    def _create_summary(self, task_hrs_dict, total_task_hrs, task_undefined):
        message = "<table border='1' width='100%'>\
              <tr>\
               <th style='text-align: center;'>Total Task Hours</th>\
               <th style='text-align: center;'>" + float_time_convert(
            total_task_hrs or 0.0) + "</th>\
              </tr>"

        if task_hrs_dict:
            for key, value in task_hrs_dict.items():
                message += "<tr>\
               <td style='text-align: center;'>" + key + "</td>\
               <td style='text-align: center;'>" + float_time_convert(
                    value or 0.0) + "</td>\
              </tr>"

        if task_undefined:
            message += "<tr>\
               <td style='text-align: center;'> Undefined</td>\
               <td style='text-align: center;'>" + float_time_convert(
                task_undefined or 0.0) + "</td>\
              </tr>"

        message += "</table><br/>"
        return message

    @api.depends('user_id', 'start_date', 'end_date')
    def _get_work_summary(self):
        for obj in self:
            task_hrs_dict = {}
            total_task_hrs = 0.0
            lines = self.env['account.analytic.line'].search([
                ('date', '>=', obj.start_date), ('date', '<=', obj.end_date),
                ('task_id', '!=', False), ('user_id', '=', obj.user_id.id)
            ])
            for line in lines:
                total_task_hrs += line.unit_amount
                if line.task_id.work_type_id and line.task_id.work_type_id.name in task_hrs_dict:
                    task_hrs_dict[line.task_id.work_type_id.name] += line.unit_amount
                else:
                    if not line.task_id.work_type_id and 'Undefined' in task_hrs_dict:
                        task_hrs_dict['Undefined'] += line.unit_amount
                    elif  not line.task_id.work_type_id:
                        task_hrs_dict['Undefined'] = line.unit_amount
                    else:
                        task_hrs_dict[line.task_id.work_type_id.name] = line.unit_amount
            task_undefined = task_hrs_dict.pop('Undefined') if task_hrs_dict.get('Undefined') else False
            message = obj._create_summary(task_hrs_dict, total_task_hrs, task_undefined)
            obj.work_summary = message

    @api.depends('start_date', 'end_date', 'total_leaves')
    def _get_total_days(self):
        for obj in self:
            if obj.start_date and obj.end_date:
                no_of_days = (obj.end_date - obj.start_date).days
                obj.total_days = no_of_days + 1
            else:
                obj.total_days = 0

    @api.depends('user_id', 'start_date', 'end_date')
    def _get_total_leaves(self):
        for obj in self:
            start_date, end_date = obj.start_date, obj.end_date
            holiday_list = self.env['hr.leave'].search([
                ('date_from', '<=', end_date), ('date_to', '>=', start_date),
                ('state', '=', 'validate'),
                ('employee_id', '=', obj.user_id.sudo().employee_ids.ids[0])
            ])
            leave_count = 0
            if holiday_list:
                h1 = holiday_list[0]
                start_date = timezone(h1.tz).localize(datetime.combine(
                    start_date, float_to_time(8.0))).astimezone(UTC).replace(tzinfo=None)
                end_date = timezone(h1.tz).localize(datetime.combine(
                    end_date, float_to_time(17.0))).astimezone(UTC).replace(tzinfo=None)
                for holiday in holiday_list:
                    if holiday.date_from < start_date and holiday.date_to > end_date:
                        leave_count += holiday._get_number_of_days(
                            start_date, end_date, obj.user_id.sudo().employee_ids.ids[0])['days']
                    elif holiday.date_from < start_date:
                        leave_count += holiday._get_number_of_days(
                            start_date, holiday.date_to, obj.user_id.sudo().employee_ids.ids[0])['days']
                    elif holiday.date_to > end_date:
                        leave_count += holiday._get_number_of_days(
                            holiday.date_from, end_date, obj.user_id.sudo().employee_ids.ids[0])['days']
                    else:
                        leave_count += holiday._get_number_of_days(
                            holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
            obj.total_leaves = leave_count

    @api.depends('job_id')
    def get_evaluation_user_inputs(self):
        for obj in self:
            vals = [(5,)]
            if obj.job_id:
                template = self.env['evaluation.template'].search(
                    [('job_id', '=', obj.job_id.id)], limit=1)
                if template and template.question_ids:
                    for question in template.question_ids:
                        vals.append((0, 0, {
                            'record_id': obj.id,
                            'question_id': question.id,
                        }))
            obj.evaluation_user_inputs = vals

    start_date = fields.Date(string='Start Date',
                             required=True,
                             default=_default_get_start_date,
                             readonly=True,
                             states={'draft': [('readonly', False)]},
                             tracking=True)
    end_date = fields.Date(string='End Date',
                             required=True,
                             default=_default_get_end_date,
                             readonly=True,
                             states={'draft': [('readonly', False)]},
                             tracking=True)
    user_id = fields.Many2one(comodel_name='res.users',
                              string="Employee",
                              tracking=True,
                              domain=[('employee_ids', '!=', False)],
                              required=True,
                              default=lambda self: self.env.user.employee_ids and self.env.user or False)
    employee_id = fields.Many2one(comodel_name='hr.employee',
                                  string="Related Employee",
                                  compute="get_employee_id",
                                  store=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirmation', 'Waiting For Confirmation'),
                                        ('approval', 'Waiting For Approval'),
                                        ('done', 'Done')],
                             string="Status",
                             default="draft",
                             tracking=True)
    job_id = fields.Many2one(comodel_name='hr.job',
                             string="Job Position",
                             tracking=True,
                             related="employee_id.job_id",
                             store=True)
    department_id = fields.Many2one(comodel_name='hr.department',
                                    string="Department",
                                    tracking=True,
                                    related="employee_id.department_id",
                                    store=True)
    manager = fields.Many2one(comodel_name='res.users',
                              string="Manager",
                              related="employee_id.parent_id.user_id",
                              store=True,
                              tracking=True)
    is_manager = fields.Boolean(string='Is Manager', compute='_get_is_manager')
    remark = fields.Text(string="Remark", tracking=True)
    work_summary = fields.Text(string="Monthly Work Summary",
                               compute="_get_work_summary",
                               store=True)
    total_days = fields.Integer(string="Total Days",
                                compute="_get_total_days",
                                store=True,
                                help="Total days in the month")
    total_leaves = fields.Float(string='Leaves',
                                compute="_get_total_leaves",
                                store=True)
    evaluation_user_inputs = fields.One2many(
        comodel_name='evaluation.user.input',
        inverse_name='record_id',
        compute='get_evaluation_user_inputs',
        store=True,
        readonly=False)

    @api.constrains('user_id', 'start_date', 'end_date')
    def _check_start_end_duration(self):
        for obj in self:
            if obj.start_date > obj.end_date:
                raise ValidationError(
                    _("Start date can not be greater than end date."))
            if obj.start_date >= fields.Date.today() or obj.end_date >= fields.Date.today():
                raise ValidationError(
                    _("You are trying to evaluate for future. Please select valid evaluation Period."))
            records = self.search([('start_date', '<=', obj.end_date),
                                   ('end_date', '>=', obj.start_date),
                                   ('user_id', '=', obj.user_id.id),
                                   ('id', '!=', obj.id)])
            if records:
                raise ValidationError(
                    _("Oops!!! There is at least one record exists for this employee during this period. Please select different period..."))

    def get_leaves(self):
        self.ensure_one()
        holiday_list = self.env['hr.leave'].search([
            ('date_from', '<=', self.end_date),
            ('date_to', '>=', self.start_date),
            ('state', '=', 'validate'),
            ('employee_id', '=', self.user_id.sudo().employee_ids.ids[0]),
        ])
        result = self.env.ref(
            'hr_holidays.hr_leave_action_action_approve_department').read()[0]
        result['domain'] = [('id', 'in', holiday_list.ids if holiday_list else [])]
        result['context'] = {}
        return result

    def get_task_summary(self):
        self.ensure_one()
        lines = self.env['account.analytic.line'].search([
            ('date', '>=', self.start_date), ('date', '<=', self.end_date),
            ('task_id', '!=', False), ('user_id', '=', self.user_id.id)
        ])
        task_ids = list(set([line.task_id.id for line in lines]))
        result = self.env.ref('employee_evaluation_management.action_project_task_record').read()[0]
        result['domain'] = [('id', 'in', task_ids)]
        result['context'] = self._context.copy()
        return result

    def check_authority(self):
        self.ensure_one()
        if self.env.user._is_superuser() or self.env.user.has_group('project.group_project_manager'):
            return True
        elif self.department_id.sudo().manager_id.user_id != self.env.user:
            return False
        return True

    def submit_evaluation(self):
        for obj in self:
            if obj.state == 'draft':
                if not self.check_authority():
                    if obj.user_id.id == self._uid:
                        pass
                    else:
                        raise UserError(
                            _("Sorry, You are not the authorized Person. Please contact Admin!!!"))
                obj.state = 'confirmation'

    def confirm_evaluation(self):
        for obj in self:
            if obj.state == 'confirmation':
                if not self.check_authority():
                    if obj.manager.id != self._uid:
                        raise UserError(
                            _("You are not the authorized Person. Please contact Admin!!!"))
                if any(not q.answer for q in obj.evaluation_user_inputs):
                    raise ValidationError(
                        _("Oops!! You can not confirm this record without answer all the questions."))
                obj.state = 'approval'

    def approve_evaluation(self):
        for obj in self:
            if obj.state == 'approval':
                if not self.check_authority():
                    raise UserError(
                        _("You are not the authorized Person. Please contact Admin!!!"))
                obj.state = 'done'

    @api.model
    def create(self, vals):
        res = super(EvaluationRecord, self).create(vals)
        message_follower_ids = []
        if res.department_id:
            if res.department_id.sudo().manager_id:
                message_follower_ids.append(
                    res.department_id.sudo().manager_id.user_id.partner_id.id)
        if res.manager:
            message_follower_ids.append(res.manager.partner_id.id)
        message_follower_ids.append(res.user_id.partner_id.id)
        res.message_subscribe(partner_ids=message_follower_ids)
        return res

    def write(self, vals):
        for obj in self:
            if obj.state != 'draft' and (vals.get('start_date') or vals.get('end_date')):
                raise UserError(
                    _("Sorry, You can't update the start date or end date in this stage!!!"))
        return super(EvaluationRecord, self).write(vals)
