from odoo import api, models, fields
from odoo.modules.module import get_module_resource
import requests
import io

from . import helpers

@api.model
def _default_image(self):
    image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
    return base64.b64encode(open(image_path, 'rb').read())

class Employee(models.Model):
    _inherit = 'hr.employee'

    # model_photo = fields.Binary(string='Model Photo')
    model_photo = fields.Image(default=_default_image)

    def write(self, values):
        # image_data = values['model_photo'].decode('base64')
        # image_PIL = PIL.Image.open(
        #     cStringIO.StringIO(image_data))
        user = self.env['res.users'].browse(values[self.user_id])
        image_data = values.update(self._sync_user(user, vals.get('model_photo') == self._default_image()))
        
        requests.post(
            'http://172.17.0.1:3000', 
            files={
                'photo': (
                    '{}-{}.jpg'.format(helpers.deaccent(self.name.encode('utf-8')), self.id),
                    cStringIO.StringIO(image_data),
                    'image/jpeg')}, 
            data={
                'name': self.name})

        # image_np = np.array(image_PIL)

        return super(Employee, self).write(values)
