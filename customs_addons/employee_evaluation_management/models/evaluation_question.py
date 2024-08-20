# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class EvaluationQuestion(models.Model):
    _name = "evaluation.question"
    _description = "Question for evaluation record"
    _rec_name = "question"
    _order = "sequence, id"

    @api.model
    def default_get(self, fields):
        defaults = super(EvaluationQuestion, self).default_get(fields)
        if (not fields or 'question_type' in fields):
            defaults['question_type'] = False if defaults.get('is_page') == True else 'free_text'
        return defaults

    template_id = fields.Many2one(comodel_name='evaluation.template',
                                  string='Evaluation Template',
                                  ondelete='cascade')
    page_id = fields.Many2one('evaluation.question',
                              string='Page',
                              compute="_compute_page_id",
                              store=True)
    question_ids = fields.One2many('evaluation.question',
                                   string='Questions',
                                   compute="_compute_question_ids")
    is_page = fields.Boolean('Is a page?')
    sequence = fields.Integer(string='Sequence', default=10)
    title = fields.Char(string='Title', required=True, translate=True)
    question = fields.Char(string='Question', related="title")
    description = fields.Html(
        string='Description',
        help="Use this field to add additional explanations about your question",
        translate=True)
    question_type = fields.Selection(selection=[
        ('free_text', 'Multiple Lines Text Box'),
        ('textbox', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
    ],
                                     string='Question Type')
    labels_ids = fields.One2many(
        comodel_name='evaluation.label',
        inverse_name='question_id',
        string='Types of answers',
        copy=True,
        help='Labels used for proposed choices: simple choice, multiple choice and columns of matrix'
    )

    @api.onchange('is_page')
    def _onchange_is_page(self):
        if self.is_page:
            self.question_type = False

    @api.depends('template_id.question_and_page_ids.is_page', 'template_id.question_and_page_ids.sequence')
    def _compute_question_ids(self):
        for question in self:
            if question.is_page:
                next_page_index = False
                for page in question.template_id.page_ids:
                    if page._index() > question._index():
                        next_page_index = page._index()
                        break
                question.question_ids = question.template_id.question_ids.filtered(
                    lambda q: q._index() > question._index() and
                    (not next_page_index or q._index() < next_page_index))
            else:
                question.question_ids = self.env['evaluation.question']

    @api.depends('template_id.question_and_page_ids.is_page', 'template_id.question_and_page_ids.sequence')
    def _compute_page_id(self):
        for question in self:
            if question.is_page:
                question.page_id = None
            else:
                page = None
                for q in question.template_id.question_and_page_ids.sorted():
                    if q == question:
                        break
                    if q.is_page:
                        page = q
                question.page_id = page

    def _index(self):
        self.ensure_one()
        return list(self.template_id.question_and_page_ids).index(self)
