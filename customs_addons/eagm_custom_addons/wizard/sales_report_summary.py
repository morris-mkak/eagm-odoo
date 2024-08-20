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


class SalesReportSummary(models.TransientModel):
    _name = "sales.report.summary"
    _description = 'Sales Report Summary'

    date_from = fields.Date(string='From', required=True,
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)))
    date_to = fields.Date(string='To', required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(
                                  months=+1,
                                  day=1,
                                  days=-1)).date()))
    product_category_id = fields.Many2one('product.category', required=True)
    loan_summary_file = fields.Binary('Sales Report Summary')
    file_name = fields.Char('File Name')
    sale_summary_report_printed = fields.Boolean(
        'Sales Summary Report Printed')

    def action_print_sales_summary_report(self):
        workbook = xlwt.Workbook(style_compression=2)
        column_heading_style = easyxf(
            'font:height 200;font:bold True;align: horiz left;')
        worksheet = workbook.add_sheet('Sales Report Summary',
                                       cell_overwrite_ok=True)
        worksheet.write(2, 0, _('Dates'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 1, _('No of Sales orders'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 2, _('No of Invoices'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 3, _("No of CN's"), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 4, _('Sales order value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 5, _('Invoice Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 6, _('CN Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 7, _('Net Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 8, _('Invoice GP Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 9, _('CN GP Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 10, _('Net GP Value'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 11, _('Invoice GP %'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 12, _('CN GP %'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
        worksheet.write(2, 13, _('Net GP %'), easyxf(
                                        'font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))

        worksheet.col(0).width = 3000
        worksheet.col(1).width = 3000
        worksheet.col(2).width = 5000
        worksheet.col(4).width = 5000
        row = 3
        row1 = row + 1
        row2 = row1 + 2
        loan_bal = 0
        new_loan = 0
        repaid_loan = 0
        loan_bal_two = 0
        interest_rate = 0
        prescribed_rate = 0
        interest_amount = 0
        fringe_tax = 0
        for wizard in self:
            sales_summary_objs = self.env['sale.order'].search(
                    [('date_order', '>=', wizard.date_from),
                     ('date_order', '<=', wizard.date_to),
                     ])
            if sales_summary_objs:
                worksheet.write(row1 + len(sales_summary_objs), 0,
                                _(' TOTALS : '),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 0,
                                _('Industry'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 1,
                                _('Sales Target'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 2,
                                _('Sales Achived'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 3,
                                _('%'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 4,
                                _('GP Target'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 5,
                                _('GP Achvied'),
                                column_heading_style)
                worksheet.write(row2 + len(sales_summary_objs), 5,
                                _('%'),
                                column_heading_style)
                for obj in sales_summary_objs:
                    loan_bal += 1
                    new_loan += 1
                    repaid_loan += 1
                    loan_bal_two += 1
                    interest_rate += 1
                    prescribed_rate += 1
                    interest_amount += 1
                    fringe_tax += 1
                    heading = obj.company_id.name
                    heading_1 = 'Daily Sales Summary Report'
                    worksheet.write_merge(0, 0, 0, 13, heading, column_heading_style)
                    worksheet.write_merge(1, 1, 0, 13, heading_1,
                                          easyxf(
                                              'font:height 200;font:bold True;align: horiz center;'))
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
                    worksheet.write(row, 8,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 9,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 10,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 11,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 12,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    worksheet.write(row, 13,
                                    '0' or '',
                                    easyxf(
                                        'font:height 200;align: horiz left;'))
                    row += 1
                    worksheet.write(row1 + len(sales_summary_objs), 1,
                                    new_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 2,
                                    repaid_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 3,
                                    loan_bal,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 4,
                                    new_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 5,
                                    repaid_loan,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 6,
                                    loan_bal_two,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 7,
                                    interest_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 8,
                                    prescribed_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 9,
                                    interest_amount,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 10,
                                    fringe_tax,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 11,
                                    interest_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 12,
                                    prescribed_rate,
                                    column_heading_style)
                    worksheet.write(row1 + len(sales_summary_objs), 13,
                                    interest_amount,
                                    column_heading_style)
            else:
                raise ValidationError(_('No Records Found'))

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodebytes(fp.getvalue())
        wizard.loan_summary_file = excel_file
        wizard.file_name = 'SalesReportSummary_' + fields.Datetime.context_timestamp(
            self, fields.Datetime.now()).strftime(
            '%Y_%m_%d_%H%M%S') + '.xlsx'
        wizard.sale_summary_report_printed = True
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': wizard.id,
            'res_model': 'sales.report.summary',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
        }
