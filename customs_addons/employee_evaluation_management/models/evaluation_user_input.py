# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import pytz

from odoo import api, fields, models, _


class EvaluationUserInput(models.Model):
    _name = "evaluation.user.input"
    _description = "Evaluation User Input"

    @api.depends('question_type', 'free_text', 'text_box', 'numerical_box',
                 'date_box', 'datetime_box', 'simple_choice', 'multiple_choice')
    def get_answer(self):
        for obj in self:
            if obj.question_type == 'free_text':
                obj.answer = obj.free_text if obj.free_text else ''
            elif obj.question_type == 'textbox':
                obj.answer = obj.text_box if obj.text_box else ''
            elif obj.question_type == 'numerical_box':
                obj.answer = str(obj.numerical_box) if obj.numerical_box else ''
            elif obj.question_type == 'date':
                obj.answer = obj.date_box.strftime('%d-%b-%Y') if obj.date_box else ''
            elif obj.question_type == 'datetime':
                if obj.datetime_box:
                    user_tz = self._context.get('tz', 'Asia/Kolkata') or 'Asia/Kolkata'
                    local = pytz.timezone(user_tz)
                    obj.answer = pytz.utc.localize(
                        obj.datetime_box).astimezone(local).strftime('%d-%b-%Y %H:%M:%S')
                else:
                    obj.answer = ''
            elif obj.question_type == 'simple_choice':
                obj.answer = obj.simple_choice.value if obj.simple_choice else ''
            elif obj.question_type == 'multiple_choice':
                obj.answer = ', '.join(obj.multiple_choice.mapped('value')) if obj.multiple_choice else ''
            else:
                obj.answer = ''

    record_id = fields.Many2one(comodel_name='evaluation.record',
                                string='Evaluation Record',
                                required=True,
                                ondelete='cascade')
    question_id = fields.Many2one(comodel_name='evaluation.question',
                                  string='Question',
                                  domain=[('is_page', '=', False)],
                                  required=True)
    question_type = fields.Selection(string='Question Type',
                                     related="question_id.question_type",
                                     store=True,
                                     readonly=True)
    answer = fields.Char(string='Answer',
                         compute='get_answer',
                         store=True,
                         readonly=True)
    free_text = fields.Text(string='Free Text')
    text_box = fields.Char(string='Text Box')
    numerical_box = fields.Float(string='Numerical Box')
    date_box = fields.Date(string='Date Box')
    datetime_box = fields.Datetime(string='Datetime Box')
    simple_choice = fields.Many2one(comodel_name='evaluation.label',
                                    string='Simple Choice')
    multiple_choice = fields.Many2many(comodel_name='evaluation.label',
                                       string='Multiple Choices')
