from odoo import http
from odoo.http import request

class WebsiteController(http.Controller):
    @http.route(['/'], type='http', auth="public", website=True)
    def index(self, **kw):
        # Establecer el idioma español por defecto
        if request.env.user._is_public():
            lang = request.env['res.lang'].search([('code', '=', 'es_ES')])
            if lang:
                request.env.context = dict(request.env.context, lang='es_ES')
        return request.redirect('/universities')