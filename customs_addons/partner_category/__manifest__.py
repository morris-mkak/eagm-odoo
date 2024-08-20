{
    'name': 'Partner Category',
    'version': '1.0.1',
    'author': 'FreelancerApps',
    'category': 'Tools',
    'depends': ['base', 'sale', 'sales_team'],
    'summary': 'Set category for partner so you will get partner hierarchy group partner category hierarchy group by partner tag group by category group by tag partner tag  contact tag',
    'description': """
Partner Category Hierarchy
==========================
Set category for partner so you will get partner hierarchy

<Tag>
group partner category hierarchy group by partner tag group by category group by tag partner tag  contact tag
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
    ],
    'images': ['static/description/partner_category_banner.png'],
    'price': 3.99,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
}
