# -*- coding: utf-8 -*-

from odoo import models, fields


class hr_ke_timesheet_sheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    slip_id = fields.Many2one(
        'hr.payslip',
        'Payslip',
        readonly=True,
        states={
            'new': [
                ('readonly',
                 False)]},
        help="This is the Payslip which the approved timesheet info will appear in")
    slip_ref = fields.Char(
        'Payslip Number',
        related='slip_id.number',
        readonly=True,
        help="This is the Payslip which the approved timesheet info will appear in")
    employee_id = fields.Many2one(
        'hr.employee', 'Employee', required=True, readonly=True, states={
            'draft': [
                ('readonly', False)], 'new': [
                ('readonly', False)]})

    # below method is called by the timesheet workflow when timesheet is being
    # approved

    def approve_timesheet(self):
        for rec in self:
            slip = {'id': ''}
            code = ''
            field_nm = ''
            arg = ''
            contract_id = rec.employee_id._get_latest_contract(field_nm, arg)
            contract = rec.env['hr.contract'].browse(
                contract_id[rec.employee_id.id])
            if contract.rem_type == 'monthly':
                code = 'PM'
            elif contract.rem_type == 'hourly':
                code = 'PH'
            else:
                code = 'PD'

            vals_payslip = {
                'employee_id': rec.employee_id.id,
                'contract_id': contract.id,
                'struct_id': contract.struct_id.id,
                'date_from': rec.date_from,
                'date_to': rec.date_to,
                'state': 'draft',
                'paid': False,
                'name': 'Payslip of ' + rec.employee_id.name_related + ' for ' + rec.date_from + ' to ' + rec.date_to,
            }
            slip = rec.env['hr.payslip'].create(vals_payslip)
            vals_work = {
                'code': code,
                'contract_id': contract.id,
                'number_of_days': rec.timesheet_activity_count,
                'number_of_hours': rec.total_timesheet,
                'name': rec.employee_id.name_related,
                'payslip_id': slip.id,
            }
            res = rec.env['hr.payslip.worked_days'].create(vals_work)
            if res:
                slip.compute_sheet()
            rec.write({'state': 'done', 'slip_id': slip.id})
            #raise ValidationError('state is done')
            return True

    
    def action_set_to_draft(self):
        for rec in self:
            super(hr_ke_timesheet_sheet, rec).action_set_to_draft()
            # cancel payslip if still in draft state
            if rec.slip_id and rec.slip_id.state == 'draft':
                rec.slip_id.signal_workflow('cancel_sheet')
        return True
