# models/department.py
from odoo import models, fields, api

class UniversityDepartment(models.Model):
    _name = 'university.department'
    _description = 'University Department'

    name = fields.Char(string='Name', required=True)
    university_id = fields.Many2one('university.university', string='University', required=True)
    head_id = fields.Many2one('university.professor', string='Department Head')
    image_1920 = fields.Image("Image", max_width=1920, max_height=1080)
    professor_ids = fields.One2many('university.professor', 'department_id', string='Professors')
    
    # Añadir campo computado para el contador de profesores
    professor_count = fields.Integer(string='Professor Count', compute='_compute_professor_count')

    @api.depends('professor_ids')
    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

