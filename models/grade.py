# models/grade.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class UniversityGrade(models.Model):
    _name = 'university.grade'
    _description = 'University Grade'
    _order = 'date desc'

    student_id = fields.Many2one('university.student', string='Student', required=True)
    enrollment_id = fields.Many2one(
        'university.enrollment', 
        string='Enrollment',
        required=True,
        domain="[('student_id', '=', student_id)]"
    )
    university_id = fields.Many2one(
        'university.university', 
        string='University',
        related='enrollment_id.university_id',
        store=True
    )
    grade = fields.Float(string='Grade', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)

    @api.onchange('student_id')
    def _onchange_student(self):
        """Limpia la matrícula si cambia el estudiante"""
        self.enrollment_id = False
        return {
            'domain': {
                'enrollment_id': [('student_id', '=', self.student_id.id)]
            }
        }

    @api.constrains('enrollment_id', 'student_id')
    def _check_student_enrollment(self):
        """Verifica que la nota corresponda a una matrícula del estudiante"""
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError(_(
                    'Solo puedes asignar notas a matrículas del mismo estudiante.'
                ))

