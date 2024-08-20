# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class EvaluationTemplate(models.Model):
    _name = "evaluation.template"
    _description = "Question template for evaluation record"
    _rec_name = "job_id"

    job_id = fields.Many2one(comodel_name="hr.job",
                             string="Job Position",
                             required=True,
                             index=True,
                             copy=False)
    question_and_page_ids = fields.One2many(comodel_name='evaluation.question',
                                            inverse_name='template_id',
                                            string='Sections and Questions',
                                            copy=True)
    page_ids = fields.One2many('evaluation.question',
                               string='Pages',
                               compute="_compute_page_and_question_ids")
    question_ids = fields.One2many('evaluation.question',
                                   string='Questions',
                                   compute="_compute_page_and_question_ids")

    _sql_constraints = [
        ('unique_job_id', 'unique(job_id)', "Already created for the selected job position."),
    ]

    @api.depends('question_and_page_ids')
    def _compute_page_and_question_ids(self):
        for template in self:
            template.page_ids = template.question_and_page_ids.filtered(lambda question: question.is_page)
            template.question_ids = template.question_and_page_ids - template.page_ids
