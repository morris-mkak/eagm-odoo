# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class WorkType(models.Model):
    _name = "work.type"
    _description = "Work Type"

    name = fields.Char(string='Work Name', required=True)
    code = fields.Char(string='Work Code', required=True)
    allow_manual_entry = fields.Boolean(string='Allow For Manual Entry')


class Project(models.Model):
    _inherit = "project.project"

    work_type_id = fields.Many2one(comodel_name='work.type',
                                   string='Work Type')


class Task(models.Model):
    _inherit = "project.task"

    @api.model
    def _set_work_type(self):
        """ Default Function for field 'work_type_id'."""
        work_type_id = self.env['work.type'].search([("name", "=", "General")])
        if work_type_id:
            return work_type_id.ids[0]
        else:
            return False

    work_type_id = fields.Many2one(comodel_name='work.type',
                                   string='Work Type',
                                   default=_set_work_type)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id and self.project_id.work_type_id:
            self.work_type_id = self.project_id.work_type_id.id
        else:
            self.work_type_id = self._set_work_type()
