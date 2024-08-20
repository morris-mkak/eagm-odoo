from odoo import tools
from odoo import api, fields, models


class KsRmaReport(models.Model):
    _name = "ks.rma.report"
    _description = "RMA Analysis Report"
    _auto = False
    _rec_name = 'ks_date_requested'
    _order = 'ks_date_requested desc'

    ks_sequence_code = fields.Char(string="RMA Number", readonly=True)
    ks_partner_id = fields.Many2one(comodel_name="res.partner", string="Partner",
                                    readonly=True)
    ks_picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking",
                                    readonly=True)
    ks_selection = fields.Selection([('sale_order', 'Sale Order'), ('purchase_order', 'Purchase Order'),
                                     ('transfer', 'Transfer')], string="Sale/Purchase/Transfer",
                                    readonly=True)
    ks_sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order",
                                       readonly=True)
    ks_purchase_order_id = fields.Many2one(comodel_name="purchase.order", string="Purchase Order",
                                           readonly=True)
    ks_team_id = fields.Many2one(comodel_name="crm.team", string="Assigned Team",
                                 readonly=True)
    ks_user_id = fields.Many2one(comodel_name="res.users", string="Assigned Person",
                                 readonly=True)
    ks_company_id = fields.Many2one(comodel_name="res.company", string="Company",
                                    readonly=True)
    ks_warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse",
                                      readonly=True)
    ks_currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", readonly=True)
    ks_confirmed_user_id = fields.Many2one(comodel_name="res.users", string="Confirmed By",
                                           readonly=True)
    ks_date_requested = fields.Date(string="Requested Date", readonly=True)
    ks_date_closed = fields.Date(string="Closed Date", readonly=True)
    ks_date_confirmed = fields.Date(string="Confirmation Date", readonly=True)
    ks_date_cancelled = fields.Date(string="Cancel Date", readonly=True)
    state = fields.Selection(([('draft', 'Draft'), ('sent', 'Sent'), ('confirm', 'Confirmed'),
                               ('cancel', 'Cancelled'), ("refunded", "Refund"), ("returned", "Return"),
                               ("replaced", "Replace"), ('refund_return', 'Refund+Return'),
                               ('closed', 'Closed')]), string="State", readonly=True)
    ks_refund_invoice_id = fields.Many2one('account.move', string='Refund', readonly=True)
    ks_return_picking_id = fields.Many2one('stock.picking', string='Return Picking', readonly=True)
    ks_is_refund = fields.Boolean(string='Is Refund', readonly=True)
    ks_is_return = fields.Boolean(string='Is Return', readonly=True)
    ks_rma_id = fields.Many2one(comodel_name="ks.rma", string="RMA", readonly=True)
    ks_product_id = fields.Many2one(comodel_name="product.product", string="Product", readonly=True)
    ks_returned_qty = fields.Integer(string="Return Quantity", readonly=True)
    ks_refund_qty = fields.Integer(string="Refund Quantity", readonly=True)
    ks_refund_amount = fields.Float(string="Refund Amount")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
               min(l.id) as id,
               l.ks_product_id as ks_product_id,
               l.ks_rma_id as ks_rma_id,
               t.uom_id as product_uom,
               s.ks_picking_id as ks_picking_id,
               s.ks_currency_id as ks_currency_id,
               s.ks_date_closed as ks_date_closed,
               s.ks_warehouse_id as ks_warehouse_id,
               s.ks_date_cancelled as ks_date_cancelled,
               sum(l.ks_returned_qty) as ks_returned_qty,
               sum(l.ks_refund_qty) as ks_refund_qty,
               sum(s.ks_store_refund_amount) as ks_refund_amount,
               count(*) as nbr,
               s.ks_sequence_code as ks_sequence_code,
               s.ks_date_requested as ks_date_requested,
               s.state as state,
               s.ks_refund_invoice_id as ks_refund_invoice_id,
               s.ks_confirmed_user_id as ks_confirmed_user_id,
               s.ks_selection as ks_selection,
               s.ks_sale_order_id as ks_sale_order_id,
               s.ks_purchase_order_id as ks_purchase_order_id,
               s.ks_date_confirmed as ks_date_confirmed,
               s.ks_is_refund as ks_is_refund,
               s.ks_is_return as ks_is_return,
               s.ks_return_picking_id as ks_return_picking_id,
               s.ks_partner_id as ks_partner_id,
               s.ks_user_id as ks_user_id,
               s.ks_company_id as ks_company_id,
               extract(epoch from avg(date_trunc('day',s.ks_date_requested)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
               s.ks_team_id as ks_team_id,
               p.product_tmpl_id,
               partner.commercial_partner_id as commercial_partner_id,
               s.id as order_id
           """

        for field in fields.values():
            select_ += field

        from_ = """
                   ks_rma_line l
                         join ks_rma s on (l.ks_rma_id=s.id)
                         join res_partner partner on s.ks_partner_id = partner.id
                           left join product_product p on (l.ks_product_id=p.id)
                               left join product_template t on (p.product_tmpl_id=t.id)
                       left join uom_uom u2 on (u2.id=t.uom_id)
                   %s
           """ % from_clause

        groupby_ = """
               l.ks_product_id,
               l.ks_rma_id,
               t.uom_id,
               s.ks_sequence_code,
               s.ks_date_requested,
               s.ks_partner_id,
               s.ks_user_id,
               s.state,
               s.ks_company_id,
               s.ks_team_id,
               p.product_tmpl_id,
               partner.country_id,
               partner.industry_id,
               partner.commercial_partner_id,
               s.id %s
           """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE l.ks_product_id IS NOT NULL GROUP BY %s)' % (
        with_, select_, from_, groupby_)

    def init(self):
        # self._table = ks_rma_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
