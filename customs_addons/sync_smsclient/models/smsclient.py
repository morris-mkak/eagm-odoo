# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time
import urllib
import logging
import urllib.parse
import urllib.request
from odoo.exceptions import *
from odoo import api, fields, models, _
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)

try:
    from SOAPpy import WSDL
except :
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
    " e.g.: apt-get install python-soappy")


class PartnerSmsSend(models.Model):
    _name = "partner.sms.send"
    _description = "Partner Sms Send"

    def _default_get_mobile(self):
        partner_pool = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(active_ids):
            i += 1
            res = partner.mobile
        if i > 1:
            raise Warning(_('You can only select one partner'))
        return res

    def _default_get_gateway(self):
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([])
        return gateway_ids and gateway_ids[0] or False

    @api.onchange('gateway')
    def onchange_gateway(self):
        """
            Update the following fields when the gateway is changed
        """
        if self.gateway:
            self.validity = self.gateway.validity
            self.classes = self.gateway.classes
            self.deferred = self.gateway.deferred
            self.priority = self.gateway.priority
            self.coding = self.gateway.coding
            self.tag = self.gateway.tag
            self.nostop = self.gateway.nostop

    mobile_to = fields.Char("To", size=256, default=_default_get_mobile, required=True, readonly=False)
    app_id = fields.Char('API ID', size=256, default=_default_get_gateway)
    user = fields.Char('Login', size=256)
    password = fields.Char('Password', size=256)
    text = fields.Text('SMS Message', required=True)
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True)
    validity = fields.Integer('Validity', help='the maximum time -in minute(s)- before the message is dropped') 
    classes = fields.Selection([
            ('0', 'Flash'),
            ('1', 'Phone display'),
            ('2', 'SIM'),
            ('3', 'Toolkit')
        ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred', help='the time -in minute(s)- to wait before sending the message') 
    priority = fields.Selection([
            ('0','0'),
            ('1','1'),
            ('2','2'),
            ('3','3')
        ], 'Priority', help='The priority of the message')
    coding = fields.Selection([
            ('1', '7 bit'),
            ('2', 'Unicode')
        ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message') # same

    def sms_send(self):
        """
            send sms to smsclient
        """
        client_obj = self.env['sms.smsclient']
        for data in self:
            if not data.gateway:
                raise Warning(_('No Gateway Found'))
            else:
                client_obj._send_message(data)
        return {}


class SMSClient(models.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    name = fields.Char('Gateway Name', size=256, required=True)
    url = fields.Char('Gateway URL', size=256, required=True, help='Base url for message')
    property_ids = fields.One2many('sms.smsclient.parms', 'gateway_id', 'Parameters')
    history_line = fields.One2many('sms.smsclient.history', 'gateway_id', 'History')
    method = fields.Selection([
            ('http', 'HTTP Method'),
            ('smpp', 'SMPP Method')
        ], 'API Method', default='http')
    state = fields.Selection([
            ('new', 'Not Verified'),
            ('waiting', 'Waiting for Verification'),
            ('confirm', 'Verified'),
        ], 'Gateway Status', default='new', readonly=True)
    users_id = fields.Many2many('res.users', string='Users Allowed')
    code = fields.Char('Verification Code', size=256)
    body = fields.Text('Message', help="The message text that will be send along with the email which is send through this server")
    validity = fields.Integer('Validity', help='The maximum time -in minute(s)- before the message is dropped', default=10)
    classes = fields.Selection([
            ('0', 'Flash'),
            ('1', 'Phone display'),
            ('2', 'SIM'),
            ('3', 'Toolkit')
        ], 'Class', default='1' ,help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer('Deferred', default=0 , help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3')
        ], 'Priority', default='3', help='The priority of the message ')
    coding = fields.Selection([
            ('1', '7 bit'),
            ('2', 'Unicode')
        ],'Coding', default='1', help='The SMS coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop', default=True, help='Do not display STOP clause in the message, this requires that this is not an advertising message')
    char_limit = fields.Boolean('Character Limit', default=True)

    def _check_permissions(self,gateway_id):
        """
            Check permission
        """
        self._cr.execute('select * from res_users_sms_smsclient_rel where sms_smsclient_id=%s and res_users_id=%s' % (gateway_id, self.env.uid))
        data = self._cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, data, name):
        """
            prepare sms client queue data
        """
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity,
            'classes': data.classes,
            'deferred': data.deferred,
            'priority': data.priority,
            'coding': data.coding,
            'tag': data.tag,
            'nostop': data.nostop,
        }

    def _send_message(self, data):
        """
            check permission after send message
        """
        gateway = data.gateway
        if gateway:
            if not self._context.get('default_intake_demo_data') and not self._check_permissions(gateway.id) and self.env.uid != SUPERUSER_ID:
                raise Warning(_('You have no permission to access %s ') % (gateway.name))
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                    if p.type == 'user':
                        prms[p.name] = p.value
                    elif p.type == 'password':
                        prms[p.name] = p.value
                    elif p.type == 'to':
                        prms[p.name] = data.mobile_to
                    elif p.type == 'sms':
                        prms[p.name] = (data.text).encode('utf-8')#data.text
                    elif p.type == 'extra':
                        prms[p.name] = p.value
                    elif p.type == 'sender':
                        prms[p.name] = p.value
                params = urllib.parse.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.env['sms.smsclient.queue']
            vals = self._prepare_smsclient_queue(data, name)
            queue_obj.create(vals)
        return True

    @api.model
    def _check_queue(self):
        """
            check sms queue history
        """
        queue_obj = self.env['sms.smsclient.queue']
        history_obj = self.env['sms.smsclient.history']
        sids = queue_obj.search([('state', '!=', 'send'),('state', '!=', 'sending')], limit=30)
        for queue_id in sids:
            queue_id.write({'state': 'sending'})
        error_ids = []
        sent_ids = []
        for sms in sids:
            if sms.gateway_id.char_limit:
                if len(sms.msg) > 160:
                    error_ids.append(sms.id)
                    continue
            if sms.gateway_id.method == 'http':
                try:
                    urllib.request.urlopen(sms.name)
                except Exception as e:
                    raise UserError(_('Error %s') % (e,))
            ### New Send Process OVH Dedicated ###
            ## Parameter Fetch ##
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                    elif p.type == 'password':
                        pwd = p.value
                    elif p.type == 'sender':
                        sender = p.value
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    message = ''
                    if sms.coding == '2':
                        message = str(sms.msg).decode('iso-8859-1').encode('utf8')
                    if sms.coding == '1':
                        message = str(sms.msg)
                    result = soap.telephonySmsUserSend(str(login), str(pwd),
                        str(account), str(sender), str(sms.mobile), message,
                        int(sms.validity), int(sms.classes), int(sms.deferred),
                        int(sms.priority), int(sms.coding),str(sms.gateway_id.tag), int(sms.gateway_id.nostop))
                    ### End of the new process ###
                except Exception as e:
                    raise UserError(_('Error %s') % (e,))
            vals = { 'name': _('SMS Sent'), 'gateway_id': sms.gateway_id.id, 'sms': sms.msg, 'to': sms.mobile}
            history_obj.create(vals)
            sent_ids.append(sms)
        for sent_id in sent_ids:
            sent_id.write({'state': 'send'})
        for error_id in queue_obj.browse(error_ids):
            error_id.write({'state': 'error', 'error': 'Size of SMS should not be more then 160 char'})
        return True


class SMSQueue(models.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    name = fields.Text('SMS Request', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]})
    msg = fields.Text('SMS Text', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile No', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Queued'),
        ('sending', 'Waiting'),
        ('send', 'Sent'),
        ('error', 'Error'),
    ], 'Message Status', default='draft', readonly=True)
    error = fields.Text('Last Error', size=256, readonly=True, states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', default=lambda self: fields.Datetime.now(), readonly=True)
    validity = fields.Integer('Validity', help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
            ('0', 'Flash'),
            ('1', 'Phone display'),
            ('2', 'SIM'),
            ('3', 'Toolkit')
        ], 'Class', help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred', help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3')
        ], 'Priority', help='The priority of the message ')
    coding = fields.Selection([
            ('1', '7 bit'),
            ('2', 'Unicode')
        ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256, help='An optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')


class Properties(models.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    name = fields.Char('Property name', size=256, help='Name of the property whom appear on the URL')
    value = fields.Char('Property value', size=256, help='Value associate on the property for the URL')
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway')
    type = fields.Selection([
            ('user', 'User'),
            ('password', 'Password'),
            ('sender', 'Sender Name'),
            ('to', 'Recipient No'),
            ('sms', 'SMS Message'),
            ('extra', 'Extra Info')
        ], 'API Method', help='If parameter concern a value to substitute, indicate it')


class HistoryLine(models.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    name = fields.Char('Description', size=160, required=True, readonly=True)
    date_create = fields.Datetime('Date', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Username', default=lambda self: self.env.user, readonly=True)
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway', ondelete='cascade', required=True)
    to = fields.Char('Mobile No', size=15, readonly=True) 
    sms = fields.Text('SMS', size=160, readonly=True)

    @api.model
    def create(self, vals):
        res = super(HistoryLine, self).create(vals)
        self._cr.commit()
        return res
