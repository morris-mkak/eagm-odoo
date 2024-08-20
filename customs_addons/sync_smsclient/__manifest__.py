# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "SMS Client",
    "version": "1.1",
    "depends": ["base", "mail", "sms"],
    "author": "Synconics Technologies Pvt. Ltd.,Julius Network Solutions,SYLEAM,OpenERP SA",
    'summary': 'Allows to send sms via different gateways',
    'images': ['static/description/main_screen.png'],
    "description": """
SMS Client module provides:
===========================
Sending SMSs very easily, individually or collectively.

*Generalities

Odoo does not directly generate the SMS you will have to subscribe to an operator with a web interface (Type OVH) or via a URL generation.
If you want to use a 'SMPP Method' you must have to install the library "Soap" which can be installed with: apt-get install python-soappy.
You can find it on https://pypi.python.org/pypi/SOAPpy/
You don't need it if you use a "HTTP Method' to send the SMS.

*Use Multiple Gateways.

The Gateway configuration is performed directly in the configuration menu. For each gateway, you have to fill in the information for your operator.

To validate Gateway, code is send to a mobile phone, when received enter it to confirm SMS account.
help desk management

help desk

Helpdesk

ticket

issue

after sales service

service

helpdesk management

repair

repair service

field service

ticket management

issue management

ticket escalate

issue escalate

escalate

RMA

return merchandise authorization

rma sms

sms

repair service management

field service management

after sales service management

auto assign ticket

ticket number

ticket priority

ticket stages

ticket configuration

cancel ticket

ticket monitor

portal

portal user

portal user ticket

portal user chat

portal user login

website portal user

helpdesk ticket

generate ticket

submit ticket

ticket attachment

ticket document

ticket chat

chat

rma warranty

rma refund

refund

warranty

product warranty

warranty expire

product return

warranty template

repair order

sales order

invoice

accounting

account

warehouse

inventory

website

ecommerce

shipment

receipt

report

rma repair order

sla

service level agreement

ticket deadline

sla policy

sla management

call center

sla on ticket

sla performance

ticket performance

salesperson performance

team performance

sla target

sla report

ticket time

ticket timesheet

ticket time start

ticket time stop

timesheet

ticket time spent

track ticket time

ticket time log

log ticket time

timesheet start

timesheet stop

ticket invoice

timesheet invoice

repair invoice

helpdesk invoice

ticket timesheet invoice

timesheet bill

ticket bill

repair intake

product intake

item intake

inventory intake

intake

repair service intake

ticket intake

sign

digital signature

signed document

document

attachment

sign attachment

pdf

intake approval

intake rejection

reject intake

approve intake

out take

product out take

product outtake

outtake

item outtake

item out take

ticket out take

reject outtake

approve out take

repair service out take

out take sign

mail

dashboard

repair service dashboard

team dashboard

graph

bar

pie

line

ticket assign

assign ticket

ticket auto assign

unassign ticket

ticket unassign

support system

repair service support

chat support

chat ticket system

live chat support

live chat ticket support

helpdesk live chat

helpdesk live chat support

helpdesk live chat ticket

product support service

repair service contract

helpdesk contract

contract

service contract

service contract start

service contract stop

ticket contract

monitor contract

contract renewal

service contract renewal

renew contract

service contract renew

renew service contract

helpdesk contract renew

renew helpdesk contract

service contract invoice

service contract bill

helpdesk contract invoice

ticket from lead

lead to ticket

crm to ticket

helpdesk report

ticket report

rma replace

rma repair

refurbishing

refurbish

product refurbished

repair service refurbish

refurb

refurb product

sub contract

contract renew

subscription

contract subscription

recurring contract

reopen ticket

ticket reopen

re open ticket

ticket re open

rework ticket

ticket rework

repair rework

rework repair

ticket quotation

quotation ticket

ticket estimation

repair quotation

quotation repair

estimation ticket

appointment

repair service appointment

customer appointment

client appointment

ticket appointment

recurring service contract

recurring service ticket

recurring ticket

ticket recurring

service ticket recurring

dynamic ticket

auto generate ticket number

ticket sequence

auto assign ticket number

auto sequence ticket number

unique ticket

unique ticket number

ticket type

merge ticket

ticket merge

sub ticket

sub task

sub service ticket

ticket sub ticket

ticket divide

divide ticket

priority ticket

priority

escalation

team escalation

ticket escalation

issue escalation

task escalation

escalate ticket

feedback

customer feedback

client feedback

repair service feedback

ticket feedback

repair service customer feedback

auto mail

mail automation

customer satisfaction

customer rating

customer survey

survey mail

customer forum

forum

customer knowledge base

client knowledge base

repair service knowledge base

support team

support team knowledgebase

faq

frequently ask question

Q&A

helpdesk forum

support system forum

support system knowledge base

support service video

website slider

customer document

document for customer

knowledgebase video

forum video

forum document

customer like

customer dislike

portal customer

ticket sms

auto send sms

sms service

repair service sms

auto ticket create sms

send sms

stage change sms

sms update

ticket update by sms

customer sms

client sms

helpdesk sms

support service sms

helpdesk video

helpdesk timesheet

helpdesk timesheet invoice

helpdesk timesheet bill

intake website form

intake customer website form

intake product customer web form

helpdesk intake form

helpdesk intake web form

helpdesk intake product web form

website timesheet web form

ticket approval

e-signature

esign

esign approval

esignature approval

website esign

website esignature

customer esign

customer esignature

customer e-signature

customer approval e-sign

customer approval esign

customer approval e-signature

customer approval esignature

repair service warranty

warranty management

inventory warranty

sales warranty

repair product warranty

customer warranty

sales order warranty

merge timesheet

team timesheet merge

merge timesheet repair service

helpdesk automation

automate helpdesk

automatic ticket system
    """,
    "website": "http://www.synconics.com,http://julius.fr",
    "category": "Tools",
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "view/smsclient_view.xml",
        "view/serveraction_view.xml",
        "view/smsclient_data.xml",
        "wizard/mass_sms_view.xml",
        "view/partner_sms_send_view.xml",
        "view/smstemplate_view.xml",
    ],
    "demo": [
        'demo/sms_demo.xml',
    ],
    'price': 0.0,
    'currency': 'EUR',
    "active": False,
    'application': True,
    "installable": True,
    'license': 'OPL-1',
}
