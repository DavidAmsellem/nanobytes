from odoo import http
from odoo.http import request

# Define el controlador principal para el sitio web de la universidad
class UniversityWebsiteController(http.Controller):

    # Ruta para mostrar la lista de universidades
    @http.route('/universidad', auth='public', website=True)  # Define la ruta como pública y parte del sitio web
    def list_universities(self, **kw):  # Método que maneja las peticiones a /universidad
        # Obtiene todas las universidades usando permisos de superusuario
        universities = request.env['university.university'].sudo().search([])
        
        # Renderiza la plantilla pasando las universidades como contexto
        return request.render('Universidad.website_universities', {
            'universities': universities,
        })

    # Ruta para mostrar los profesores de una universidad específica
    @http.route('/profesores/<int:university_id>', auth='public', website=True)  # La ruta incluye un parámetro dinámico
    def list_professors(self, university_id, **kw):  # Recibe el ID de la universidad como parámetro
        # Busca los profesores que pertenecen a la universidad especificada
        professors = request.env['university.professor'].sudo().search([
            ('university_id', '=', university_id)
        ])
        
        # Obtiene el objeto universidad correspondiente
        university = request.env['university.university'].sudo().browse(university_id)
        
        # Renderiza la plantilla con los profesores y la universidad
        return request.render('Universidad.website_professors', {
            'professors': professors,
            'university': university,
        })
    
    # Ruta para mostrar todos los profesores
    @http.route('/profesores', auth='public', website=True)  # Ruta pública para listar todos los profesores
    def all_professors(self, **kw):
        # Obtiene todos los profesores del sistema
        professors = request.env['university.professor'].sudo().search([])
        
        # Renderiza la plantilla con la lista completa de profesores
        return request.render('Universidad.website_all_professors', {
            'professors': professors,
        })

    # Ruta para mostrar las calificaciones en el portal
    @http.route('/my/grades', type='http', auth='user', website=True)  # Ruta que requiere autenticación
    def portal_my_grades(self, **kw):
        # Obtiene el usuario actual
        user = request.env.user
        # Verifica si el usuario es administrador
        is_admin = user.has_group('base.group_system')
        
        # Maneja de forma segura el parámetro de universidad
        try:
            university_id = int(kw.get('university_id', 0))
        except (ValueError, TypeError):
            university_id = 0
            
        # Obtiene el filtro de calificaciones (todas, aprobadas, suspendidas)
        grade_filter = kw.get('grade_filter', 'all')
        
        # Construye el dominio para la búsqueda
        domain = []
        # Añade filtro por universidad si se especifica
        if university_id:
            domain.append(('enrollment_id.university_id', '=', university_id))
        
        # Añade filtros por nota según el criterio seleccionado
        if grade_filter == 'passed':
            domain.append(('grade', '>=', 5.0))
        elif grade_filter == 'failed':
            domain.append(('grade', '<', 5.0))
        
        # Lógica diferente para administradores y estudiantes
        if is_admin:
            # Administrador puede ver todas las notas
            grades = request.env['university.grade'].sudo().search(domain)
            universities = request.env['university.university'].sudo().search([])
        else:
            # Busca el estudiante asociado al usuario
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            
            # Si no es estudiante, redirige al portal
            if not student:
                return request.redirect('/my')
                
            # Añade filtro para mostrar solo las notas del estudiante
            domain.append(('student_id', '=', student.id))
            grades = request.env['university.grade'].sudo().search(domain)
            # Obtiene solo las universidades donde el estudiante tiene notas
            universities = request.env['university.university'].sudo().search([
                ('id', 'in', grades.mapped('enrollment_id.university_id').ids)
            ])
        
        # Renderiza la plantilla con todos los datos necesarios
        return request.render('Universidad.portal_grades', {
            'grades': grades,
            'is_admin': is_admin,
            'universities': universities,
            'current_university': university_id,
            'current_filter': grade_filter
        })

