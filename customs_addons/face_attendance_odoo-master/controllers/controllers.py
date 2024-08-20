# -*- coding: utf-8 -*-
from odoo import http

# class FaceAttendance(http.Controller):
#     @http.route('/face_attendance/face_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/face_attendance/face_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('face_attendance.listing', {
#             'root': '/face_attendance/face_attendance',
#             'objects': http.request.env['face_attendance.face_attendance'].search([]),
#         })

#     @http.route('/face_attendance/face_attendance/objects/<model("face_attendance.face_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('face_attendance.object', {
#             'object': obj
#         })