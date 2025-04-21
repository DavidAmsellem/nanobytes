# models/department.py
# Importación de los módulos necesarios de Odoo
from odoo import models, fields, api

# Definición de la clase del modelo heredando de models.Model
class UniversityDepartment(models.Model):
    # Nombre técnico del modelo en la base de datos
    _name = 'university.department'
    # Descripción del modelo para la interfaz de usuario
    _description = 'University Department'

    # Campo básico para el nombre del departamento (obligatorio)
    name = fields.Char(
        string='Name',          # Etiqueta que se muestra en la interfaz
        required=True           # Campo obligatorio
    )

    # Relación muchos a uno con el modelo university.university
    university_id = fields.Many2one(
        'university.university',    # Modelo relacionado
        string='University',        # Etiqueta en la interfaz
        required=True,             # Campo obligatorio
        ondelete='restrict'        # Evita eliminar si hay registros relacionados
    )

    # Relación muchos a uno con el modelo university.professor (jefe de departamento)
    head_id = fields.Many2one(
        'university.professor',     # Modelo relacionado
        string='Department Head',   # Etiqueta en la interfaz
        ondelete='restrict'        # Evita eliminar si hay registros relacionados
    )

    # Campo para almacenar la imagen del departamento
    image_1920 = fields.Image(
        "Image",                   # Etiqueta en la interfaz
        max_width=1920,           # Ancho máximo de la imagen
        max_height=1080           # Alto máximo de la imagen
    )

    # Relación uno a muchos con profesores (inversa de department_id en professor)
    professor_ids = fields.One2many(
        'university.professor',     # Modelo relacionado
        'department_id',           # Campo relacionado en el otro modelo
        string='Professors'        # Etiqueta en la interfaz
    )

    # Campo computado para contar profesores
    professor_count = fields.Integer(
        string='Professor Count',   # Etiqueta en la interfaz
        compute='_compute_professor_count'  # Método que calcula el valor
    )

    # Método que calcula el número de profesores
    @api.depends('professor_ids')   # Se recalcula cuando cambia professor_ids
    def _compute_professor_count(self):
        for record in self:
            # Cuenta el número de registros en professor_ids
            record.professor_count = len(record.professor_ids)

