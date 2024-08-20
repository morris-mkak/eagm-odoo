from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_category_id = fields.Many2one('partner.category', 'Category')


class ResPartnerHCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    name = fields.Char("Category Name", required=True)
    parent_id = fields.Many2one('partner.category', 'Parent Category')
    child_category_ids = fields.One2many('partner.category', 'parent_id', 'Child Category')
    partner_ids = fields.One2many('res.partner', 'partner_category_id', 'Partners')
