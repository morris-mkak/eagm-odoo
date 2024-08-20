# -*- coding: utf-8 -*-
# Copyright 2021 Dishon Kadoh <http://dishonkadoh.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, _
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf
from odoo.exceptions import ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class BrandReportSummary(models.TransientModel):
    _name = "brand.report.summary"
    _description = 'Brand Report Summary'

    date_from = fields.Date(string='From', required=True,
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)))
    date_to = fields.Date(string='To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(
                                  months=+1,
                                  day=1,
                                  days=-1)).date()))
    loan_summary_file = fields.Binary('Brand Report Summary')
    file_name = fields.Char('File Name')
    brand_summary_report_printed = fields.Boolean(
        'Brand Summary Report Printed')

    def action_print_brand_summary_report(self):
        workbook = xlwt.Workbook(style_compression=2)
        column_heading_style = easyxf(
            'font:height 200;font:bold True;align: horiz left;')
        worksheet = workbook.add_sheet('Brand Report Summary',
                                       cell_overwrite_ok=True)
        worksheet.write(0, 0, _('Brand'), easyxf(
            'font:height 200;font:bold True;align: horiz left;'))
        worksheet.write(0, 1, _('Qty in Ctns'), easyxf(
            'font:height 200;font:bold True;align: horiz left;'))
        worksheet.write(0, 2, _('Qty in Inners'), easyxf(
            'font:height 200;font:bold True;align: horiz left;'))
        worksheet.write(0, 3, _('Qty in Pcs'), easyxf(
            'font:height 200;font:bold True;align: horiz left;'))
        worksheet.write(0, 4, _('Sales Value'), easyxf(
            'font:height 200;font:bold True;align: horiz left;'))
        worksheet.write(0, 5, _('% Contribution'), column_heading_style)
        worksheet.write(0, 6, _('GPValue'), column_heading_style)
        worksheet.write(0, 7, _('% GP'), column_heading_style)


        worksheet.col(0).width = 3000
        worksheet.col(1).width = 3000
        worksheet.col(2).width = 5000
        worksheet.col(4).width = 5000
        row = 1
        row1 = row + 1
        loan_bal = 0
        new_loan = 0
        repaid_loan = 0
        loan_bal_two = 0
        interest_rate = 0
        prescribed_rate = 0
        interest_amount = 0
        fringe_tax = 0
        for wizard in self:
            brand_summary_objs = self.env['sale.order'].search(
                    [('date_order', '>=', wizard.date_from),
                     ('date_order', '<=', wizard.date_to),
                     ])
            if brand_summary_objs:
                worksheet.write(row1 + len(brand_summary_objs), 0,
                                _(' TOTALS : '),
                                column_heading_style)
                for obj in brand_summary_objs:
                    loan_bal += 1
                    new_loan += 1
                    repaid_loan += 1
                    loan_bal_two += 1
                    interest_rate += 1
                    prescribed_rate += 1
                    interest_amount += 1
                    fringe_tax += 1
                    worksheet.write(row, 0,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 1,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 2,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 3,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 4,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 5,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 6,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 7,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    row += 1
                    worksheet.write(row1 + len(brand_summary_objs), 1,
                                    loan_bal,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 2,
                                    new_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 3,
                                    repaid_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 4,
                                    loan_bal_two,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 5,
                                    interest_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 6,
                                    prescribed_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(brand_summary_objs), 7,
                                    interest_amount,
                                    column_heading_style)
            else:
                raise ValidationError(_('No Records Found'))

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodebytes(fp.getvalue())
        wizard.loan_summary_file = excel_file
        wizard.file_name = 'BrandReportSummary_' + fields.Datetime.context_timestamp(
            self, fields.Datetime.now()).strftime(
            '%Y_%m_%d_%H%M%S') + '.xlsx'
        wizard.brand_summary_report_printed = True
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': wizard.id,
            'res_model': 'brand.report.summary',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
