# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    subscription_management = fields.Selection(string='Subscription Management', selection=[('create', 'Creation'), ('renew', 'Renewal'), ('upsell', 'Upselling')],
                                               default='create',
                                               help="Creation: The Sales Order created the subscription\n"
                                                    "Upselling: The Sales Order added lines to the subscription\n"
                                                    "Renewal: The Sales Order replaced the subscription's content with its own")
    subscription_count = fields.Integer(compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        """Compute the number of distinct subscriptions linked to the order."""
        for order in self:
            sub_count = len(self.env['sale.order.line'].read_group([('order_id', '=', order.id), ('subscription_id', '!=', False)],
                                                    ['subscription_id'], ['subscription_id']))
            order.subscription_count = sub_count

    def action_open_subscriptions(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        subscriptions = self.order_line.mapped('subscription_id')
        action = self.env["ir.actions.actions"]._for_xml_id("sale_subscription.sale_subscription_action")
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        elif len(subscriptions) == 1:
            form_view = [(self.env.ref('sale_subscription.sale_subscription_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subscriptions.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['context'] = dict(self._context, create=False)
        return action

    def action_draft(self):
        if any(order.state == 'cancel' and any(line.subscription_id for line in order.order_line) for order in self):
            raise UserError(_('You cannot set to draft a canceled quotation linked to subscriptions. Please create a new quotation.'))
        return super(SaleOrder, self).action_draft()

    def _prepare_subscription_data(self, template):
        """Prepare a dictionnary of values to create a subscription from a template."""
        self.ensure_one()
        date_today = fields.Date.context_today(self)
        recurring_invoice_day = date_today.day
        recurring_next_date = self.env['sale.subscription']._get_recurring_next_date(
            template.recurring_rule_type, template.recurring_interval,
            date_today, recurring_invoice_day
        )
        values = {
            'name': template.name,
            'template_id': template.id,
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'payment_term_id': self.payment_term_id.id,
            'date_start': fields.Date.context_today(self),
            'description': self.note or template.description,
            'pricelist_id': self.pricelist_id.id,
            'company_id': self.company_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'recurring_next_date': recurring_next_date,
            'recurring_invoice_day': recurring_invoice_day,
            'payment_token_id': self.transaction_ids.get_last_transaction().payment_token_id.id if template.payment_mode in ['validate_send_payment', 'success_payment'] else False
        }
        default_stage = self.env['sale.subscription.stage'].search([('category', '=', 'progress')], limit=1)
        if default_stage:
            values['stage_id'] = default_stage.id
        return values

    def update_existing_subscriptions(self):
        """
        Update subscriptions already linked to the order by updating or creating lines.

        :rtype: list(integer)
        :return: ids of modified subscriptions
        """
        res = []
        deleted_product_ids = None
        for order in self:
            subscriptions = order.order_line.mapped('subscription_id').sudo()
            if subscriptions and order.subscription_management != 'renew':
                order.subscription_management = 'upsell'
            res.append(subscriptions.ids)
            if order.subscription_management == 'renew':
                subscriptions.wipe()
                subscriptions.increment_period(renew=True)
                subscriptions.payment_term_id = order.payment_term_id
                subscriptions.set_open()
                # Some products of the subscription may be missing from the SO: they can be archived or manually removed from the SO.
                # we delete the recurring line of these subscriptions
                deleted_product_ids = subscriptions.mapped(
                    'recurring_invoice_line_ids.product_id') - order.order_line.mapped('product_id')
            for subscription in subscriptions:
                subscription_lines = order.order_line.filtered(lambda l: l.subscription_id == subscription and l.product_id.recurring_invoice)
                line_values = subscription_lines._update_subscription_line_data(subscription)
                subscription.write({'recurring_invoice_line_ids': line_values})
        return res

    def create_subscriptions(self):
        """
        Create subscriptions based on the products' subscription template.

        Create subscriptions based on the templates found on order lines' products. Note that only
        lines not already linked to a subscription are processed; one subscription is created per
        distinct subscription template found.

        :rtype: list(integer)
        :return: ids of newly create subscriptions
        """
        res = []
        for order in self:
            to_create = order._split_subscription_lines()
            # create a subscription for each template with all the necessary lines
            for template in to_create:
                values = order._prepare_subscription_data(template)
                values['recurring_invoice_line_ids'] = to_create[template]._prepare_subscription_line_data()
                subscription = self.env['sale.subscription'].sudo().create(values)
                subscription.onchange_date_start()
                res.append(subscription.id)
                to_create[template].write({'subscription_id': subscription.id})
                subscription.message_post_with_view(
                    'mail.message_origin_link', values={'self': subscription, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
                )
                self.env['sale.subscription.log'].sudo().create({
                    'subscription_id': subscription.id,
                    'event_date': fields.Date.context_today(self),
                    'event_type': '0_creation',
                    'amount_signed': subscription.recurring_monthly,
                    'recurring_monthly': subscription.recurring_monthly,
                    'currency_id': subscription.currency_id.id,
                    'category': subscription.stage_category,
                    'user_id': order.user_id.id,
                    'team_id': order.team_id.id,
                })
        return res

    def _split_subscription_lines(self):
        """Split the order line according to subscription templates that must be created."""
        self.ensure_one()
        res = dict()
        new_sub_lines = self.order_line.filtered(lambda l: not l.subscription_id and l.product_id.subscription_template_id and l.product_id.recurring_invoice)
        templates = new_sub_lines.mapped('product_id').mapped('subscription_template_id')
        for template in templates:
            lines = self.order_line.filtered(lambda l: l.product_id.subscription_template_id == template and l.product_id.recurring_invoice)
            res[template] = lines
        return res

    def _action_confirm(self):
        """Update and/or create subscriptions on order confirmation."""
        res = super(SaleOrder, self)._action_confirm()
        self.update_existing_subscriptions()
        self.create_subscriptions()
        return res

    def _get_payment_type(self, tokenize=False):
        contains_subscription = any(line.product_id.recurring_invoice for line in self.sudo().order_line)
        return super()._get_payment_type(tokenize=contains_subscription or tokenize)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    subscription_id = fields.Many2one('sale.subscription', 'Subscription', copy=False, check_company=True)

    def _prepare_invoice_line(self, **optional_values):
        """
        Override to add subscription-specific behaviours.

        Display the invoicing period in the invoice line description, link the invoice line to the
        correct subscription and to the subscription's analytic account if present, add revenue dates.
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)  # <-- ensure_one()
        if self.subscription_id:
            res.update(subscription_id=self.subscription_id.id)
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            next_date = self.subscription_id.recurring_next_date
            previous_date = next_date - relativedelta(**{periods[self.subscription_id.recurring_rule_type]: self.subscription_id.recurring_interval})
            is_already_period_msg = False
            if self.order_id.subscription_management != 'upsell':  # renewal or creation: one entire period
                date_start = previous_date
                date_start_display = previous_date
                date_end = next_date - relativedelta(days=1)  # the period does not include the next renewal date
            else:  # upsell: pro-rated period
                date_start, date_start_display, date_end = None, None, None
                try:
                    regexp = r"\[(\d{4}-\d{2}-\d{2}) -> (\d{4}-\d{2}-\d{2})\]"
                    match = re.search(regexp, self.name)
                    date_start = fields.Date.from_string(match.group(1))
                    date_start_display = date_start
                    date_end = fields.Date.from_string(match.group(2))
                except Exception:
                    _logger.error('_prepare_invoice_line: unable to compute invoicing period for %r - "%s"', self, self.name)
                    # Fallback on discount
                if not date_start or not date_start_display or not date_end:
                    # here we have a slight problem: the date used to compute the pro-rated discount
                    # (that is, the date_from in the upsell wizard) is not stored on the line,
                    # preventing an exact computation of start and end revenue dates
                    # witness me as I try to retroengineer the ~correct dates 🙆‍
                    # (based on `partial_recurring_invoice_ratio` from the sale.subscription model)
                    total_days = (next_date - previous_date).days
                    days = round((1 - self.discount / 100.0) * total_days)
                    date_start = next_date - relativedelta(days=days+1)
                    date_start_display = next_date - relativedelta(days=days)
                    date_end = next_date - relativedelta(days=1)
                else:
                    is_already_period_msg = True
            if not is_already_period_msg:
                lang = self.order_id.partner_invoice_id.lang
                format_date = self.env['ir.qweb.field.date'].with_context(lang=lang).value_to_html
                # Ugly workaround to display the description in the correct language
                if lang:
                    self = self.with_context(lang=lang)
                period_msg = _("Invoicing period") + ": [%s -> %s]" % (fields.Date.to_string(date_start_display), fields.Date.to_string(date_end))
                res.update({
                    'name': res['name'] + '\n' + period_msg,
                })
            res.update({
                'subscription_start_date': date_start,
                'subscription_end_date': date_end,
            })
            if self.subscription_id.analytic_account_id:
                res['analytic_account_id'] = self.subscription_id.analytic_account_id.id
        return res

    @api.model
    def create(self, vals):
        """Set the correct subscription on lines at creation for upsell/renewal quotes."""
        if vals.get('order_id'):
            order = self.env['sale.order'].browse(vals['order_id'])
            Product = self.env['product.product']
            if order.origin and order.subscription_management in ('upsell', 'renew') and Product.browse(vals['product_id']).recurring_invoice:
                vals['subscription_id'] = (
                    self.env['sale.subscription'].search(['&', ('code', '=', order.origin), ('partner_id', '=', order.partner_id.id)], limit=1).id
                    or self.env['sale.subscription'].search([('code', '=', order.origin)], limit=1).id
                )
        return super(SaleOrderLine, self).create(vals)

    def _prepare_subscription_line_data(self):
        """Prepare a dictionnary of values to add lines to a subscription."""
        values = list()
        for line in self:
            values.append((0, False, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'uom_id': line.product_uom.id,
                'price_unit': line.price_unit,
                'discount': line.discount if line.order_id.subscription_management != 'upsell' else False,
            }))
        return values

    def _update_subscription_line_data(self, subscription):
        """Prepare a dictionnary of values to add or update lines on a subscription."""
        values = list()
        dict_changes = dict()
        for line in self:
            sub_line = subscription.recurring_invoice_line_ids.filtered(
                lambda l: (l.product_id, l.uom_id, l.price_unit) == (line.product_id, line.product_uom, line.price_unit)
            )
            if sub_line:
                # We have already a subscription line, we need to modify the product quantity
                if len(sub_line) > 1:
                    # we are in an ambiguous case
                    # to avoid adding information to a random line, in that case we create a new line
                    # we can simply duplicate an arbitrary line to that effect
                    sub_line[0].copy({'name': line.display_name, 'quantity': line.product_uom_qty})
                else:
                    dict_changes.setdefault(sub_line.id, sub_line.quantity)
                    # upsell, we add the product to the existing quantity
                    dict_changes[sub_line.id] += line.product_uom_qty
            else:
                # we create a new line in the subscription: (0, 0, values)
                values.append(line._prepare_subscription_line_data()[0])

        values += [(1, sub_id, {'quantity': dict_changes[sub_id]}) for sub_id in dict_changes]
        return values
