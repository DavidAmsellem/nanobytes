# Importamos los módulos necesarios de Odoo y Python
from odoo import models, fields, api
from datetime import datetime

class UniversityEnrollment(models.Model):
    # Nombre técnico del modelo en la base de datos
    _name = 'university.enrollment'
    # Descripción del modelo para la interfaz de usuario
    _description = 'University Enrollment'
    # Orden por defecto de los registros
    _order = 'name'

    # Campo para el número de matrícula (autogenerado)
    name = fields.Char(
        string="Enrollment Name",    # Etiqueta en la interfaz
        required=True,              # Campo obligatorio
        copy=False,                 # No se copia al duplicar
        readonly=True,              # Solo lectura
        default='New'               # Valor por defecto
    )
    
    # Relación con el estudiante
    student_id = fields.Many2one(
        'university.student',        # Modelo relacionado
        string='Student',           # Etiqueta en la interfaz
        required=True               # Campo obligatorio
    )
    
    # Universidad (calculada desde el estudiante)
    university_id = fields.Many2one(
        'university.university',     # Modelo relacionado
        string='University',        # Etiqueta en la interfaz
        compute='_compute_university', # Método de cálculo
        store=True,                 # Almacenar en base de datos
        readonly=True               # Solo lectura
    )
    
    # Asignatura a la que se matricula
    subject_id = fields.Many2one(
        'university.subject',        # Modelo relacionado
        string='Subject',           # Etiqueta en la interfaz
        required=True,              # Campo obligatorio
        domain="[('university_id', '=', university_id)]"  # Filtro dinámico
    )
    
    # Profesor asignado (calculado desde la asignatura)
    professor_id = fields.Many2one(
        'university.professor',      # Modelo relacionado
        string='Professor',         # Etiqueta en la interfaz
        compute='_compute_professor', # Método de cálculo
        store=True                  # Almacenar en base de datos
    )
    
    # Departamento (relación relacionada desde asignatura)
    department_id = fields.Many2one(
        'university.department',     # Modelo relacionado
        string='Department',        # Etiqueta en la interfaz
        related='subject_id.department_id', # Campo relacionado
        store=True,                # Almacenar en base de datos
        readonly=True              # Solo lectura
    )

    # Fecha de matrícula
    date = fields.Date(
        string="Enrollment Date",   # Etiqueta en la interfaz
        default=fields.Date.context_today  # Fecha actual por defecto
    )

    # Notas asociadas a esta matrícula
    grade_ids = fields.One2many(
        'university.grade',         # Modelo relacionado
        'enrollment_id',           # Campo relacionado en el otro modelo
        string="Grades"            # Etiqueta en la interfaz
    )
    
    # Profesores disponibles para la asignatura
    available_professor_ids = fields.Many2many(
        'university.professor',     # Modelo relacionado
        string='Available Professors', # Etiqueta en la interfaz
        related='subject_id.professor_ids', # Campo relacionado
        readonly=True              # Solo lectura
    )

    # Método para calcular el profesor
    @api.depends('subject_id.professor_ids')
    def _compute_professor(self):
        for record in self:
            # Asigna el primer profesor de la asignatura si existe
            record.professor_id = record.subject_id.professor_ids[0] if record.subject_id.professor_ids else False

    # Método para calcular la universidad
    @api.depends('student_id', 'student_id.university_id')
    def _compute_university(self):
        for record in self:
            # Asigna la universidad del estudiante
            record.university_id = record.student_id.university_id if record.student_id else False

    # Método que se ejecuta al cambiar el estudiante
    @api.onchange('student_id')
    def _onchange_student(self):
        if self.student_id:
            # Limpia la asignatura si la universidad no coincide
            if self.subject_id and self.subject_id.university_id != self.student_id.university_id:
                self.subject_id = False

    # Validación de universidad coincidente
    @api.constrains('student_id', 'subject_id')
    def _check_university_match(self):
        for record in self:
            if record.student_id and record.subject_id:
                # Verifica que estudiante y asignatura sean de la misma universidad
                if record.student_id.university_id != record.subject_id.university_id:
                    raise ValidationError('El estudiante y la asignatura deben pertenecer a la misma universidad.')

    # Sobrescribe el método create para generar número de matrícula
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            # Obtiene datos necesarios
            subject_id = vals.get('subject_id')
            date_val = vals.get('date')
            year = datetime.strptime(date_val, "%Y-%m-%d").year if date_val else datetime.today().year

            # Obtiene el prefijo de la asignatura
            subject = self.env['university.subject'].browse(subject_id)
            prefix = subject.name[:3].upper() if subject else "UNK"

            # Calcula el siguiente número de secuencia
            count = self.search_count([
                ('subject_id', '=', subject_id),
                ('date', '>=', f"{year}-01-01"),
                ('date', '<=', f"{year}-12-31")
            ]) + 1

            # Genera el número de matrícula
            seq = str(count).zfill(4)
            vals['name'] = f"{prefix}/{year}/{seq}"

        return super(UniversityEnrollment, self).create(vals)


