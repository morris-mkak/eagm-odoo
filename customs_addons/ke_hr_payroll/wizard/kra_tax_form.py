# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import xlwt
from io import BytesIO
import base64
from xlwt import easyxf
import datetime
from odoo.exceptions import ValidationError
from PIL import Image
import re
import os


class MonthlyP9Wizard(models.TransientModel):
    _name = 'monthly.p9.wizard'
    _description = 'Monthly P9 Wizard'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string='To Date', required=True)
    p9_file = fields.Binary('KRA P9 Form')
    file_name = fields.Char('File Name')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    p9_printed = fields.Boolean('KRA P9 Form Printed')
    individual_employee = fields.Boolean('Individual Printed Employee',default=True)

    def print_p9_xls_report(self):
        # current_working_dir = os.getcwd()
        # abs_pathname = os.path.join(current_working_dir, "custom_addons/ke_hr_payroll.static/description/kra.png")
        # img = Image.open(abs_pathname).convert('RGB')
        # image_parts = img.split()
        # r = image_parts[0]
        # g = image_parts[1]
        # b = image_parts[2]
        # new_image = Image.merge("RGB", (r, g, b,))
        # new_image.save('kra.bmp')
        for wizard in self:
            if wizard.individual_employee:
                row = 16
                row2 = 16
                row3 = 16
                row4 = 16
                row5 = 16
                row6 = 16
                row7 = 16
                row8 = 16
                row9 = 16
                total_gross_pay = 0
                total_gross_taxable_pay = 0
                total_net_taxable_pay = 0
                nssf = 0
                paye = 0
                tax_relief = 0
                net_paye = 0
                non_cash_allowances = 0
                payslip_objs = self.env['hr.payslip'].search([
                    ('date_from', '>=', wizard.from_date),
                    ('employee_id', '=', wizard.employee_id.id),
                    ('date_to', '<=', wizard.to_date), ])
                employers_kra_id = self.env['res.config.settings'].search([])
                for employees in payslip_objs:
                    print(employees.employee_id.name)
                workbook = xlwt.Workbook()
                column_heading_style = easyxf(
                    'font:height 200;font:bold True;font: color black;')
                center_heading_style = easyxf(
                    'font:height 200; align: horiz center;font:bold True;font: color black;')
                worksheet = workbook.add_sheet(wizard.employee_id.name,
                                               cell_overwrite_ok=True)
                for rec in employers_kra_id:
                    worksheet.write(7, 9, rec.employer_kra, easyxf(
                        'font:height 200;font:bold True;'))
                filename_nhif = 'KRA P9 For-' + re.sub(
                    '[^A-Za-z0-9]+', '',
                    wizard.employee_id.name) + '_' + fields.Datetime.context_timestamp(
                    self, fields.datetime.now()).strftime(
                    '%Y_%m_%d-%H%M%S')
                worksheet.write(5, 1, self.env.user.company_id.name, easyxf(
                    'font:height 200;font:bold True;'))
                worksheet.write(3, 0, _('P9A'), column_heading_style)
                worksheet.write(5, 0, _('Employers Name'), column_heading_style)
                worksheet.write(6, 5, _('DOMESTIC TAXES DEPARTMENT'), easyxf(
                    'font:height 250;font:bold True;'))
                worksheet.write(7, 0, _('Employees Main Name'),
                                column_heading_style)
                worksheet.write(7, 8, _('Employers PIN:'),
                                column_heading_style)
                worksheet.write(9, 0, _('Employees Other Names'),
                                column_heading_style)
                worksheet.write(9, 8, _('Employees PIN:'),
                                column_heading_style)
                worksheet.write_merge(12, 14, 0, 0, _('MONTH'),
                                      column_heading_style)
                worksheet.write(12, 1, _('Basic Salary'), column_heading_style)
                worksheet.write(12, 2, _('Benefits Non Cash'),
                                column_heading_style)
                worksheet.write(12, 3, _('Value of Quarters'),
                                column_heading_style)
                worksheet.write(12, 4, _('Total Gross pay'),
                                column_heading_style)
                worksheet.write_merge(12, 12, 5, 7, _('Defined Contribution Retirement Scheme'),
                                      column_heading_style)
                worksheet.write_merge(13, 13, 5, 7, _('E'),
                                      column_heading_style)
                worksheet.write(14, 5, _('E1 30% of A'),
                                column_heading_style)
                worksheet.write(14, 6, _('E2 Actual'),
                                column_heading_style)
                worksheet.write(14, 7, _('E3 fixed'),
                                column_heading_style)
                worksheet.write(12, 8, _('Owner Occupier Interest'),
                                column_heading_style)
                worksheet.write(14, 8, _('Amount of interest'),
                                column_heading_style)
                worksheet.write(12, 9, _('Retirement Contribution & Owner Occupier Interest'),
                                column_heading_style)
                worksheet.write(14, 9, _('Occupied Interest(The lowest of E added to F)'),
                                column_heading_style)
                worksheet.write(12, 10, _('Chargeable Pay'),
                                column_heading_style)
                worksheet.write(12, 11, _('Tax Charged'), column_heading_style)
                worksheet.write(12, 12, _('Personal Relief + Insurnace Relief'),
                                column_heading_style)
                worksheet.write(12, 13, _('PAYE Tax (J-K)'),
                                column_heading_style)
                worksheet.write(15, 1, _('Kshs.'), center_heading_style)
                worksheet.write(15, 2, _('Kshs.'), center_heading_style)
                worksheet.write(15, 3, _('Kshs.'), center_heading_style)
                worksheet.write(15, 4, _('Kshs.'), center_heading_style)
                worksheet.write(15, 5, _('Kshs.'), center_heading_style)
                worksheet.write(15, 6, _('Kshs.'), center_heading_style)
                worksheet.write(15, 7, _('Kshs.'), center_heading_style)
                worksheet.write(15, 8, _('Kshs.'), center_heading_style)
                worksheet.write(15, 9, _('Kshs.'), center_heading_style)
                worksheet.write(15, 10, _('Kshs.'), center_heading_style)
                worksheet.write(15, 11, _('Kshs.'), center_heading_style)
                worksheet.write(15, 12, _('Kshs.'), center_heading_style)
                worksheet.write(15, 13, _('Kshs.'), center_heading_style)
                worksheet.write(13, 1, _('A.'), center_heading_style)
                worksheet.write(13, 2, _('B'), center_heading_style)
                worksheet.write(13, 3, _('C'), center_heading_style)
                worksheet.write(13, 4, _('D'), center_heading_style)
                worksheet.write(13, 5, _('E'), center_heading_style)
                worksheet.write(13, 8, _('F'), center_heading_style)
                worksheet.write(13, 9, _('G'), center_heading_style)
                worksheet.write(13, 10, _('H'), center_heading_style)
                worksheet.write(13, 11, _('J'), center_heading_style)
                worksheet.write(13, 12, _('K'), center_heading_style)
                worksheet.write(13, 13, _('L'), center_heading_style)
                #worksheet.insert_bitmap('kra.bmp', 0, 5)
                worksheet.col(0).width = 5000
                worksheet.col(1).width = 5000
                worksheet.col(2).width = 5000
                worksheet.col(3).width = 5000
                worksheet.col(4).width = 5000
                worksheet.col(5).height = 5000
                total_row = row + len(payslip_objs)
                row10 = total_row + 2
                row11 = total_row + 3
                row12 = total_row + 5
                row13 = total_row + 6
                row14 = total_row + 7
                row15 = total_row + 8
                row16 = total_row + 9
                worksheet.write(total_row, 0, _('TOTALS'), column_heading_style)
                worksheet.write(row10, 0,
                                _('To be completed by Employer at end of year'))
                worksheet.write(row11, 0, _(
                    'TOTAL CHARGEABLE PAY  (COL. H)   Kshs.'),
                                column_heading_style)
                worksheet.write(row11, 7,
                                _('TOTAL TAX (COL. L) Kshs.'),
                                column_heading_style)
                worksheet.write(row12, 0, _('IMPORTANT'),
                                column_heading_style)
                worksheet.write(row13, 0, _('Use P9A'))
                worksheet.write(row13, 8, self.env.user.company_id.name, easyxf(
                    'font:height 200;font:bold True;'))
                worksheet.write(row14, 0, _(
                    '1.(a) For all liable employees and where director/employee received Benefits in addition to cash emoluments.'))
                worksheet.write(row14, 8, _('DATE & STAMP'),
                                column_heading_style)
                worksheet.write(row15, 0, _(
                    '1.(b)  Where an employee is eligible to deduction on owner occupier interest.'))
                worksheet.write(row15, 8, _('SIGNATURE'),
                                column_heading_style)
                worksheet.write(row16, 0, _(
                    '2.(a) Allowable  interest in respect of any month must not exceed Kshs. 12,500/= or Kshs. 150,000 per year.'))
                for payslip in payslip_objs:
                    t1 = datetime.datetime.strptime(str(payslip.date_from),
                                                    '%Y-%m-%d')
                    t2 = datetime.datetime.strptime(str(payslip.date_from),
                                                    '%Y-%m-%d')
                    month = t2.strftime("%B")
                    year = t1.strftime("%Y")
                    worksheet.write(7, 1, _(payslip.employee_id.name.split(' ')[
                                    0] or ''),
                                    column_heading_style)
                    worksheet.write(9, 1, _(payslip.employee_id.name.split(' ')[
                                    -1] or ''),
                                    column_heading_style)
                    worksheet.write(9, 9, _(payslip.employee_id.tax_pin),
                                    column_heading_style)
                    worksheet.write(4, 0,
                                    _('TAX DEDUCTION CARD YEAR {}'.format(
                                        year)),
                                    column_heading_style)
                    worksheet.write(row, 0, month)
                    row += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P010':
                            total_gross_pay += line.amount
                            worksheet.write(row2, 1, line.amount)
                            worksheet.write(total_row, 1, total_gross_pay,
                                            column_heading_style)
                            row2 += 1
                all_non_cash_allowances = []
                partial_non_cash_allowances = []
                for rec in payslip_objs:
                    all_non_cash_allowances.append(rec.line_ids)
                    for line in rec.line_ids:
                        if line.code == 'P037':
                            partial_non_cash_allowances.append(rec.line_ids)
                            non_cash_allowances += line.amount
                for i in all_non_cash_allowances:
                    if i not in partial_non_cash_allowances:
                        worksheet.write(row9, 2, 0)
                        row9 += 1
                    else:
                        for rec in i:
                            if rec.code == 'P037':
                                worksheet.write(row9, 2, rec.amount)
                                row9 += 1
                                worksheet.write(total_row, 2,
                                                non_cash_allowances,
                                                column_heading_style)
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P045':
                            total_gross_taxable_pay += line.amount
                            worksheet.write(row3, 4, line.amount)
                            worksheet.write(total_row, 4,
                                            total_gross_taxable_pay,
                                            column_heading_style)
                            row3 += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P065':
                            nssf += line.amount
                            worksheet.write(row4, 7, line.amount)
                            worksheet.write(total_row, 7, nssf,
                                            column_heading_style)
                            row4 += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P085':
                            total_net_taxable_pay += line.amount
                            worksheet.write(row5, 10, line.amount)
                            worksheet.write(total_row, 10,
                                            total_net_taxable_pay,
                                            column_heading_style)
                            worksheet.write(row11, 3, _(total_net_taxable_pay),
                                            column_heading_style)
                            row5 += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P090':
                            paye += line.amount
                            worksheet.write(row6, 11, line.amount)
                            worksheet.write(total_row, 11, paye,
                                            column_heading_style)
                            row6 += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P095':
                            tax_relief += line.amount
                            worksheet.write(row7, 12, line.amount)
                            worksheet.write(total_row, 12, tax_relief,
                                            column_heading_style)
                            row7 += 1
                for rec in payslip_objs:
                    for line in rec.line_ids:
                        if line.code == 'P105':
                            net_paye += line.amount
                            worksheet.write(row8, 13, line.amount)
                            worksheet.write(total_row, 13, net_paye,
                                            column_heading_style)
                            worksheet.write(row11, 9, _(net_paye),
                                            column_heading_style)
                            row8 += 1
            else:
                raise ValidationError (_('Select Employee To print the P9 Form'))
            fp = BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.p9_file = excel_file
            wizard.file_name = filename_nhif + '.xls'
            wizard.p9_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'monthly.p9.wizard',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }