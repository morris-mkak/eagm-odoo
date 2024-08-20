# -*- coding: utf-8 -*-

from odoo import models, fields
# import cStringIO
import requests
import io

from . import helpers


class Employee(models.Model):
    _inherit = 'hr.employee'

    model_photo = fields.Binary(string='Model Photo')

    def write(self, values):
        # image_data = values['model_photo'].decode('base64')
        # image_PIL = PIL.Image.open(
        #     cStringIO.StringIO(image_data))
        image_data = values['model_photo']
        requests.post('http://172.17.0.1:3000', files={
            'photo': (
                '{}-{}.jpg'.format(helpers.deaccent(self.name.encode('utf-8')), self.id),
                cStringIO.StringIO(image_data),
                'image/jpeg')
        }, data={
            'name': self.name
        })

        # image_np = np.array(image_PIL)

        return super(Employee, self).write(values)
