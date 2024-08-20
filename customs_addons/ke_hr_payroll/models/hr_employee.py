# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class KEmployee(models.Model):
    _inherit = ["hr.employee"]

    payslips_line = fields.One2many('hr.payslip.line', 'employee_id',
                                    string='Payslip Lines')
    overtime_count = fields.Integer(
        compute='_compute_overtime_count',
        string='# Employee Overtime')

    def _compute_overtime_count(self):
        for rec in self:
            data = self.env['ke.overtime'].search(
                [('employee_id', 'in', rec.ids)]).ids
            rec.overtime_count = len(data)

    advance_count = fields.Integer(
        compute='_compute_advance_count',
        string='# Employee Advance')

    def _compute_advance_count(self):
        for rec in self:
            data = self.env['ke.advance'].search(
                [('employee_id', 'in', rec.ids)]).ids
            rec.advance_count = len(data)

    @api.depends('write_date')
    def _compute_employee_number(self):
        for rec in self:
            if rec.payroll_no:
                rec.employee_no = rec.payroll_no
            else:
                rec.employee_no = str(rec.id).zfill(4)

    def _get_default_currency(self):
        return self.env.user.company_id.currency_id

    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        required=True,
        default=_get_default_currency)
    is_consultant = fields.Boolean('Is a Consultant?')
    nhif = fields.Char(
        'NHIF No.',
        required=True,
        help="Fill in the NHIF number issued by National Hospital Insurance Fund. For those employees in the formal sector, it is compulsory to be a member.")
    nssf_vol = fields.Boolean(
        'NSSF Voluntary Contributions?',
        default=False,
        help="Check this box if the employee or employer or both are is willing to contribute voluntarily to NSSF Scheme.The amount will be a voluntary top up by either employee or employer over and above the mandatory tier I and tier II contributions")
    nssf_t3 = fields.Boolean(
        'NSSF Tier III Contributions?', default=False,
        help="This is for pension contributions above the mandatory amount defined in the NSSF Act 2013.The exact figure will vary from employer to employer")
    nssf_vol_mem = fields.Float(
        'Voluntary Member Amount',
        digits=dp.get_precision('Account'))
    nssf_vol_emp = fields.Float(
        'Voluntary Employer Amount',
        digits=dp.get_precision('Account'))
    nssf_t3_emp = fields.Float(
        'Tier III Employer Amount',
        digits=dp.get_precision('Account'))
    nssf_t3_mem = fields.Float(
        'Tier III Member Amount',
        digits=dp.get_precision('Account'))
    nssf = fields.Char(
        'NSSF No.',
        required=True,
        help="key in the Employee NSSF number. It is mandatory to register as a memmber of NSSF as an employee")
    helb = fields.Boolean(
        'HELB Loan ?', default=False,
        help="Check this box if the employee is currently paying for Higher Education Loans Board Loan")
    helb_rate = fields.Float(
        'HELB Monthly Amount',
        digits=dp.get_precision('Account'),
        help="HELB will issue Loan payment instructions for your employee upon contacting them. Upon the employment of any loanee, you need to inform the Board in writing within a period of three months of such employment. Fill in the monthly figure advised by HELB.")
    tax_pin = fields.Char(
        'KRA PIN',
        required=True,
        help="Key in the 11 charater PIN of the employee, It is mandatory to have a PIN as a tax payer")
    # Others
    # birth_country = fields.Many2one('res.country', 'Country of Birth')
    kins = fields.One2many(
        'ke.employee.kin',
        'employee_id',
        'Dependants',
        help="These are records of details of family members of the employee who may be benefiting from Health Insurance or any other such benefits offered by employer")
    employee_no = fields.Char(
        'Internal Number',
        compute='_compute_employee_number',
        store=True,
        help="This is a unique number assigned to each employee internally in the DB. If you do not set the payroll number, this number will be used as the payroll number")
    payroll_no = fields.Char(
        'Payroll Number',
        help="a unique number assigned to each employee to be used in payroll")
    personal_email = fields.Char(
        'Personal Email',
        help="Personal Email that can be used to reach the employee before or after employment")
    deductions = fields.One2many(
        'ke.deductions',
        'employee_id',
        'Deductions',
        help="These are after-tax deductions (other than NHIF and HELB) made on employee salary.They include contributions or deductions towards SACCO,Salary Advance,etc")
    reliefs = fields.One2many(
        'ke.reliefs', 'employee_id', 'Tax Relief',
        help="These are tax reliefs (other than the Personal Tax Relief) entitled to th employee..example is the Insurance relief.")
    # disability Tax Exemption
    disability = fields.Boolean(
        'Employee has disability ?',
        default=False,
        help="Check this box if the employee has disability and is registered with Council of Persons with Disability and has a certificate of exemption from commissioner of Domestic Taxes")
    disability_rate = fields.Float(
        'Disability Exempt Amount',
        digits=dp.get_precision('Account'),
        help="For Persons with Disability, First KShs 150,000 pm is exempt from tax. Here, you can record expenses related to personal care and home care allowable up to a maximum of KShs 50,000 per month.")
    disability_cert = fields.Char(
        'Disability Cert No',
        help="Persons with Disability must apply for certificate of exemption from Commissioner of Domestic Taxes. Cetificate is issued within 30 days and is valid for 3 years")
    hosp = fields.Boolean(
        'H.O.S.P Deposit?',
        default=False,
        help='Check this box if the employee is making monthly deposits in respect of funds deposited in “approved Institution” under "Registered Home Ownership Savings Plan". Such Employee is eligible to a deduction up to a maximum of Kshs. 4,000 /- (Four thousand shillings) per month or Kshs. 48,000/- per annum ')
    hosp_deposit = fields.Float(
        'Actual Deposit to H.O.S.P (Monthly):', dp=(32, 2))
    mortgage = fields.Boolean(
        'Owner Occupied Interest (O.C.I)?',
        default=False,
        help="Check this box if the employee is paying any interest on load borrowed to finance the purchase or improvement of his or her own house which is occupying.The amount of interest allowable under the law to be deducted from taxable pay must not exceed Kshs.150,000 per year (equivalent to Kshs. 12,500 per month). ")
    mortgage_interest = fields.Float(
        'Actual Interest paid (Monthly):', dp=(32, 2))
    pension = fields.Boolean(
        'Personal Pension/Providend Fund Scheme?',
        default=False,
        help="Check this box if the employee is registered to a personal pension or provident fund scheme.Contribution to any registered defined benefit fund or defined contribution fund is an admissible deduction in arriving at the employee's taxable pay of the month")
    resident = fields.Boolean(
        'Resident?',
        default=True,
        help="Check this box if the employee is a resident in Kenya. Such inviduals are entitled to a personal tax relief of Kshs. 1,162 per month and insurance relief if any")
    emp_type = fields.Selection(
        [('primary', 'Primary Employee'),
         ('secondary', 'Secondary Employee')],
        default='primary', required=True, string="Type of Employee:",
        help='[primary] - Select this option of this is the primary employment for the employee\n [Secodary] -Select tis option if this is the secondary employment for the employee.\n Default case is [primary] ')
    director = fields.Boolean(
        'Employee is a Director?',
        default=False,
        help='Check this box if the employee is a director of the Company')
    director_type = fields.Selection([("full",
                                       "Full Time Service Director"),
                                      ("nonfull",
                                       "Non Full Time Service Director")],
                                     string="Director Type")
    global_income = fields.Float(
        'Global Income (Non Full Time Director):', dp=(32, 2),
        help="Please record the Global Income of a Non Full time Service director. This amount will be used in computing the taxable pay as per the law")

    _sql_constraints = [
        ('ke_payroll_no', 'unique (payroll_no)',
         "Another employee with the same payroll number exist!. Payroll number is unique.")]

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')