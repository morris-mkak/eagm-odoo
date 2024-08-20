# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class EvaluationLabel(models.Model):
    _name = "evaluation.label"
    _description = "Evaluation Label"
    _order = "sequence, id"
    _rec_name = "value"

    question_id = fields.Many2one('evaluation.question',
                                  string='Question',
                                  ondelete='cascade')
    sequence = fields.Integer('Label Sequence order', default=10)
    value = fields.Char('Suggested value', translate=True, required=True)
