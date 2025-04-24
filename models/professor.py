# Importamos los módulos necesarios de Odoo para modelos, campos y decoradores API
from odoo import models, fields, api

# Definimos la clase Profesor que hereda de models.Model
class UniversityProfessor(models.Model):
    # Nombre técnico del modelo en la base de datos
    _name = 'university.professor'
    # Descripción del modelo para la interfaz de usuario
    _description = 'University Professor'

    # Campo básico para el nombre del profesor (obligatorio)
    name = fields.Char(
        string='Name',          # Etiqueta en la interfaz
        required=True           # Campo obligatorio
    )
    
    # Campo para la imagen del profesor con dimensiones máximas
    image_1920 = fields.Image(
        "Image",                # Etiqueta en la interfaz
        max_width=1920,         # Ancho máximo permitido
        max_height=1080         # Alto máximo permitido
    )

    # Relación muchos a uno con la universidad (obligatorio)
    university_id = fields.Many2one(
        'university.university', # Modelo relacionado
        string='University',     # Etiqueta en la interfaz
        required=True           # Campo obligatorio
    )
    
    # Relación muchos a uno con el departamento
    department_id = fields.Many2one(
        'university.department', # Modelo relacionado
        string='Department'      # Etiqueta en la interfaz
    )
    
    # Relación muchos a muchos con asignaturas
    subject_ids = fields.Many2many(
        'university.subject',    # Modelo relacionado
        string='Subjects'        # Etiqueta en la interfaz
    )

    # Relación uno a muchos con matrículas
    enrollment_ids = fields.One2many(
        'university.enrollment', # Modelo relacionado
        'professor_id',         # Campo relacionado en el otro modelo
        string='Enrollments'    # Etiqueta en la interfaz
    )
    
    # Campo computado para contar matrículas
    enrollment_count = fields.Integer(
        string='Enrollment Count',    # Etiqueta en la interfaz
        compute='_compute_enrollment_count'  # Método que calcula el valor
    )

    # Método que calcula el número de matrículas
    @api.depends('enrollment_ids')   # Se recalcula cuando cambian las matrículas
    def _compute_enrollment_count(self):
        for prof in self:
            # Cuenta el número de matrículas del profesor
            prof.enrollment_count = len(prof.enrollment_ids)

    # Acción para ver las matrículas del profesor
    def action_view_enrollments(self):
        """Abre una vista con las matrículas del profesor"""
        return {
            'type': 'ir.actions.act_window',    # Tipo de acción
            'name': 'Enrollments',              # Título de la ventana
            'res_model': 'university.enrollment', # Modelo a mostrar
            'view_mode': 'list,form',           # Modos de vista disponibles
            'domain': [
                ('professor_id', '=', self.id)  # Filtro para mostrar solo las matrículas del profesor
            ],
            'context': {
                'default_professor_id': self.id  # Valor por defecto al crear nuevos registros
            },
        }



