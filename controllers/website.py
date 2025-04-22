"""
Este módulo contiene el controlador principal para las funcionalidades del sitio web de la universidad.
Maneja todas las rutas públicas y del portal relacionadas con universidades, profesores, estudiantes y calificaciones.
"""

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.osv import expression
from typing import Dict, Any

class UniversityWebsite(http.Controller):
    """
    Controlador principal para las características del sitio web de la universidad.
    Gestiona todas las rutas y vistas públicas del sitio web.
    """

    def _get_theme_color(self, university_id: int) -> Dict[str, str]:
        """
        Obtiene los colores del tema para una universidad específica basado en su ID.
        
        Args:
            university_id (int): ID de la universidad
            
        Returns:
            Dict[str, str]: Diccionario con colores de fondo y borde
            
        Example:
            >>> self._get_theme_color(1)
            {'bg': '#e8f4f2', 'border': '#92d3c7'}
        """
        THEME_COLORS = {
            0: {'bg': '#ffecee', 'border': '#ff9eaa'},  # Rosa suave
            1: {'bg': '#e8f4f2', 'border': '#92d3c7'},  # Verde menta
            2: {'bg': '#fff4e3', 'border': '#ffd699'},  # Amarillo pastel
            3: {'bg': '#eae4f2', 'border': '#b39ddb'},  # Púrpura suave
            4: {'bg': '#e3f2ff', 'border': '#90caf9'},  # Azul claro
            5: {'bg': '#f0f8e5', 'border': '#aed581'}   # Verde lima
        }
        return THEME_COLORS[university_id % 6]

    @http.route('/universities', type='http', auth='public', website=True)
    def list_universities(self, **kw: Any) -> str:
        """
        Muestra la lista de todas las universidades en el sitio web.
        Incluye funcionalidad de búsqueda.
        """
        domain = []
        search_term = kw.get('search', '').strip()
        
        if search_term:
            domain = [
                '|',
                ('name', 'ilike', search_term),
                ('city', 'ilike', search_term)
            ]
        
        universities = request.env['university.university'].sudo().search(domain)
        
        return request.render('Universidad.website_universities', {
            'universities': universities,
            'search': search_term,
        })

    @http.route('/professors/<int:university_id>', type='http', auth='public', website=True)
    def list_university_professors(self, university_id: int, **kw: Any) -> str:
        """
        Muestra los profesores de una universidad específica.
        
        Args:
            university_id (int): ID de la universidad a mostrar
            
        Returns:
            str: Template renderizado con los profesores de la universidad
            
        Route: /professors/<university_id>
        Auth: public
        """
        University = request.env['university.university'].sudo()
        Professor = request.env['university.professor'].sudo()

        university = University.browse(university_id)
        professors = Professor.search([('university_id', '=', university_id)])
        
        return request.render('Universidad.website_professors', {
            'professors': professors,
            'university': university,
        })
    
    @http.route('/professors', type='http', auth='public', website=True)
    def list_all_professors(self, **kw: Any) -> str:
        """Display all professors grouped by university"""
        University = request.env['university.university'].sudo()
        Professor = request.env['university.professor'].sudo()

        universities = University.search([])
        professors_by_university = {}
        university_colors = {}
        
        for university in universities:
            professors = Professor.search([('university_id', '=', university.id)])
            if professors:
                professors_by_university[university] = professors
                university_colors[university.id] = self._get_theme_color(university.id)
        
        return request.render('Universidad.website_all_professors', {
            'universities': professors_by_university,
            'university_colors': university_colors,
        })

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

    @http.route('/my/grades', type='http', auth='user', website=True)
    def show_portal_grades(self, **kw: Any) -> str:
        """Display grades in user portal"""
        user = request.env.user
        is_admin = user.has_group('base.group_system')
        
        # Redirigir si no es admin ni estudiante
        if not is_admin:
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            if not student:
                return request.redirect('/my')
        
        try:
            university_id = int(kw.get('university_id', 0))
        except (ValueError, TypeError):
            university_id = 0
            
        grade_filter = kw.get('grade_filter', 'all')
        domain = self._build_grades_domain(university_id, grade_filter)
        
        grades, universities = self._get_filtered_grades(user, is_admin, domain)
        
        return request.render('Universidad.portal_grades', {
            'grades': grades,
            'is_admin': is_admin,
            'universities': universities,
            'current_university': university_id,
            'current_filter': grade_filter
        })

    def _build_grades_domain(self, university_id: int, grade_filter: str) -> list:
        """Build search domain for grades"""
        domain = []
        if university_id:
            domain.append(('enrollment_id.university_id', '=', university_id))
        
        if grade_filter == 'passed':
            domain.append(('grade', '>=', 5.0))
        elif grade_filter == 'failed':
            domain.append(('grade', '<', 5.0))
            
        return domain

    def _get_filtered_grades(self, user, is_admin: bool, domain: list) -> tuple:
        """Get grades based on user permissions"""
        Grade = request.env['university.grade'].sudo()
        University = request.env['university.university'].sudo()
        
        if is_admin:
            grades = Grade.search(domain)
            universities = University.search([])
        else:
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            
            if not student:
                raise AccessError("No student record found for current user")
                
            domain.append(('student_id', '=', student.id))
            grades = Grade.search(domain)
            universities = University.search([
                ('id', 'in', grades.mapped('enrollment_id.university_id').ids)
            ])
            
        return grades, universities

    def _get_external_news(self) -> list:
        """Get external education news links"""
        return [
            {
                'title': 'Latest Education News',
                'description': 'Stay updated with the latest news in education.',
                'link': 'https://www.educationweek.org/',
                'source': 'Education Week',
                'category': 'education'
            },
            {
                'title': 'World University Rankings',
                'description': 'Check the latest university rankings worldwide.',
                'link': 'https://www.timeshighereducation.com/world-university-rankings',
                'source': 'Times Higher Education',
                'category': 'rankings'
            },
            {
                'title': 'Research & Innovation',
                'description': 'Discover the latest research trends and innovations.',
                'link': 'https://www.sciencedaily.com/',
                'source': 'Science Daily',
                'category': 'research'
            }
        ]

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw: Any) -> str:
        """Display homepage with external news"""
        return request.render('Universidad.website_homepage', {
            'stats': self._get_university_stats(),
            'featured_universities': self._get_featured_universities(),
            'external_news': self._get_external_news()
        })

    def _get_university_stats(self) -> Dict[str, int]:
        """Get statistics for homepage"""
        return {
            'university_count': request.env['university.university'].sudo().search_count([]),
            'professor_count': request.env['university.professor'].sudo().search_count([]),
            'student_count': request.env['university.student'].sudo().search_count([]),
            'department_count': request.env['university.department'].sudo().search_count([])
        }

    def _get_featured_universities(self, limit: int = 3):
        """Get featured universities"""
        return request.env['university.university'].sudo().search([], limit=limit)

    def _get_languages(self):
        """Get available languages for the website"""
        return request.env['res.lang'].sudo().search([
            ('active', '=', True),
            ('code', 'in', ['es_ES', 'en_US'])  # Solo español e inglés
        ])

    @http.route(['/'], type='http', auth="public", website=True)
    def index(self, **kw):
        # Establecer el idioma predeterminado solo si no está configurado en la sesión
        if request.env.user._is_public() and not request.session.get('lang'):
            lang = request.env['res.lang'].search([('code', '=', 'es_ES')])
            if lang:
                request.session['lang'] = 'es_ES'
                request.session['frontend_lang'] = 'es_ES'
        
        # Respetar el idioma seleccionado en la sesión
        if request.session.get('lang'):
            request.env.context = dict(request.env.context, lang=request.session['lang'])
        
        return request.render('Universidad.website_homepage', {
            'stats': self._get_university_stats(),
            'featured_universities': self._get_featured_universities(),
            'external_news': self._get_external_news()
        })

    @http.route('/change_lang/<string:lang_code>', type='http', auth='public', website=True)
    def change_language(self, lang_code, **kw):
        """Change website language"""
        if lang_code:
            # Verificar si el idioma está activo
            lang = request.env['res.lang'].sudo().search([
                ('code', '=', lang_code),
                ('active', '=', True)
            ], limit=1)
            
            if lang:
                # Establecer el idioma en la sesión
                request.session.update({
                    'lang': lang_code,
                    'frontend_lang': lang_code
                })
                
                # Actualizar el idioma del usuario si está autenticado
                if not request.env.user._is_public():
                    request.env.user.sudo().write({'lang': lang_code})
                
                # Redireccionar con la cookie establecida
                response = request.redirect(kw.get('r', '/'))
                response.set_cookie('frontend_lang', lang_code)
                return response
        
        return request.redirect('/')

