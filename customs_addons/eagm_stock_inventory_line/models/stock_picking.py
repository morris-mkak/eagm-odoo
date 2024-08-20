from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_reserved_ctns = fields.Float(
        compute='_compute_total_reserved_ctns', 
        string='Total Reserved Cartons', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    total_done_ctns = fields.Float(
        compute='_compute_total_done_ctns', 
        string='Total Done Cartons', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    total_ctns = fields.Float(
        compute='_compute_total_ctns', 
        string='Total Cartons', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    total_ctns_without_package = fields.Float(
        compute='_compute_total_ctns', 
        string='Cartons Without Package', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    total_ctns_in_package = fields.Float(
        compute='_compute_total_ctns', 
        string='Cartons in Package', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    total_repacked_ctns = fields.Float(
        compute='_compute_total_ctns', 
        string='Repacked into', store=True,
        digits='Total Cartons', 
        readonly=True, default=0)
    
    
    @api.onchange("move_line_ids_without_package")
    @api.depends("move_line_ids_without_package")
    def _compute_total_ctns(self):
        for record in self:
            total_ctns_without_package = 0
            total_lines_with_package = []
            total_ctns_in_package = 0
            if record.move_line_ids_without_package:
                for rec in record.move_line_ids_without_package:
                    if rec.result_package_id.id:
                        total_lines_with_package.append(rec.result_package_id.id)
                        total_ctns_in_package += rec.done_ctns
                    elif not rec.result_package_id.id:
                        total_ctns_without_package += rec.done_ctns
                record.total_ctns = total_ctns_without_package + len(set(total_lines_with_package))
                record.total_ctns_without_package = total_ctns_without_package
                record.total_ctns_in_package = total_ctns_in_package
                record.total_repacked_ctns = len(set(total_lines_with_package))
    
    @api.onchange("move_line_ids_without_package")
    @api.depends("move_line_ids_without_package")
    def _compute_total_done_ctns(self):
        for record in self:
            total_done_ctns = 0
            if record.move_line_ids_without_package:
                for rec in record.move_line_ids_without_package:
                    total_done_ctns += rec.done_ctns
                record.total_done_ctns = total_done_ctns
    
    @api.onchange("move_line_ids_without_package")
    @api.depends("move_line_ids_without_package")
    def _compute_total_reserved_ctns(self):
        for record in self:
            total_reserved_ctns = 0
            if record.move_line_ids_without_package:
                for rec in record.move_line_ids_without_package:
                    total_reserved_ctns += rec.reserved_ctns
                record.total_reserved_ctns = total_reserved_ctns

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self._compute_total_ctns()
        self._compute_total_reserved_ctns()
        self._compute_total_done_ctns()
        return res