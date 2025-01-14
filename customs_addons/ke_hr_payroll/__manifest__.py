# -*- coding:utf-8 -*-
# Copyright (C) 2020 Dishon Kadoh (<mail@dishonkadoh.com>).
{
    'name': 'Odoo14 Kenyan Payroll',
    'category': 'Human Resources',
    'version': '14.0.0.1',
    'summary': 'This Odoo 14 generic payroll module is customised to Comply With Kenyan Tax Laws to Manage your employee payroll records',
    'description': "",
    'author': 'Dishon Kadoh',
    "images": ['static/description/banner.png'],
    "website": "http://dishonkadoh.com/",
    "price": 460.0,
    "currency": "EUR",
    "license": "LGPL-3",
    'depends': ['base',
                'hr',
                'hr_contract',
                'account',
                'hr_payroll',
                'hr_payroll_account',
                'attachment_indexation'],
    'external_dependencies': {'python': ['openpyxl']},
    'data': [
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/overtime_view.xml',
        'views/advance_view.xml',
        'views/hr_payslip.xml',
        # 'views/hr_contract_type.xml',
        'views/hr_contract.xml',
        'wizard/kra_tax_form.xml',
        'views/res_config_settings.xml',
        'views/hr_loan.xml',
        'views/hr_payslip_run.xml',
        'views/benefit_type.xml',
        'views/relation_type.xml',
        'views/relief_type.xml',
        'views/deductions_type.xml',
        'views/cash_allowances_type.xml',
        'views/non_cash_allowances_type.xml',
        'views/cash_allowances.xml',
        'views/reliefs.xml',
        'views/deductions.xml',
        'views/employee_kin.xml',
        'views/hr_payroll_structure_type.xml',
        'views/hr_employee.xml',
        # 'views/hr_payroll_account_views.xml',
        'data/hr_payroll_structure_type.xml',
        'data/overtime_data.xml',
        'data/salary_advance_data.xml',
        'data/categories_data.xml',
        'data/payroll_structure.xml',
        'data/perm_emp_rules_data.xml',
        'data/non_cash_allowances_data.xml',
        'data/cash_allowances_data.xml',
        'data/deductions_data.xml',
        'data/tax_relief_data.xml',
        'data/hr_loan_seq.xml',
        'data/res.bank.csv',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'insallable': True

}