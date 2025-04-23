from odoo import http
from odoo.http import request
from typing import Dict, Any
from .universities import UniversityWebsiteUniversities

class UniversityWebsiteProfessors(http.Controller):
    """Controlador para las páginas de profesores"""

    def __init__(self):
        super().__init__()
        self._university_controller = UniversityWebsiteUniversities()

    @http.route('/professors', type='http', auth='public', website=True)
    def list_all_professors(self, **kw: Any) -> str:
        """Mostrar todos los profesores con opciones de búsqueda y filtrado"""
        Professor = request.env['university.professor'].sudo()
        University = request.env['university.university'].sudo()
        
        # Obtener y validar parámetros de búsqueda
        search = kw.get('search', '')
        
        # Manejo seguro de conversión de ID de universidad
        try:
            university_id = int(kw.get('university_id')) if kw.get('university_id') else 0
        except ValueError:
            university_id = 0
            
        # Manejo seguro de conversión de ID de departamento
        try:
            department_id = int(kw.get('department_id')) if kw.get('department_id') else 0
        except ValueError:
            department_id = 0
        
        # Construir dominio de búsqueda
        domain = []
        if search:
            domain = [
                '|', '|',
                ('name', 'ilike', search),
                ('department_id.name', 'ilike', search),
                ('subject_ids.name', 'ilike', search)
            ]
        
        if university_id:
            domain.append(('university_id', '=', university_id))
        if department_id:
            domain.append(('department_id', '=', department_id))
            
        # Obtener profesores filtrados
        professors = Professor.search(domain)
        
        # Obtener datos para los filtros
        universities = University.search([])
        departments = request.env['university.department'].sudo().search([])
        
        # Agrupar profesores por universidad
        professors_by_university = {}
        for university in universities:
            uni_professors = professors.filtered(lambda p: p.university_id.id == university.id)
            if uni_professors:
                professors_by_university[university.id] = {
                    'university': university,
                    'professors': uni_professors,
                    'theme_colors': self._university_controller._get_theme_color(university.id)
                }
        
        return request.render('Universidad.website_all_professors', {
            'universities': professors_by_university,
            'all_universities': universities,
            'all_departments': departments,
            'search': search,
            'selected_university': university_id,
            'selected_department': department_id
        })

    @http.route('/professors/<int:university_id>', type='http', auth='public', website=True)
    def list_university_professors(self, university_id: int, **kw: Any) -> str:
        """Mostrar profesores de una universidad específica"""
        university = request.env['university.university'].sudo().browse(university_id)
        if not university.exists():
            return request.redirect('/professors')
            
        professors = request.env['university.professor'].sudo().search([
            ('university_id', '=', university_id)
        ])
        
        return request.render('Universidad.website_professors', {
            'university': university,
            'professors': professors,
            'theme_colors': self._university_controller._get_theme_color(university_id)
        })