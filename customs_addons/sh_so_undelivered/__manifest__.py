# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    'name': 'Sales Order Undelivered',
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    "support": "support@softhealer.com",
    'version': '14.0.1',
    'category': 'Sales',
    "summary": """Display Undelivered So App, Filter Undelivered Records Module In So With, order date, Group by, partner ,product, Order Date, In List View, Form View, Kanban View, Search View Odoo""",
    'description': """If you want to get an undelivered sales order? Here we build a module that can help to find all undelivered sales orders easily, very easy to find undelivered sales order from one click with list view and form of the sales order. You can easily group by undelivered order by name, customer, order no.""",
    'depends': [
        'sale_management'
    ],
    'data': [
        'views/sale_order_line.xml',
    ],
    'images': ['static/description/background.png', ],
    "live_test_url": "https://www.youtube.com/watch?v=5kZo8049t3I&feature=youtu.be",
    "license": "OPL-1",
    'auto_install': False,
    'installable': True,
    'application': True,
    "price": 25,
    "currency": "EUR"
}
