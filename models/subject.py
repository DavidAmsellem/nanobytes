# Importación de módulos necesarios para trabajar con Odoo
from odoo import models, fields  # Importa los módulos para crear modelos y definir campos en Odoo

# Definición de la clase 'UniversitySubject', que representa las asignaturas en una universidad
class UniversitySubject(models.Model):
    _name = 'university.subject'  # Nombre técnico del modelo (usado en el código y la base de datos)
    _description = 'University Subject'  # Descripción del modelo, se usa en la interfaz de usuario

    # Definición de los campos del modelo
    name = fields.Char(string='Name', required=True)  # Nombre de la asignatura, es obligatorio
    university_id = fields.Many2one('university.university', string='University', required=True)  # Relación con la universidad (Many2one), es obligatorio

    # Relación de muchos a muchos con los profesores que imparten la asignatura
    professor_ids = fields.Many2many('university.professor', string='Professors')  # Los profesores que imparten esta asignatura

    # Relación de uno a muchos con las matrículas que están asociadas a esta asignatura
    enrollment_ids = fields.One2many('university.enrollment', 'subject_id', string='Enrollments')  # Matrículas asociadas a esta asignatura
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')  # Contador de matrículas

    # Campo para mostrar una imagen relacionada con la asignatura
    image_1920 = fields.Image(string="Image")  # Imagen asociada a la asignatura

    # Método computado para contar las matrículas de la asignatura
    def _compute_enrollment_count(self):
        for record in self:  # Itera sobre cada registro de asignatura
            record.enrollment_count = len(record.enrollment_ids)  # Calcula cuántas matrículas están asociadas a la asignatura

    # Acción para ver las matrículas asociadas a esta asignatura
    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',  # Tipo de acción para abrir una ventana
            'name': 'Enrollments',  # Nombre de la ventana
            'res_model': 'university.enrollment',  # Modelo de las matrículas
            'view_mode': 'list,form',  # Tipos de vista disponibles: lista y formulario
            'domain': [('subject_id', '=', self.id)],  # Filtra las matrículas por la asignatura actual
            'context': {'default_subject_id': self.id},  # Define un contexto con el id de la asignatura
            'target': 'current',  # La acción se abrirá en la ventana actual
        }
