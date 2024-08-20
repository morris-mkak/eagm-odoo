# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel): 
	_inherit = 'res.config.settings'

	allow_warehouse = fields.Boolean(string="Allow Warehouse in Sale Order Line", default=False)

	def set_values(self):
		self.env['ir.config_parameter'].sudo().set_param('bi_multiwarehouse_for_sales.allow_warehouse', self.allow_warehouse)
		res = super(ResConfigSettings, self).set_values()

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		config_parameter = self.env['ir.config_parameter'].sudo()
		allow_warehouse = config_parameter.get_param('bi_multiwarehouse_for_sales.allow_warehouse')
		res.update(allow_warehouse=allow_warehouse)
		return res
