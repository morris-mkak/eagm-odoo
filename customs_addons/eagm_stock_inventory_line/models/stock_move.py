from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    reserved_ctns = fields.Float(
        compute='_compute_reserved_ctns',
        string='Reserved Ctns', store=True,
        digits='Reserved Cartons', 
        readonly=False, default=0)
    done_ctns = fields.Float(
        # compute='_compute_done_ctns', inverse='_inverse_done_ctns',
        string='Done Ctns', store=True,
        digits='Reserved Cartons', 
        readonly=False, default=0)
    
    @api.onchange("product_uom_qty", "qty_done")
    @api.depends("product_uom_qty", "qty_done")
    def _compute_reserved_ctns(self):
        for record in self:
            #if record.product_uom_qty:
            if record.product_id.uom_po_id.factor_inv != 0:
                record.reserved_ctns = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.product_uom_qty
            # else:
            #     record.reserved_ctns = 0
    
    # @api.onchange("reserved_ctns", "qty_done")
    def _inverse_reserved_ctns(self):
        for record in self:
            if record.reserved_ctns and record.product_id and record.product_uom_id:
                record.product_uom_qty = (record.product_id.uom_po_id.factor_inv/record.product_uom_id.factor_inv)*record.reserved_ctns
            # else:
            #     record.product_uom_qty = 0

    @api.onchange("qty_done")
    def _compute_done_ctns(self):
        for record in self:
            #if record.qty_done:
            if record.product_id.uom_po_id.factor_inv != 0:
                record.done_ctns = (record.product_uom_id.factor_inv/record.product_id.uom_po_id.factor_inv)*record.qty_done
            # else:
            #     record.done_ctns = 0
    
    @api.onchange("done_ctns")
    def _inverse_done_ctns(self):
        for record in self:
            if record.done_ctns and record.product_id and record.product_uom_id:
                record.qty_done = (record.product_id.uom_po_id.factor_inv/record.product_uom_id.factor_inv)*record.done_ctns
            # else:
            #     record.qty_done = 0
    
    def _get_aggregated_product_quantities(self, **kwargs):
        """ Returns a dictionary of products (key = id+name+description+uom) and corresponding values of interest.

        Allows aggregation of data across separate move lines for the same product. This is expected to be useful
        in things such as delivery reports. Dict key is made as a combination of values we expect to want to group
        the products by (i.e. so data is not lost). This function purposely ignores lots/SNs because these are
        expected to already be properly grouped by line.

        returns: dictionary {product_id+name+description+uom: {product, name, description, qty_done, product_uom}, ...}
        """
        aggregated_move_lines = {}
        for move_line in self:
            name = move_line.product_id.display_name
            description = move_line.move_id.description_picking
            if description == name or description == move_line.product_id.name:
                description = False
            uom = move_line.product_uom_id
            line_key = str(move_line.product_id.id) + "_" + name + (description or "") + "uom " + str(uom.id)


            if line_key not in aggregated_move_lines:
                aggregated_move_lines[line_key] = {'name': name,
                                                   'description': description,
                                                   'qty_done': move_line.qty_done,
                                                   'product_uom': uom.name,
                                                   'product': move_line.product_id,
                                                   'reserved_ctns': move_line.reserved_ctns,
                                                   'done_ctns': move_line.done_ctns,
						   'x_studio_packing_code_1': move_line.x_studio_packing_code_1
						}
            else:
                aggregated_move_lines[line_key]['qty_done'] += move_line.qty_done
        return aggregated_move_lines
