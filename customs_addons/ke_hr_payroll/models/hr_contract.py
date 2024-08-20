# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class KeContract(models.Model):
    """Inherited to add more features"""
    _inherit = "hr.contract"

    wage = fields.Monetary(
        'Remuneration',
        required=True,
        currency_field='currency_id',
        help="""This is the amount of salary or wage paid to the employee.\n
        If the remunation model is [Monthly] then this is the Monthly Basic Salary paid to
        employee\n If the remuneration model is [Daily] then this is the Daily Wage
        paid to employee. \n If the remuneration model is [Hourly] then this is the
        Hourly Wage paid to employee""")
    rem_type = fields.Selection(related="structure_type_id.wage_type", readonly=True)
    tax_applicable = fields.Selection(
        related="structure_type_id.tax_applicable",readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        'Currency',
        related='employee_id.currency_id')

    @api.constrains('wage')
    def ke_validate_values(self):
        if self.wage < 0:
            raise ValidationError(_("Only Positive value is accepted for salary or wage"))

    benefits = fields.One2many(
        'ke.benefits',
        'contract_id',
        'Benefits',
        help="These are all non cash benefits other than Housing and Car benefit that are entitled to your employee and are taxable by Kenyan Law. These includes, Eletricity, water, Telephone, servants..etc.Such benefits amounting to KES 3000/- and above are taxable")
    cash_allowances = fields.One2many(
        'ke.cash_allowances',
        'contract_id',
        'Cash Allowances',
        help='These are all cash allowances that are taxable as per kenyan law. These incluses overtime allowances, leave alllowances,transport allowances,house allowances, directors fee, lump sum pay, etc..')
    house = fields.Boolean(
        'Housing Benefit ?', default=False,
        help="Check this box if your employee is entitled to housing by employer. Such benefit is taxable")
    house_type = fields.Selection(
        [("own", "Employer's Owned House"),
         ("rented", "Employer's Rented House"),
         ("agric", "Agriculture Farm"),
         ("director", "House to Non full time service Director")])
    rent = fields.Float(
        'Rent of House/Market Value', dp=(32, 2),
        help="This the actual rent of house paid by the employer if the house is rented by employer on behalf of the employee. If the House is owned by the Employer, then this is the Market value of the rent of the house.")
    rent_recovered = fields.Float('Rent Recovered from Employee:', dp=(
        32, 2),
                                  help="This is the actual rent recovered from the employee if any")
    car = fields.Boolean('Car Benefit:', default=False,
                         help="Check this box if the employee is provided with a motor vehicle by employer. the chargeable benefit for private use shall be the higher of the rate determined by the Commissioner of taxes and the prescribed rate of benefit. Where such vehicle is hired or leased from third party, employees shall be deemed to have received a benefit in that year of income, equal to the cost of hiring or leasing")
    cars = fields.One2many(
        'ke.cars',
        'contract_id',
        'Car Benefits',
        help="This is a record of cars provided to the employee by the employer for personal use. The taxable value of this benefit is computed here as per the prescribed rates in the law")



