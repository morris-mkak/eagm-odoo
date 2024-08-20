# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class KsStockPickingExtended(models.Model):
    """ Inherited the stock.picking model for the implementation of an RMA Module"""

    _inherit = "stock.picking"

    ks_rma_id = fields.Many2one(comodel_name="ks.rma", string="RMA Order",
                                readonly=True, help="Select the RMA Orders.")
    is_rma_in_picking = fields.Boolean('Distinguish RMA IN picking')
    is_rma_out_picking = fields.Boolean('Distinguish RMA Out picking')

    # Return product lines Dic with product id as key
    def _return_order_line_product_qty_dict(self, rec):
        rma_product_qty = {}
        for line in rec.move_lines:
            if line.product_id:
                rma_product_qty[line.product_id.id] = line.quantity_done
        return rma_product_qty

    @api.constrains('state')
    def _update_return_quantity_to_order(self):
        for rec in self:
            if rec.state == 'done' and rec.ks_rma_id and rec.ks_rma_id.ks_selection != 'transfer':
                if rec.is_rma_in_picking and rec.ks_rma_id.ks_selection == 'sale_order':
                    if rec.ks_rma_id.ks_picking_id.picking_type_code == 'outgoing':
                        qty_dict = self._return_order_line_product_qty_dict(rec)
                        for line in rec.ks_rma_id.ks_sale_order_id.order_line:
                            if qty_dict.get(line.product_id.id, False):
                                if line.qty_delivered:
                                    line.qty_delivered -= qty_dict[line.product_id.id]
                if rec.is_rma_out_picking and rec.ks_rma_id.ks_selection == 'purchase_order':
                    if rec.ks_rma_id.ks_picking_id.picking_type_code == 'incoming':
                        qty_dict = self._return_order_line_product_qty_dict(rec)
                        for line in rec.ks_rma_id.ks_purchase_order_id.order_line:
                            if qty_dict.get(line.product_id.id, False):
                                if line.qty_received:
                                    line.qty_received -= qty_dict[line.product_id.id]

    @api.onchange('ks_rma_id')
    def _onchange_origin(self):
        for record in self:
            record.origin = record.ks_rma_id.ks_sequence_code

    def action_ks_rma_order(self):
        """ This opens a new window for ks.rma model """

        ks_ctx = dict()
        ks_check_approval = self.env['ir.config_parameter'].sudo().get_param('ks_rma.is_rma_approval_process_access')
        ks_ctx['default_ks_partner_id'] = self.partner_id.id
        if self.sale_id:
            ks_ctx['default_ks_selection'] = 'sale_order'
            ks_ctx['default_ks_sale_order_id'] = self.sale_id.id
            ks_ctx['default_ks_check_approval'] = ks_check_approval
        elif self.purchase_id:
            ks_ctx['default_ks_selection'] = 'purchase_order'
            ks_ctx['default_ks_purchase_order_id'] = self.purchase_id.id
            ks_ctx['default_ks_check_approval'] = ks_check_approval
        else:
            ks_ctx['default_ks_selection'] = 'transfer'
        ks_ctx['default_ks_picking_id'] = self.id
        ks_ctx['default_ks_check_approval'] = ks_check_approval
        return {
            'name': _('Create RMA'),
            'res_model': 'ks.rma',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ks_ctx
        }


class KsStockPickingTypeExtended(models.Model):
    """ Inherited the stock.picking.type for the implementation of an RMA Module"""

    _inherit = "stock.picking.type"

    ks_is_rma_operation = fields.Boolean(string="RMA Operation",
                                         help="If yes then apply RMA Operation for the operation types.")
