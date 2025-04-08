# models/grade.py
from odoo import models, fields

class UniversityGrade(models.Model):
    _name = 'university.grade'
    _description = 'University Grade'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    enrollment_id = fields.Many2one('university.enrollment', string='Enrollment', required=True)
    grade = fields.Float(string='Grade')

