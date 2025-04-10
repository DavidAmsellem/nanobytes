from odoo import models, fields, api
from datetime import datetime

class UniversityEnrollment(models.Model):
    _name = 'university.enrollment'
    _description = 'University Enrollment'
    _order = 'name'

    name = fields.Char(string="Enrollment Name", required=True, copy=False, readonly=True, default='New')
    
    student_id = fields.Many2one('university.student', string='Student', required=True)
    
    university_id = fields.Many2one(
        'university.university',
        string='University',
        compute='_compute_university',
        store=True,
        readonly=True
    )
    
    subject_id = fields.Many2one(
        'university.subject',
        string='Subject',
        required=True,
        domain="[('university_id', '=', university_id)]"
    )
    
    professor_id = fields.Many2one(
        'university.professor',
        string='Professor',
        compute='_compute_professor',
        store=True
    )
    
    department_id = fields.Many2one(
        'university.department',
        string='Department',
        related='subject_id.department_id',
        store=True,
        readonly=True
    )
    date = fields.Date(string="Enrollment Date", default=fields.Date.context_today)

    grade_ids = fields.One2many('university.grade', 'enrollment_id', string="Grades")
    
    available_professor_ids = fields.Many2many(
        'university.professor',
        string='Available Professors',
        related='subject_id.professor_ids',
        readonly=True
    )

    @api.depends('subject_id.professor_ids')
    def _compute_professor(self):
        for record in self:
            # Asignamos el primer profesor de la asignatura si existe
            record.professor_id = record.subject_id.professor_ids[0] if record.subject_id.professor_ids else False

    @api.depends('student_id', 'student_id.university_id')
    def _compute_university(self):
        for record in self:
            record.university_id = record.student_id.university_id if record.student_id else False

    @api.onchange('student_id')
    def _onchange_student(self):
        if self.student_id:
            # Limpiar subject_id si la universidad cambió
            if self.subject_id and self.subject_id.university_id != self.student_id.university_id:
                self.subject_id = False

    @api.constrains('student_id', 'subject_id')
    def _check_university_match(self):
        for record in self:
            if record.student_id and record.subject_id:
                if record.student_id.university_id != record.subject_id.university_id:
                    raise ValidationError('El estudiante y la asignatura deben pertenecer a la misma universidad.')

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


