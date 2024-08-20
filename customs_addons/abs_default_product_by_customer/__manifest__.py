# -*- coding: utf-8 -*-
#################################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
'name'        : "Default Product By Customer",
'author'      : "Ascetic Business Solution",
'category'    : "Sales",
'summary'     : "Default Product By Customer On sale order is customize for our expectation & needs.",
'website'     : "http://www.asceticbs.com",
'description' : """Added page product in customer form view module,add one2many product_ids field inherit in customer form page ,and for sale order make a funcationality  for select customer and than come product automatically.""" ,
'version'     : '14.0.1.0',
'depends'     : ['base','sale_management'],
'data'        : [
                'security/ir.model.access.csv',
                'views/res_partner_view.xml',
                ],
'license': 'OPL-1',
'images': ['static/description/banner.png'],
'price'   : 35.00,
'installable' : True,
'application' : True,
'auto_install': False,
}
