# -*- coding: utf-8 -*-

from datetime import date
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError, UserError

_logger = logging.getLogger(__name__)


class KsRma(models.Model):
    """ Model for the RMA Orders """

    _name = "ks.rma"
    _inherit = ["mail.thread", "portal.mixin", "mail.activity.mixin"]
    _description = "RMA Orders"
    _rec_name = "ks_sequence_code"

    ks_sequence_code = fields.Char(string="RMA Number", required=True, copy=False, readonly=True,
                                   states={'draft': [('readonly', False)]}, index=True, tracking=True,
                                   help="Unique sequence is allocated to the RMA record.",
                                   default=_('New'))
    ks_partner_id = fields.Many2one(comodel_name="res.partner", string="Partner",
                                    readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the partner Information")
    ks_picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking",
                                    readonly=True, required=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the Stock Picking Information")
    ks_picking_id_replace = fields.Many2one(comodel_name="stock.picking",
                                            help="Used to store replace operation picking")
    ks_selection = fields.Selection([('sale_order', 'Sale Order'), ('purchase_order', 'Purchase Order'),
                                     ('transfer', 'Transfer')], string="Sale/Purchase/Transfer",
                                    readonly=True, tracking=True, states={'draft': [('readonly', False)]},
                                    help='RMA Creation Method 1. Sale Order: From Sale order '
                                         '2. Purchase Order: From Purchase order'
                                         '3. Transfer: Directly From Picking')
    ks_sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order",
                                       readonly=True, tracking=True,
                                       states={'draft': [('readonly', False)]},
                                       help="Tells the Sale order Information")
    ks_purchase_order_id = fields.Many2one(comodel_name="purchase.order", string="Purchase Order",
                                           readonly=True, tracking=True,
                                           states={'draft': [('readonly', False)]},
                                           help="Tells the Purchase Order Information")
    ks_team_id = fields.Many2one(comodel_name="crm.team", string="Assigned Team",
                                 readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 help="Tells the Team Information")
    ks_user_id = fields.Many2one(comodel_name="res.users", string="Assigned Person",
                                 default=lambda self: self.env.user.id,
                                 readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 help="Tells the user Information")
    ks_company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                    default=lambda self: self.env.user.company_id.id,
                                    readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the Company Information.")
    ks_warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse",
                                      readonly=True, tracking=True,
                                      states={'draft': [('readonly', False)]},
                                      help="Tells the Warehouse Information")
    ks_currency_id = fields.Many2one(comodel_name="res.currency", string="Currency",
                                     default=lambda self: self.env.user.currency_id.id,
                                     readonly=True, tracking=True,
                                     states={'draft': [('readonly', False)]},
                                     help="Tells the Currency Information.")
    ks_confirmed_user_id = fields.Many2one(comodel_name="res.users", string="Confirmed By",
                                           readonly=True, tracking=True,
                                           help="Tells the Approved User Information.")
    ks_date_requested = fields.Date(string="Requested Date", default=date.today(),
                                    readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the Requested Date.")
    ks_date_closed = fields.Date(string="Closed Date",
                                 readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 help="Tells the Closing Date.")
    ks_date_confirmed = fields.Date(string="Confirmation Date",
                                    readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the Confirmation Date.")
    ks_date_cancelled = fields.Date(string="Cancel Date",
                                    readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    help="Tells the Cancellation Date.")
    state = fields.Selection(
        ([('draft', 'Draft'), ('sent', 'Sent'), ('confirm', 'Confirmed'),
          ('cancel', 'Cancelled'), ("refunded", "Refunded"),
          ("returned", "Returned"), ("replaced", "Replaced"), ('refund_return', 'Refunded+Returned'),
          ('reject', 'Rejected'), ('wait', 'Waiting'), ('closed', 'Closed')]), string="State", default="draft",
        tracking=True, help="Tells the status of the RMA Orders.")
    ks_notes = fields.Text(string="Notes", help="Add a description for your RMA Order.")
    ks_rma_line_ids = fields.One2many(comodel_name="ks.rma.line", inverse_name="ks_rma_id",
                                      readonly=True, tracking=True,
                                      states={'draft': [('readonly', False)]},
                                      string="RMA Line")
    ks_get_picking = fields.Char(string="Sale Order Name",
                                 readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 help="Tells the particular sale order/purchase order name")
    ks_picking_type_id = fields.Many2one(comodel_name="stock.picking.type",
                                         readonly=True, tracking=True, string='Operation Type',
                                         states={'draft': [('readonly', False)]},
                                         help='Required to create stock picking')
    ks_return_picking_type_id = fields.Many2one(comodel_name="stock.picking.type",
                                                readonly=True, tracking=True, string='Operation Type For Returns',
                                                states={'draft': [('readonly', False)]},
                                                help='Required to create return stock picking')
    ks_refund_invoice_id = fields.Many2one('account.move', string='Refund',
                                           tracking=True, readonly=True)
    ks_return_picking_id = fields.Many2one('stock.picking', string='Return Picking',
                                           tracking=True, readonly=True)
    ks_is_refund = fields.Boolean(string='Is Refund', readonly=True, states={'draft': [('readonly', False)]},
                                  tracking=True, help='Checked it if operation type is Refund')
    ks_is_return = fields.Boolean(string='Is Return', readonly=True, states={'draft': [('readonly', False)]},
                                  tracking=True, help='Checked it if operation type is Return')
    ks_is_replace = fields.Boolean(string='Is Replace', readonly=True, states={'draft': [('readonly', False)]},
                                   tracking=True, help='Checked it if operation type is Replace')
    ks_reason_return = fields.Many2one(string='Reason for Return', states={'draft': [('readonly', False)]},
                                       tracking=True, readonly=True, comodel_name='ks.return.reasons')
    ks_reason_refund = fields.Many2one(string='Reason for Refund', states={'draft': [('readonly', False)]},
                                       tracking=True, readonly=True, comodel_name='ks.refund.reasons')
    ks_reason_replace = fields.Many2one(string='Reason for Replace', states={'draft': [('readonly', False)]},
                                        tracking=True, readonly=True, comodel_name='ks.replace.reasons')
    ks_status_return = fields.Char(string='Return Status', compute='_check_status_return')
    ks_status_refund = fields.Char(string='Refund Status', compute='_check_status_refund')
    ks_refund_amount = fields.Float(string='Total Refund Amount', compute='calculate_amount')
    ks_store_refund_amount = fields.Float(help='To store the computed value')
    ks_policy = fields.Text(string='Policies for operation', related='ks_company_id.ks_policy')
    ks_terms = fields.Text(string='Terms and Conditions', related='ks_company_id.ks_terms')
    ks_check_approval = fields.Boolean(string='Check Approval Process',
                                       default=lambda self: True if self.env['ir.config_parameter'].sudo().get_param
                                                                    ('ks_rma.is_rma_approval_process_access') in [
                                                                        "TRUE", "True", "true"] else False)
    ks_check_preview = fields.Boolean(string='Check Preview button',
                                      default=lambda self: True if self.env['ir.config_parameter'].sudo().get_param
                                                                    ('ks_rma.is_rma_portal_access') in [
                                                                       "TRUE", "True", "true"] else False)

    def action_ks_rma_send_approval(self):
        return self.write({'state': 'wait'})

    def action_ks_rma_approved(self):
        if not (self.ks_is_return or self.ks_is_refund or self.ks_is_replace):
            raise UserError(_('Please select at least one RMA operation!!'))
        else:
            for order in self.filtered(lambda order: order.ks_partner_id not in order.message_partner_ids):
                order.message_subscribe([order.ks_partner_id.id])
            if self.ks_user_id and self.ks_user_id.partner_id not in self.message_partner_ids:
                self.message_subscribe([self.ks_user_id.partner_id.id])
            return self.write({
                'state': 'confirm',
                'ks_date_confirmed': date.today(),
                'ks_confirmed_user_id': self.env.user.id
            })

    def action_ks_rma_send_reject(self):
        return self.write({'state': 'reject'})

    @api.onchange('ks_is_replace')
    def uncheck_operations(self):
        if self.ks_is_replace:
            self.ks_is_refund = False
            self.ks_is_return = False

    @api.depends('ks_rma_line_ids.ks_refund_qty')
    def calculate_amount(self):
        for rec in self:
            if rec.ks_is_refund:
                rec.ks_refund_amount += sum(rec.ks_rma_line_ids.mapped('ks_subtotal_amount'))
            else:
                rec.ks_refund_amount = 0
            rec.ks_store_refund_amount = rec.ks_refund_amount

    @api.constrains('ks_return_picking_id.state')
    def _check_status_return(self):
        for rec in self:
            if not rec.ks_is_replace and rec.state != 'closed':
                rec.ks_status_return = ''
                if (rec.ks_return_picking_id and rec.ks_return_picking_id.state == 'done') \
                        and (rec.ks_refund_invoice_id and rec.ks_refund_invoice_id.state == 'posted'
                             and rec.ks_refund_invoice_id.payment_state == 'paid'):
                    rec.state = 'refund_return'
                elif rec.ks_return_picking_id and rec.ks_return_picking_id.state == 'done':
                    rec.ks_status_return = 'Returned'
                    rec.state = 'returned'
                else:
                    pass
            else:
                rec.ks_status_return = ''

    @api.constrains('ks_refund_invoice_id.payment_state')
    def _check_status_refund(self):
        for rec in self:
            if not rec.ks_is_replace and rec.state != 'closed':
                rec.ks_status_refund = ''
                if (rec.ks_return_picking_id and rec.ks_return_picking_id.state == 'done') \
                        and (rec.ks_refund_invoice_id and rec.ks_refund_invoice_id.state == 'posted'
                             and rec.ks_refund_invoice_id.payment_state == 'paid'):
                    rec.state = 'refund_return'
                elif rec.ks_refund_invoice_id and rec.ks_refund_invoice_id.state == 'posted' \
                        and rec.ks_refund_invoice_id.payment_state == 'paid':
                    rec.ks_status_refund = 'Refunded'
                    rec.state = 'refunded'
                else:
                    pass
            else:
                rec.ks_status_refund = ''

    @api.constrains('ks_picking_id')
    def _set_rma_id_in_picking(self):
        if self.ks_picking_id:
            self.ks_picking_id.ks_rma_id = self.id

    @api.onchange('ks_picking_type_id')
    def _set_return_operation_type(self):
        if self.ks_picking_type_id and self.ks_picking_type_id.return_picking_type_id:
            self.ks_return_picking_type_id = self.ks_picking_type_id.return_picking_type_id.id

    # Return RMA lines Dic with product id as key
    def _return_order_line_product_price_dict(self, order_line):
        rma_product_price = {}
        for rma_line in order_line:
            if rma_line.product_id:
                if self.ks_selection == 'sale_order':
                    rma_product_price[rma_line.product_id.id] = [rma_line.price_unit, rma_line.tax_id.ids,
                                                                 rma_line.discount]
                if self.ks_selection == 'purchase_order':
                    rma_product_price[rma_line.product_id.id] = [rma_line.price_unit, rma_line.taxes_id.ids, 0.0]
        return rma_product_price

    @api.onchange('ks_is_return')
    def _set_default_return_quantity(self):
        if self.ks_picking_id:
            for rma_line in self.ks_rma_line_ids:
                if self.ks_is_return:
                    rma_line.ks_returned_qty = rma_line.ks_delivered_qty
                else:
                    rma_line.ks_returned_qty = 0

    @api.onchange('ks_is_refund')
    def _set_default_refund_quantity(self):
        if self.ks_picking_id and self.ks_is_refund:
            for rma_line in self.ks_rma_line_ids:
                if self.ks_is_refund:
                    rma_line.ks_refund_qty = rma_line.ks_delivered_qty
                else:
                    rma_line.ks_refund_qty = 0

    @api.onchange('ks_is_replace')
    def _set_default_replace_quantity(self):
        if self.ks_picking_id and self.ks_is_replace:
            for rma_line in self.ks_rma_line_ids:
                if self.ks_is_replace:
                    rma_line.ks_replace_qty = rma_line.ks_delivered_qty
                else:
                    rma_line.ks_replace_qty = 0

    @api.onchange('ks_picking_id')
    def _set_rma_line_ids_from_picking(self):
        if self.ks_picking_id:
            line_ids, tax_ids = [], []
            rma_product_price = {}
            price = 0
            discount = 0.0
            if not self.ks_picking_id.move_lines:
                self.update({
                    'ks_picking_id': False
                })
                raise UserError(_('Selected picking has no move line!! Please select another picking'))
            self.ks_picking_type_id = self.ks_picking_id.picking_type_id.id
            if self.ks_selection == 'transfer':
                self.ks_partner_id = self.ks_picking_id.partner_id.id
            if self.ks_selection == 'sale_order':
                rma_product_price = self._return_order_line_product_price_dict(self.ks_sale_order_id.order_line)
            if self.ks_selection == 'purchase_order':
                rma_product_price = self._return_order_line_product_price_dict(self.ks_purchase_order_id.order_line)
            for move_line in self.ks_picking_id.move_line_ids_without_package:
                if rma_product_price.get(move_line.product_id.id, False):
                    price = rma_product_price[move_line.product_id.id][0]
                    tax_ids = rma_product_price[move_line.product_id.id][1]
                    discount = rma_product_price[move_line.product_id.id][2]
                line_ids.append(self.env['ks.rma.line'].create({
                    'ks_product_id': move_line.product_id.id if move_line.product_id else False,
                    'ks_delivered_qty': move_line.qty_done,
                    'ks_price_unit': price,
                    'tax_ids': [(6, 0, tax_ids)],
                    'discount': discount,
                    'ks_company_id': self.ks_company_id.id,
                    'ks_returned_qty': move_line.qty_done if self.ks_is_return else 0,
                    'ks_refund_qty': move_line.qty_done if self.ks_is_refund else 0,
                    'ks_replace_qty': move_line.qty_done if self.ks_is_replace else 0
                }).id)
            self.ks_rma_line_ids = [(6, 0, line_ids)]

    @api.onchange('ks_selection')
    def apply_domain_on_picking_transfer(self):
        if self.ks_selection == 'transfer':
            if not self.ks_partner_id:
                return {'domain': {'ks_picking_id': [('origin', '=', False),
                                                     ('state', '=', 'done'),
                                                     ('ks_rma_id', '=', False)]
                                   }
                        }
            else:
                return {'domain': {'ks_picking_id': [('origin', '=', False),
                                                     ('partner_id', '=', self.ks_partner_id.id),
                                                     ('state', '=', 'done'),
                                                     ('ks_rma_id', '=', False)]
                                   }
                        }

    @api.onchange('ks_sale_order_id', 'ks_purchase_order_id')
    def onchange_order_id(self):
        if self.ks_sale_order_id:
            self.ks_get_picking = self.ks_sale_order_id.name
            self.ks_partner_id = self.ks_sale_order_id.partner_id
        if self.ks_purchase_order_id:
            self.ks_get_picking = self.ks_purchase_order_id.name
            self.ks_partner_id = self.ks_purchase_order_id.partner_id
        if self.ks_selection == 'transfer':
            self.ks_get_picking = self.ks_picking_id.name
        return {'domain': {'ks_picking_id': [('partner_id', '=', self.ks_partner_id.id),
                                             ('origin', '=', self.ks_get_picking),
                                             ('state', '=', 'done'), ('ks_rma_id', '=', False)]
                           }}

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['ks_sequence_code'] = self.env['ir.sequence'].next_by_code('ks.rma')
        return super(KsRma, self).create(values)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancel', 'closed'):
                raise UserError(_(
                    'You can delete the RMA Order whose are in Draft Cancel or Closed state. '
                    'First, you have to cancel or close it. '))
            return super(KsRma, self).unlink()

    def action_ks_rma_cancel(self):
        return self.write({'state': 'cancel',
                           'ks_date_cancelled': date.today()})

    def action_ks_rma_close(self):
        return self.write({'state': 'closed',
                           'ks_date_closed': date.today()})

    def _prepare_confirmation_mail_to_partner(self):
        ks_template_id = self.env.ref('ks_rma.mail_template_ks_rma_confirmation')
        if ks_template_id:
            try:
                ks_template_id.send_mail(self.id)
                _logger.info('Confirmation Mail Has Sent To %s', self.ks_partner_id.name)
            except Exception as e:
                _logger.error(e.message, exc_info=True)

    @api.constrains('ks_confirmed_user_id')
    def _send_confirmation_mail(self):
        if self.ks_confirmed_user_id:
            self._prepare_confirmation_mail_to_partner()

    def _prepare_requested_mail_to_assigned_person(self):
        ks_template_id = self.env.ref('ks_rma.mail_template_ks_rma_requested')
        if ks_template_id:
            try:
                ks_template_id.send_mail(self.id)
                _logger.info('RMA Request Mail Has been Sent To %s', self.ks_user_id.name)
            except Exception as e:
                _logger.error(e.message, exc_info=True)

    @api.constrains('ks_date_requested')
    def _send_rma_requested_mail(self):
        if self.ks_date_requested:
            self._prepare_requested_mail_to_assigned_person()

    def action_ks_rma_email(self):
        """ Opens a wizard to compose an email, with ks_rma mail template loaded by default """
        self.ensure_one()
        template = self.env.ref('ks_rma.mail_template_ks_rma', False)
        form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = {
            'default_model': 'ks.rma',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template),
            'default_template_id': template and template.id or False,
            'default_composition_mode': 'comment',
            'mark_rma_as_sent': True,
            'model_description': 'RMA',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('ks_partner_id')
    def onchange_ks_partner_id(self):
        for rec in self:
            if rec.ks_partner_id:
                if rec.ks_selection:
                    if rec.ks_selection == 'sale_order':
                        if rec.ks_sale_order_id and rec.ks_sale_order_id.id not in rec.ks_partner_id.sale_order_ids.ids:
                            rec.ks_sale_order_id = False
                    if rec.ks_selection == 'purchase_order':
                        if rec.ks_purchase_order_id and rec.ks_purchase_order_id.id \
                                not in rec.env['purchase.order'].search(
                            [('partner_id', '=', rec.ks_partner_id.id)]).ids:
                            rec.ks_purchase_order_id = False
                    if rec.ks_selection == 'transfer':
                        if rec.ks_picking_id and rec.ks_partner_id != rec.ks_picking_id.partner_id:
                            rec.ks_picking_id = False
                return {'domain': {'ks_sale_order_id': [('partner_id', '=', rec.ks_partner_id.id)
                    , ('state', 'in', ('sale', 'done'))],
                                   'ks_purchase_order_id': [('partner_id', '=', rec.ks_partner_id.id),
                                                            ('state', 'in', ('purchase', 'done'))],
                                   }
                        }
            else:
                return {'domain': {'ks_sale_order_id': [('state', 'in', ('sale', 'done'))],
                                   'ks_purchase_order_id': [('state', 'in', ('purchase', 'done'))],
                                   }
                        }

    # return a action of picking
    def action_view_receipt(self):
        if self.ks_return_picking_id:
            action = self.env.ref('stock.action_picking_tree_all').with_context(
                active_id=self.id).read()[0]
            action.update(
                res_id=self.ks_return_picking_id.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
            return action

    def action_view_receipt_replace(self):
        if self.ks_picking_id_replace:
            action = self.env.ref('stock.action_picking_tree_all').with_context(
                active_id=self.id).read()[0]
            action.update(
                res_id=self.ks_picking_id_replace.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
            return action

    # Prepare receipt on RmA Form
    def _prepare_picking_receipt(self):
        stock_picking = self.env['stock.picking']
        line_ids = []
        stock_dict_sale = {
            'ks_rma_id': self.id,
            'is_rma_in_picking': True,
            'state': 'assigned',
            'origin': self.ks_get_picking,
            'partner_id': self.ks_partner_id.id,
            'picking_type_id': self.ks_return_picking_type_id.id,
            'company_id': self.ks_company_id.id,
            'location_id': self.ks_picking_id.location_dest_id.id,
            'location_dest_id': self.ks_picking_id.location_id.id
        }
        stock_picking = stock_picking.create(stock_dict_sale)
        for rma_line in self.ks_rma_line_ids:
            if rma_line.ks_returned_qty:
                line_ids.append(self.env['stock.move'].create({
                    'name': rma_line.ks_product_id.name if rma_line.ks_product_id else '',
                    'product_id': rma_line.ks_product_id.id if rma_line.ks_product_id else False,
                    'product_uom_qty': rma_line.ks_returned_qty,
                    'picking_id': stock_picking.id,
                    'product_uom': rma_line.ks_product_id.uom_id.id if rma_line.ks_product_id else False,
                    'location_id': self.ks_picking_id.location_dest_id.id,
                    'location_dest_id': self.ks_picking_id.location_id.id
                }).id)
        return stock_picking

    # Prepare delivery order on Rma form
    def _prepare_picking_order(self):
        stock_picking = self.env['stock.picking']
        line_ids = []
        stock_dict_sale = {
            'ks_rma_id': self.id,
            'is_rma_out_picking': True,
            'state': 'assigned',
            'origin': self.ks_get_picking,
            'partner_id': self.ks_partner_id.id,
            'company_id': self.ks_company_id.id,
            'picking_type_id': self.ks_return_picking_type_id.id,
            'location_id': self.ks_picking_id.location_dest_id.id,
            'location_dest_id': self.ks_picking_id.location_id.id
        }
        stock_picking = stock_picking.create(stock_dict_sale)
        for rma_line in self.ks_rma_line_ids:
            if rma_line.ks_returned_qty:
                line_ids.append(self.env['stock.move'].create({
                    'name': rma_line.ks_product_id.name if rma_line.ks_product_id else '',
                    'product_id': rma_line.ks_product_id.id if rma_line.ks_product_id else False,
                    'product_uom_qty': rma_line.ks_returned_qty,
                    'picking_id': stock_picking.id,
                    'product_uom': rma_line.ks_product_id.uom_id.id if rma_line.ks_product_id else False,
                    'location_id': self.ks_picking_id.location_dest_id.id,
                    'location_dest_id': self.ks_picking_id.location_id.id
                }).id)
        return stock_picking

    # Prepare internal transfers on Rma form
    def _prepare_picking_internal(self):
        stock_picking = self.env['stock.picking']
        line_ids = []
        stock_dict_sale = {
            'ks_rma_id': self.id,
            'is_rma_out_picking': True,
            'state': 'assigned',
            'origin': self.ks_get_picking,
            'partner_id': self.ks_partner_id.id,
            'company_id': self.ks_company_id.id,
            'picking_type_id': self.ks_return_picking_type_id.id,
            'location_id': self.ks_picking_id.location_dest_id.id,
            'location_dest_id': self.ks_picking_id.location_id.id
        }
        stock_picking = stock_picking.create(stock_dict_sale)
        for rma_line in self.ks_rma_line_ids:
            if rma_line.ks_returned_qty:
                line_ids.append(self.env['stock.move'].create({
                    'name': rma_line.ks_product_id.name if rma_line.ks_product_id else '',
                    'product_id': rma_line.ks_product_id.id if rma_line.ks_product_id else False,
                    'product_uom_qty': rma_line.ks_returned_qty,
                    'picking_id': stock_picking.id,
                    'product_uom': rma_line.ks_product_id.uom_id.id if rma_line.ks_product_id else False,
                    'location_id': self.ks_picking_id.location_dest_id.id,
                    'location_dest_id': self.ks_picking_id.location_id.id
                }).id)
        return stock_picking

    # Action : To Return
    def action_ks_rma_return(self):
        if self.state in ['confirm', 'refunded'] and self.ks_selection == 'sale_order':
            stock_picking_record = self._prepare_picking_receipt()
            if stock_picking_record:
                self.ks_return_picking_id = stock_picking_record
                if self.state == 'refunded':
                    self.state = 'refund_return'

        if self.state in ['confirm', 'refunded'] and self.ks_selection == 'purchase_order':
            stock_picking_record = self._prepare_picking_order()
            if stock_picking_record:
                self.ks_return_picking_id = stock_picking_record
                if self.state == 'refunded':
                    self.state = 'refund_return'
        if self.state == 'confirm' and self.ks_selection == 'transfer':
            if self.ks_picking_id.picking_type_id.code == 'incoming':
                stock_picking_record = self._prepare_picking_order()
                if stock_picking_record:
                    self.ks_return_picking_id = stock_picking_record
            if self.ks_picking_id.picking_type_id.code == 'outgoing':
                stock_picking_record = self._prepare_picking_receipt()
                if stock_picking_record:
                    self.ks_return_picking_id = stock_picking_record
            if self.ks_picking_id.picking_type_id.code == 'internal':
                stock_picking_record = self._prepare_picking_internal()
                if stock_picking_record:
                    self.ks_return_picking_id = stock_picking_record

    # Create Refund for sale order
    def ks_sale_refund_invoice(self):
        invoice_state_list = self.ks_sale_order_id.invoice_ids.mapped('state')
        if 'posted' in invoice_state_list or 'paid' in invoice_state_list:
            line_list = []
            if self.ks_rma_line_ids:
                for rma_line in self.ks_rma_line_ids:
                    if rma_line.ks_refund_qty:
                        line_list.append(
                            (0, 0, {
                                'quantity': rma_line.ks_refund_qty,
                                'product_id': rma_line.ks_product_id.id,
                                'price_unit': rma_line.ks_price_unit,
                                'tax_ids': [(6, 0, rma_line.tax_ids.ids)],
                                'discount': rma_line.discount
                            }))
            refund_invoice_id = self.env['account.move'].create({
                'move_type': 'out_refund',
                'partner_id': self.ks_partner_id.id,
                'currency_id': self.ks_currency_id.id,
                'invoice_line_ids': line_list,
                'invoice_origin': self.ks_sale_order_id.name
            })
            if refund_invoice_id:
                for line in refund_invoice_id.invoice_line_ids:
                    line.name = line._get_computed_name()
                    line.account_id = line._get_computed_account()
                    line.product_uom_id = line._get_computed_uom()
                refund_invoice_id.action_post()
                return refund_invoice_id

    # Create Refund for purchase order
    def ks_purchase_refund_invoice(self):
        invoice_state_list = self.ks_purchase_order_id.invoice_ids.mapped('state')
        if 'posted' in invoice_state_list or 'paid' in invoice_state_list:
            line_list = []
            if self.ks_rma_line_ids:
                for rma_line in self.ks_rma_line_ids:
                    if rma_line.ks_refund_qty:
                        line_list.append(
                            (0, 0, {
                                'quantity': rma_line.ks_refund_qty,
                                'product_id': rma_line.ks_product_id.id,
                                'price_unit': rma_line.ks_price_unit,
                                'tax_ids': [(6, 0, rma_line.tax_ids.ids)],
                            }))
            refund_invoice_id = self.env['account.move'].create({
                'move_type': 'in_refund',
                'partner_id': self.ks_partner_id.id,
                'currency_id': self.ks_currency_id.id,
                'invoice_line_ids': line_list,
                'invoice_origin': self.ks_purchase_order_id.name
            })
            if refund_invoice_id:
                for line in refund_invoice_id.invoice_line_ids:
                    line.name = line._get_computed_name()
                    line.account_id = line._get_computed_account()
                    line.product_uom_id = line._get_computed_uom()
                refund_invoice_id.action_post()
                return refund_invoice_id

    # Return product lines Dic with product id as key
    def _return_invoice_line_product_qty_dict(self, parent_id):
        rma_product_qty = {}
        for line in parent_id.invoice_line_ids:
            if line.product_id:
                rma_product_qty[line.product_id.id] = line.quantity
        return rma_product_qty

    # Action : To Refund
    def action_ks_rma_refund(self):
        if self.ks_sale_order_id:
            if self.ks_sale_order_id.invoice_count:
                refund_invoice_id = self.ks_sale_refund_invoice()
                if refund_invoice_id:
                    self.ks_refund_invoice_id = refund_invoice_id[0]
                    if self.state == 'returned':
                        self.state = 'refund_return'
                    qty_dict = self._return_invoice_line_product_qty_dict(self.ks_refund_invoice_id)
                    for line in self.ks_sale_order_id.order_line:
                        if qty_dict.get(line.product_id.id, False):
                            if line.qty_invoiced:
                                line.qty_invoiced -= qty_dict[line.product_id.id]
            else:
                raise UserError(_('No Invoice Available!'))
        if self.ks_purchase_order_id:
            if self.ks_purchase_order_id.invoice_count:
                refund_invoice_id = self.ks_purchase_refund_invoice()
                if refund_invoice_id:
                    self.ks_refund_invoice_id = refund_invoice_id[0]
                    if self.state == 'returned':
                        self.state = 'refund_return'
                    qty_dict = self._return_invoice_line_product_qty_dict(self.ks_refund_invoice_id)
                    for line in self.ks_purchase_order_id.order_line:
                        if qty_dict.get(line.product_id.id, False):
                            if line.qty_invoiced:
                                line.qty_invoiced -= qty_dict[line.product_id.id]
            else:
                raise UserError(_('No Bill Available!'))

    # Action: open Refund invoice
    def action_view_refund_invoice(self):
        return {
            'name': _('Refund Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.ks_refund_invoice_id.id,
        }

    # Delivery order for replace
    def _prepare_picking_order_replace(self):
        stock_picking = self.env['stock.picking']
        line_ids = []
        stock_dict_sale = {
            'ks_rma_id': self.id,
            'is_rma_in_picking': True,
            'state': 'assigned',
            'origin': 3,
            'partner_id': self.ks_partner_id.id,
            'picking_type_id': self.ks_return_picking_type_id.id,
            'company_id': self.ks_company_id.id,
            'location_id': self.ks_picking_id.location_dest_id.id,
            'location_dest_id': self.ks_picking_id.location_id.id
        }
        stock_picking = stock_picking.create(stock_dict_sale)
        for rma_line in self.ks_rma_line_ids:
            if rma_line.ks_replace_qty:
                line_ids.append(self.env['stock.move'].create({
                    'name': rma_line.ks_product_id.name if rma_line.ks_product_id else '',
                    'product_id': rma_line.ks_product_id.id if rma_line.ks_product_id else False,
                    'product_uom_qty': rma_line.ks_replace_qty,
                    'picking_id': stock_picking.id,
                    'product_uom': rma_line.ks_product_id.uom_id.id if rma_line.ks_product_id else False,
                    'quantity_done': rma_line.ks_replace_qty,
                    'location_id': self.ks_picking_id.location_dest_id.id,
                    'location_dest_id': self.ks_picking_id.location_id.id
                }).id)
        return stock_picking

    def _preparing_another_picking_order_replace_(self):
        stock_picking = self.env['stock.picking']
        line_ids = []
        stock_dict_sale = {
            'ks_rma_id': self.id,
            'is_rma_in_picking': True,
            'state': 'assigned',
            'origin': 3,
            'partner_id': self.ks_partner_id.id,
            'picking_type_id': self.ks_picking_type_id.id,
            'company_id': self.ks_company_id.id,
            'location_id': self.ks_picking_id.location_id.id,
            'location_dest_id': self.ks_picking_id.location_dest_id.id
        }
        stock_picking = stock_picking.create(stock_dict_sale)
        for rma_line in self.ks_rma_line_ids:
            if rma_line.ks_replace_qty:
                line_ids.append(self.env['stock.move'].create({
                    'name': rma_line.ks_product_id.name if rma_line.ks_product_id else '',
                    'product_id': rma_line.ks_product_id.id if rma_line.ks_product_id else False,
                    'product_uom_qty': rma_line.ks_replace_qty,
                    'picking_id': stock_picking.id,
                    'product_uom': rma_line.ks_product_id.uom_id.id if rma_line.ks_product_id else False,
                    'quantity_done': rma_line.ks_replace_qty,
                    'location_id': self.ks_picking_id.location_id.id,
                    'location_dest_id': self.ks_picking_id.location_dest_id.id
                }).id)
        return stock_picking

    def action_ks_rma_replace(self):
        if self.state in ['confirm', 'replaced'] and self.ks_selection == 'sale_order':
            stock_picking_record = self._prepare_picking_order_replace()
            stock_picking_record_another = self._preparing_another_picking_order_replace_()
            if stock_picking_record and stock_picking_record_another:
                self.ks_return_picking_id = stock_picking_record
                self.ks_return_picking_id.state = 'done'
                self.ks_picking_id_replace = stock_picking_record_another
                self.ks_picking_id_replace.state = 'done'
                self.state = 'replaced'
        if self.state in ['confirm', 'replaced'] and self.ks_selection == 'purchase_order':
            stock_picking_record = self._prepare_picking_order_replace()
            stock_picking_record_another = self._preparing_another_picking_order_replace_()
            if stock_picking_record and stock_picking_record_another:
                self.ks_return_picking_id = stock_picking_record
                self.ks_return_picking_id.state = 'done'
                self.ks_picking_id_replace = stock_picking_record_another
                self.ks_picking_id_replace.state = 'done'
                self.state = 'replaced'

    def _compute_access_url(self):
        for record in self:
            record.access_url = '/my/rmas/{}'.format(record.id)

    def ks_action_preview(self):
        """Invoked when 'Preview' button in rma form view is clicked."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'RMA Report - %s' % self.ks_sequence_code


class KsRmaMail(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        ks_current_rma = self.env['ks.rma'].search([('ks_sequence_code', '=', self.record_name)])
        ks_current_rma.write({'state': 'sent'})
        return super(KsRmaMail, self).action_send_mail()
