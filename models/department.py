# models/department.py
from odoo import models, fields

class UniversityDepartment(models.Model):
    _name = 'university.department'
    _description = 'University Department'

    name = fields.Char(string='Name', required=True)
    university_id = fields.Many2one('university.university', string='University', required=True)
    head_id = fields.Many2one('university.professor', string='Department Head')

    professor_ids = fields.One2many('university.professor', 'department_id', string='Professors')

