# -*- coding: utf-8 -*-
from odoo import http


class PurchaseEdifact(http.Controller):
    @http.route('/purchase_edifact/purchase_order/<int:id>', type='http', auth='public')
    def download_file(self, id, **kwargs):
        my_record = http.request.env['purchase.order'].browse(id)
        file_content = my_record.edifact_file
        file_name = my_record.edifact_file_name
        return http.request.make_response(
            file_content,
            [('Content-Type', 'application/octet-stream'), ('Content-Disposition', 'attachment; filename="%s"' % file_name)])


