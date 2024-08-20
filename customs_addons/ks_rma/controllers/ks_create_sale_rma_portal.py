from odoo import http, tools
from odoo.http import request


class RmaCreationSale(http.Controller):
    """Create RMA From Portal Page Of Sale Order"""

    @http.route('/create/rma/request', type='json', auth='user')
    def create_rma_from_sale_portal(self, **kwargs):
        config_parameter = request.env['ir.config_parameter'].sudo()
        default_team_id = config_parameter.get_param('ks_rma.ks_rma_team_id')
        default_user_id = config_parameter.get_param('ks_rma.ks_rma_user_id')
        default_warehouse_id = config_parameter.get_param('ks_rma.ks_warehouse_id')
        picking_id = kwargs.get('picking_id', False)
        picking_type_id = kwargs.get('picking_type_id', False)
        return_picking_type_id = kwargs.get('return_picking_type_id', False)
        order_id = kwargs.get('sale_order_id', False)
        partner_id = kwargs.get('partner_id', False)
        is_return = kwargs.get('is_return', False)
        is_refund = kwargs.get('is_refund', False)
        is_replace = kwargs.get('is_replace', False)
        rma_lines = kwargs.get('rma_lines', False)
        ks_notes = kwargs.get('ks_notes', False)
        return_reason = kwargs.get('return_reason', False)
        refund_reason = kwargs.get('refund_reason', False)
        replace_reason = kwargs.get('replace_reason', False)
        if not default_warehouse_id:
            default_warehouse_id = request.env['stock.warehouse'].sudo().search(
                                    [('company_id', '=', request.env.company.id)], limit=1).id
        try:
            ks_rma_id = request.env['ks.rma'].sudo().create({
                            'ks_partner_id': partner_id,
                            'ks_picking_id': picking_id,
                            'ks_picking_type_id': picking_type_id,
                            'ks_return_picking_type_id': return_picking_type_id,
                            'ks_sale_order_id': order_id,
                            'ks_team_id': int(default_team_id) if default_team_id else False,
                            'ks_user_id': int(default_user_id) if default_user_id else request.env.user.id,
                            'ks_company_id': request.env.user.company_id.id,
                            'ks_currency_id': request.env.user.currency_id.id,
                            'ks_warehouse_id': int(default_warehouse_id) if default_warehouse_id else False,
                            'ks_selection': 'sale_order',
                            'ks_is_refund': is_refund,
                            'ks_is_return': is_return,
                            'ks_is_replace': is_replace,
                            'ks_reason_return': return_reason,
                            'ks_reason_refund': refund_reason,
                            'ks_reason_replace': replace_reason,
                            'ks_notes': ks_notes,
                        })
            if ks_rma_id and rma_lines:
                price = 0
                tax_ids = []
                rma_product_price = ks_rma_id._return_order_line_product_price_dict(ks_rma_id.ks_sale_order_id.order_line)
                for key, value in rma_lines.items():
                    if rma_product_price.get(int(key), False):
                        price = rma_product_price[int(key)][0]
                        tax_ids = rma_product_price[int(key)][1]
                    request.env['ks.rma.line'].sudo().create({
                        'ks_rma_id': ks_rma_id.id,
                        'ks_product_id': int(key),
                        'ks_delivered_qty': value[0],
                        'ks_returned_qty': value[2],
                        'ks_refund_qty': value[1],
                        'ks_replace_qty': value[3],
                        'ks_price_unit': price,
                        'tax_ids': [(6, 0, tax_ids)],
                        'ks_company_id': request.env.user.company_id.id,
                    })
                return {'Success': ks_rma_id}
        except Exception as e:
            return {'Error': str(e)}