from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class UniversityEnrollment(models.Model):
    """
    Model representing student enrollments in university subjects.
    Manages the enrollment process including relationships between students, 
    subjects, professors, and universities.
    """
    _name = 'university.enrollment'
    _description = 'University Enrollment'
    _order = 'name'

    name = fields.Char(
        string="Enrollment Number",
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help="Unique enrollment identifier"
    )
    
    student_id = fields.Many2one(
        'university.student',
        string='Student',
        required=True,
        help="Student enrolled in the subject"
    )
    
    university_id = fields.Many2one(
        'university.university',
        string='University',
        compute='_compute_university',
        store=True,
        readonly=True,
        help="University where the enrollment takes place"
    )
    
    subject_id = fields.Many2one(
        'university.subject',
        string='Subject',
        required=True,
        domain="[('university_id', '=', university_id)]",
        help="Subject in which the student is enrolled"
    )
    
    professor_id = fields.Many2one(
        'university.professor',
        string='Professor',
        compute='_compute_professor',
        store=True,
        help="Professor assigned to teach the subject"
    )
    
    department_id = fields.Many2one(
        'university.department',
        string='Department',
        related='subject_id.department_id',
        store=True,
        readonly=True,
        help="Department responsible for the subject"
    )

    date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        help="Date when the enrollment was created"
    )

    grade_ids = fields.One2many(
        'university.grade',
        'enrollment_id',
        string="Grades",
        help="Grades received for this enrollment"
    )
    
    available_professor_ids = fields.Many2many(
        'university.professor',
        string='Available Professors',
        related='subject_id.professor_ids',
        readonly=True,
        help="Professors available to teach this subject"
    )

    @api.depends('subject_id.professor_ids')
    def _compute_professor(self):
        """
        Computes the professor for the enrollment based on the subject's professors.
        Assigns the first available professor if any exists.
        """
        for record in self:
            record.professor_id = record.subject_id.professor_ids[0] if record.subject_id.professor_ids else False

    @api.depends('student_id', 'student_id.university_id')
    def _compute_university(self):
        """
        Computes the university for the enrollment based on the student's university.
        """
        for record in self:
            record.university_id = record.student_id.university_id if record.student_id else False

    @api.onchange('student_id')
    def _onchange_student(self):
        """
        Handles changes in the student field.
        Clears the subject if the universities don't match.
        """
        if self.student_id:
            if self.subject_id and self.subject_id.university_id != self.student_id.university_id:
                self.subject_id = False

    @api.constrains('student_id', 'subject_id')
    def _check_university_match(self):
        """
        Validates that the student and subject belong to the same university.
        
        Raises:
            ValidationError: If the student and subject universities don't match
        """
        for record in self:
            if record.student_id and record.subject_id:
                if record.student_id.university_id != record.subject_id.university_id:
                    raise ValidationError(_('Student and subject must belong to the same university.'))

    @api.model
    def create(self, vals):
        """
        Override of create method to generate enrollment numbers.
        
        Args:
            vals (dict): Values for creating the enrollment record
            
        Returns:
            record: Newly created enrollment record
        """
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


