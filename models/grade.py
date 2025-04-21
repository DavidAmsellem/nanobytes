# Importación de los módulos necesarios de Odoo
from odoo import models, fields, api, _  # _ para traducciones
from odoo.exceptions import ValidationError  # Para manejar errores de validación

# Definición de la clase Grade heredando de models.Model
class UniversityGrade(models.Model):
    # Nombre técnico del modelo en la base de datos
    _name = 'university.grade'
    # Descripción del modelo para la interfaz de usuario
    _description = 'University Grade'
    # Orden por defecto de los registros (por fecha descendente)
    _order = 'date desc'

    # Relación muchos a uno con el estudiante (obligatorio)
    student_id = fields.Many2one(
        'university.student',        # Modelo relacionado
        string='Student',           # Etiqueta en la interfaz
        required=True               # Campo obligatorio
    )

    # Relación muchos a uno con la matrícula (obligatorio)
    enrollment_id = fields.Many2one(
        'university.enrollment',     # Modelo relacionado
        string='Enrollment',        # Etiqueta en la interfaz
        required=True,              # Campo obligatorio
        # Dominio dinámico: solo muestra matrículas del estudiante seleccionado
        domain="[('student_id', '=', student_id)]"
    )

    # Universidad (obtenida a través de la matrícula)
    university_id = fields.Many2one(
        'university.university',     # Modelo relacionado
        string='University',        # Etiqueta en la interfaz
        related='enrollment_id.university_id',  # Campo relacionado
        store=True                  # Almacenar en base de datos
    )

    # Calificación numérica (obligatorio)
    grade = fields.Float(
        string='Grade',             # Etiqueta en la interfaz
        required=True               # Campo obligatorio
    )

    # Fecha de la calificación
    date = fields.Date(
        string='Date',              # Etiqueta en la interfaz
        default=fields.Date.today,  # Fecha actual por defecto
        required=True               # Campo obligatorio
    )

    # Método que se ejecuta al cambiar el estudiante
    @api.onchange('student_id')
    def _onchange_student(self):
        """Limpia la matrícula si cambia el estudiante"""
        # Reinicia el campo de matrícula
        self.enrollment_id = False
        # Actualiza el dominio de matrículas disponibles
        return {
            'domain': {
                'enrollment_id': [('student_id', '=', self.student_id.id)]
            }
        }

    # Validación de consistencia entre estudiante y matrícula
    @api.constrains('enrollment_id', 'student_id')
    def _check_student_enrollment(self):
        """Verifica que la nota corresponda a una matrícula del estudiante"""
        for record in self:
            # Comprueba que la matrícula pertenezca al estudiante
            if record.enrollment_id.student_id != record.student_id:
                # Lanza error si no coinciden
                raise ValidationError(_(
                    'Solo puedes asignar notas a matrículas del mismo estudiante.'
                ))

