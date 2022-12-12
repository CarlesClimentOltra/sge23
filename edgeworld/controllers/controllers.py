# -*- coding: utf-8 -*-
# from odoo import http


# class Edgeworld(http.Controller):
#     @http.route('/edgeworld/edgeworld', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edgeworld/edgeworld/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('edgeworld.listing', {
#             'root': '/edgeworld/edgeworld',
#             'objects': http.request.env['edgeworld.edgeworld'].search([]),
#         })

#     @http.route('/edgeworld/edgeworld/objects/<model("edgeworld.edgeworld"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edgeworld.object', {
#             'object': obj
#         })
