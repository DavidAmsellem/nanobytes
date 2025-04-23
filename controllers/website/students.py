from odoo import http
from odoo.http import request
from odoo.osv import expression

class UniversityWebsiteStudents(http.Controller):
    """Controlador para las páginas de estudiantes"""

    @http.route('/students', type='http', auth='public', website=True)
    def list_students(self, **kw):
        """Display list of all students with search and university filter"""
        domain = []
        
        # Filtrar por universidad si se selecciona una
        if kw.get('university_id'):
            domain.append(('university_id', '=', int(kw.get('university_id'))))
        
        # Filtrar por término de búsqueda
        search_term = kw.get('search', '').strip()
        if search_term:
            domain = expression.AND([domain, [
                '|', '|',
                ('name', 'ilike', search_term),
                ('tutor_id.name', 'ilike', search_term),
                ('enrollment_ids.subject_id.name', 'ilike', search_term)
            ]])
        
        # Obtener estudiantes y universidades
        students = request.env['university.student'].sudo().search(domain)
        universities = request.env['university.university'].sudo().search([])
        
        return request.render('Universidad.website_students', {
            'students': students,
            'universities': universities,
            'search': search_term,
        })