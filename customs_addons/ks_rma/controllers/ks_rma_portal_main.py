from odoo import _, exceptions, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import consteq


class KsPortalRma(CustomerPortal):

    def _ks_is_rma_portal_access(self):
        return request.env['ir.config_parameter'].sudo().get_param('ks_rma.is_rma_portal_access')

    def _prepare_portal_layout_values(self):
        values = super(KsPortalRma, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('ks_selection', '=', 'sale_order')
        ]
        values['rma_count'] = request.env['ks.rma'].search_count(domain)
        values['rma_portal_access'] = self._ks_is_rma_portal_access()
        return values

    def _rma_get_page_view_values(self, rma, access_token, **kwargs):
        values = {
            'page_name': 'RMA',
            'rma': rma,
        }
        return self._get_page_view_values(
            rma, access_token, values, 'my_rmas_history', False, **kwargs)

    def _get_filter_domain(self, kw):
        partner = request.env.user.partner_id
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]), ('ks_selection', '=', 'sale_order')
        ]
        return domain

    @http.route(['/my/rmas', '/my/rmas/page/<int:page>'],
                type='http', auth="user", website=True)
    def ks_portal_my_rmas(self, page=1, date_begin=None, date_end=None, sortby=None, domain=None, **kw):
        res = self._ks_is_rma_portal_access()
        if res:
            values = self._prepare_portal_layout_values()
            domain = self._get_filter_domain(kw)
            rma_obj = request.env['ks.rma']
            searchbar_sortings = {
                'ks_date_confirmed': {'label': _('Date'), 'order': 'ks_date_confirmed desc'},
                'ks_sequence_code': {'label': _('Name'), 'order': 'ks_sequence_code desc'},
                'state': {'label': _('Status'), 'order': 'state'},
            }
            # default sort by order
            if not sortby:
                sortby = 'ks_date_confirmed'
            order = searchbar_sortings[sortby]['order']
            # archive_groups = self._get_archive_groups('ks.rma', [])
            if date_begin and date_end:
                domain += [
                    ('create_date', '>', date_begin),
                    ('create_date', '<=', date_end),
                ]
            # count for pager
            rma_count = rma_obj.search_count(domain)
            # pager
            pager = portal_pager(
                url="/my/rmas",
                url_args={
                    'date_begin': date_begin,
                    'date_end': date_end,
                    'sortby': sortby,
                },
                total=rma_count,
                page=page,
                step=self._items_per_page
            )
            # content according to pager and archive selected
            rmas = rma_obj.search(
                domain,
                order=order,
                limit=self._items_per_page,
                offset=pager['offset']
            )
            # request.session['my_rmas_history'] = rmas.ids[:100]
            values.update({
                'date': date_begin,
                'rmas': rmas,
                'page_name': 'RMA',
                'pager': pager,
                # 'archive_groups': archive_groups,
                'default_url': '/my/rmas',
                'searchbar_sortings': searchbar_sortings,
                'sortby': sortby,
            })
            return request.render("ks_rma.ks_portal_my_rmas", values)

    @http.route(['/my/rmas/<int:rma_id>'],
                type='http', auth="public", website=True)
    def ks_portal_my_rma_detail(self, rma_id, access_token=None,
                                report_type=None, download=False, **kw):
        res = self._ks_is_rma_portal_access()
        if res:
            try:
                rma_sudo = self._document_check_access('ks.rma', rma_id, access_token)
            except (AccessError, MissingError):
                return request.redirect('/my')
            if report_type in ('html', 'pdf', 'text'):
                return self._show_report(
                    model=rma_sudo,
                    report_type=report_type,
                    report_ref='ks_rma.report_rma_action',
                    download=download,
                )

            values = self._rma_get_page_view_values(rma_sudo, access_token, **kw)
            return request.render("ks_rma.ks_portal_rma_page", values)

    @http.route(['/my/rma/picking/pdf/<int:rma_id>/<int:picking_id>'],
                type='http', auth="public", website=True)
    def ks_portal_my_rma_picking_report(self, ks_rma_id, ks_picking_id,
                                        access_token=None, **kw):
        try:
            ks_picking = self.ks_picking_check_access(
                ks_rma_id, ks_picking_id, access_token=access_token)
        except exceptions.AccessError:
            return request.redirect('/my')
        ks_report_sudo = request.env.ref('stock.action_report_delivery').sudo()
        ks_pdf = ks_report_sudo.render_qweb_pdf([ks_picking.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(ks_pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    def ks_picking_check_access(self, ks_rma_id, ks_picking_id, access_token=None):
        ks_rma = request.env['ks.rma'].browse([ks_rma_id])
        ks_picking_sudo = request.env['stock.picking'].sudo().browse([ks_picking_id])
        try:
            ks_picking_sudo.check_access_rights('read')
            ks_picking_sudo.check_access_rule('read')
        except exceptions.AccessError:
            if not access_token or not consteq(ks_rma.access_token, access_token):
                raise
        return ks_picking_sudo
