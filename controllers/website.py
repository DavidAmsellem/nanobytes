from odoo import http


from odoo.http import request


# Define una clase que actuará como controlador de rutas web en el módulo Universidad
class UniversityWebsiteController(http.Controller):

    # Define una ruta pública (accesible a todos) que muestra todas las universidades
    @http.route('/universidad', auth='public', website=True)
    def list_universities(self, **kw):
        # Busca todos los registros del modelo 'university.university' con permisos de superusuario
        universities = request.env['university.university'].sudo().search([])
        
        # Renderiza la plantilla XML 'Universidad.website_universities' y le pasa la lista de universidades
        return request.render('Universidad.website_universities', {
            'universities': universities,
        })

    # Define una ruta pública para mostrar los profesores de una universidad específica
    @http.route('/profesores/<int:university_id>', auth='public', website=True)
    def list_professors(self, university_id, **kw):
        # Busca todos los profesores que pertenecen a la universidad con el ID recibido por la URL
        professors = request.env['university.professor'].sudo().search([
            ('university_id', '=', university_id)
        ])
        
        # Recupera el objeto universidad correspondiente al ID recibido
        university = request.env['university.university'].sudo().browse(university_id)
        
        # Renderiza la plantilla XML 'Universidad.website_professors' y pasa los profesores y la universidad
        return request.render('Universidad.website_professors', {
            'professors': professors,
            'university': university,
        })
    
    # Define una ruta pública que muestra todos los profesores del sistema
    @http.route('/profesores', auth='public', website=True)
    def all_professors(self, **kw):
        # Busca todos los registros del modelo 'university.professor'
        professors = request.env['university.professor'].sudo().search([])
        
        # Renderiza la plantilla XML 'Universidad.website_all_professors' y le pasa los profesores
        return request.render('Universidad.website_all_professors', {
            'professors': professors,
        })

    # Define una ruta privada (requiere login) para que el estudiante vea sus propias notas
    @http.route('/my/grades', type='http', auth='user', website=True)
    def portal_my_grades(self, **kw):
        user = request.env.user
        is_admin = user.has_group('base.group_system')
        
        # Manejo seguro del valor de university_id
        try:
            university_id = int(kw.get('university_id', 0))
        except (ValueError, TypeError):
            university_id = 0
            
        grade_filter = kw.get('grade_filter', 'all')
        
        domain = []
        if university_id:  # Solo añade el filtro si university_id es diferente de 0
            domain.append(('enrollment_id.university_id', '=', university_id))
        
        if grade_filter == 'passed':
            domain.append(('grade', '>=', 5.0))
        elif grade_filter == 'failed':
            domain.append(('grade', '<', 5.0))
        
        if is_admin:
            grades = request.env['university.grade'].sudo().search(domain)
            universities = request.env['university.university'].sudo().search([])
        else:
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            
            if not student:
                return request.redirect('/my')
                
            domain.append(('student_id', '=', student.id))
            grades = request.env['university.grade'].sudo().search(domain)
            universities = request.env['university.university'].sudo().search([
                ('id', 'in', grades.mapped('enrollment_id.university_id').ids)
            ])
        
        return request.render('Universidad.portal_grades', {
            'grades': grades,
            'is_admin': is_admin,
            'universities': universities,
            'current_university': university_id,
            'current_filter': grade_filter
        })

