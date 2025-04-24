# Importación de los módulos necesarios de Odoo
from odoo import models, fields, api, _  # _ para traducciones
from odoo.exceptions import ValidationError  # Para manejar errores de validación

# Definición de la clase Grade heredando de models.Model
class UniversityGrade(models.Model):
    """
    Model representing academic grades for university students.
    Manages the grading system including relationships with students, enrollments,
    and universities, along with grade values and dates.
    """
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
        required=True,              # Campo obligatorio
        help='Student who received the grade'
    )

    # Relación muchos a uno con la matrícula (obligatorio)
    enrollment_id = fields.Many2one(
        'university.enrollment',     # Modelo relacionado
        string='Enrollment',        # Etiqueta en la interfaz
        required=True,              # Campo obligatorio
        # Dominio dinámico: solo muestra matrículas del estudiante seleccionado
        domain="[('student_id', '=', student_id)]",
        help='Course enrollment associated with this grade'
    )

    # Universidad (obtenida a través de la matrícula)
    university_id = fields.Many2one(
        'university.university',     # Modelo relacionado
        string='University',        # Etiqueta en la interfaz
        related='enrollment_id.university_id',  # Campo relacionado
        store=True,                  # Almacenar en base de datos
        help='University where the grade was issued'
    )

    # Calificación numérica (obligatorio)
    grade = fields.Float(
        string='Grade',             # Etiqueta en la interfaz
        required=True,              # Campo obligatorio
        help='Numerical grade value'
    )

    # Fecha de la calificación
    date = fields.Date(
        string='Date',              # Etiqueta en la interfaz
        default=fields.Date.today,  # Fecha actual por defecto
        required=True,              # Campo obligatorio
        help='Date when the grade was issued'
    )

    # Método que se ejecuta al cambiar el estudiante
    @api.onchange('student_id')
    def _onchange_student(self):
        """
        Handles the change of student in the grade record.
        Clears the enrollment field and updates available enrollments
        based on the selected student.

        Returns:
            dict: Domain filter for enrollment field
        """
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
        """
        Validates the consistency between student and enrollment.
        Ensures that grades can only be assigned to enrollments
        that belong to the selected student.

        Raises:
            ValidationError: If the enrollment does not belong to the selected student
        """
        for record in self:
            # Comprueba que la matrícula pertenezca al estudiante
            if record.enrollment_id.student_id != record.student_id:
                # Lanza error si no coinciden
                raise ValidationError(_(
                    'You can only assign grades to enrollments of the same student.'
                ))

