# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo Employee Evaluation Management",
  "summary"              :  """This module manages the evaluation reports of the employees.""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Employee-Evaluation-Management.html",
  "description"          :  """Employee Evaluation Management
""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=employee_evaluation_management",
  "depends"              :  [
                             'hr_timesheet',
                             'hr_attendance',
                             'hr_holidays',
                             'project',
                            ],
  "data"                 :  [
                             'security/security.xml',
                             'security/ir.model.access.csv',
                             'data/work_type_data.xml',
                             'views/project_view.xml',
                             'views/assets.xml',
                             'views/evaluation_record_view.xml',
                             'views/evaluation_question_view.xml',
                             'views/evaluation_template_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
