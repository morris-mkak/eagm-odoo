from odoo import fields, models, api

class ResPartner(models.Model):
  _inherit = 'res.partner'
  
  is_chain_customer = fields.Boolean("Is Chain", default=False)
