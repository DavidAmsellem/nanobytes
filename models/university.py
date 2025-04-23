# Importa los módulos necesarios de Odoo
from odoo import models, fields

# Define la clase Universidad
class University(models.Model):
    # Nombre técnico del modelo en la base de datos
    _name = 'university.university'
    # Descripción del modelo para la interfaz de usuario
    _description = 'University'

    # Campo obligatorio para el nombre de la universidad
    name = fields.Char(string='Name', required=True)
    
    # Campo para almacenar la imagen de la universidad con dimensiones máximas
    image_1920 = fields.Image("Image", max_width=1920, max_height=1080)

    # Campos para la dirección de la universidad
    street = fields.Char(string='Street')     # Calle
    city = fields.Char(string='City')         # Ciudad
    zip = fields.Char(string='ZIP')           # Código postal
    state_id = fields.Many2one('res.country.state', string='State')    # Estado/Provincia
    country_id = fields.Many2one('res.country', string='Country')      # País

    # Relación con el director de la universidad
    director_id = fields.Many2one('university.professor', string='Director')

    # Relaciones y contadores para registros relacionados
    # Matrículas
    enrollment_ids = fields.One2many('university.enrollment', 'university_id', string='Enrollments')
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')

    # Estudiantes
    student_ids = fields.One2many('university.student', 'university_id', string='Students')
    student_count = fields.Integer(string='Student Count', compute='_compute_student_count')

    # Profesores
    professor_ids = fields.One2many('university.professor', 'university_id', string='Professors')
    professor_count = fields.Integer(string='Professor Count', compute='_compute_professor_count')

    # Departamentos
    department_ids = fields.One2many('university.department', 'university_id', string='Departments')
    department_count = fields.Integer(string='Department Count', compute='_compute_department_count')

    # Método para calcular el número de matrículas
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    # Método para calcular el número de estudiantes
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    # Método para calcular el número de profesores
    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

        # Método para calcular el número de departamentos
    def _compute_department_count(self):
        for record in self:
            record.department_count = len(record.department_ids)



    # Acción para ver la lista de profesores de la universidad (mostrandolo en lista)
    def action_view_professors(self):
        return {
            'type': 'ir.actions.act_window',      # Tipo de acción
            'name': 'Professors',                  # Título de la ventana
            'res_model': 'university.professor',   # Modelo a mostrar
            'view_mode': 'list',             # Modos de vista disponibles
            'domain': [('university_id', '=', self.id)],  # Filtro de registros
            'context': {'default_university_id': self.id},  # Contexto por defecto
            'target': 'current',                  # Destino de la ventana
        }

    # Acción para ver la lista de estudiantes de la universidad (mostrando los list)
    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',  #Tipo de accion 
            'name': 'Students',                         #Titulo de la venatana
            'res_model': 'university.student',     # Modelo a mostrar
            'view_mode': 'list',      # Modelos de vistas a mostrar
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',                    # Destino de la ventana (esta)
        } 

    # Acción para ver la lista de departamentos de la universidad (mostrando en kanban)
    def action_view_departments(self):
        return {
            'type': 'ir.actions.act_window',  #Tipo de accion
            'name': 'Departments',              # Titulo de la ventana
            'res_model': 'university.department',   # Modelo a mostrar
            'view_mode': 'kanban',   #Modelos de vista a mostrar
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    # Acción para ver la lista de matrículas de la universidad (mostrando en lista)
    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }




