from odoo import models, fields, api
from datetime import datetime

class UniversityEnrollment(models.Model):
    _name = 'university.enrollment'
    _description = 'University Enrollment'
    _order = 'name'

    name = fields.Char(string="Enrollment Name", required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('university.student', string='Student', required=True)
    subject_id = fields.Many2one('university.subject', string='Subject', required=True)
    professor_id = fields.Many2one('university.professor', string='Professor')
    university_id = fields.Many2one('university.university', string='University', required=True)
    date = fields.Date(string="Enrollment Date", default=fields.Date.context_today)

    grade_ids = fields.One2many('university.grade', 'enrollment_id', string="Grades")  # ← Añadido

    
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            subject_id = vals.get('subject_id')
            date_val = vals.get('date')
            year = datetime.strptime(date_val, "%Y-%m-%d").year if date_val else datetime.today().year

            subject = self.env['university.subject'].browse(subject_id)
            prefix = subject.name[:3].upper() if subject else "UNK"

            count = self.search_count([
                ('subject_id', '=', subject_id),
                ('date', '>=', f"{year}-01-01"),
                ('date', '<=', f"{year}-12-31")
            ]) + 1

            seq = str(count).zfill(4)
            vals['name'] = f"{prefix}/{year}/{seq}"

        return super(UniversityEnrollment, self).create(vals)


