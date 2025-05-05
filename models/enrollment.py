from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

# Definition of the UniversityEnrollment model
class UniversityEnrollment(models.Model):
    """
    Model representing student enrollments in university subjects.
    Manages the enrollment process including relationships between students, 
    subjects, professors, and universities.
    """
    _name = 'university.enrollment'  # Technical name of the model
    _description = 'University Enrollment'  # Human-readable description
    _order = 'name'  # Default sorting order

    name = fields.Char(
        string="Enrollment Number",  # Label shown in the UI
        required=True,  # Field is mandatory
        copy=False,  # Do not copy this field on record duplication
        readonly=True,  # Read-only field
        default='New',  # Default value
        help="Unique enrollment identifier"  
    )
    
    student_id = fields.Many2one( #relacion con estudiante
        'university.student',     #estudiante puede tener varias matriculas
        string='Student',  # Label shown in the UI
        required=True,  # Field is mandatory
        help="Student enrolled in the subject"  # Tooltip help text
    )
    
    university_id = fields.Many2one(
        'university.university',  #relacion con universidad
        string='University',    #la universidad puede tener varias matriculas
        compute='_compute_university',  # Computed field
        store=True,  # Store in database
        readonly=True,  # Read-only field
        help="University where the enrollment takes place"  # Tooltip help text
    )
    
    subject_id = fields.Many2one(
        'university.subject',  #relacion con asignatura
        string='Subject',  # una asignatura puede tener varias matriculas
        required=True,  # Field is mandatory
        domain="[('university_id', '=', university_id)]",  # Filter based on university
        help="Subject in which the student is enrolled"  # Tooltip help text
    )
    
    professor_id = fields.Many2one(
        'university.professor',  # relacion con profesores
        string='Professor',  # los profesores pueden tener varias matriculas
        compute='_compute_professor',  # Computed field
        store=True,  # Store in database
        help="Professor assigned to teach the subject"  # Tooltip help text
    )
    
    department_id = fields.Many2one(
        'university.department',  # Related model: department
        string='Department',  # Los departamentos pueden tener varias matriculas
        related='subject_id.department_id',  # Fetched from subject
        store=True,  # Store in database
        readonly=True,  # Read-only field
        help="Department responsible for the subject"  # Tooltip help text
    )

    date = fields.Date(
        string="Enrollment Date",  # Label shown in the UI
        default=fields.Date.context_today,  # Default to today's date
        help="Date when the enrollment was created"  # Tooltip help text
    )

    grade_ids = fields.One2many(
        'university.grade',  # Related model: grade
        'enrollment_id',  # Una matricula puede tener varias notas
        string="Grades",  # Label shown in the UI
        help="Grades received for this enrollment"  # Tooltip help text
    )
    
    available_professor_ids = fields.Many2many(
        'university.professor',  # Related model: professor
        string='Available Professors',  # Label shown in the UI
        related='subject_id.professor_ids',  # Fetched from subject
        readonly=True,  # Read-only field
        help="Professors available to teach this subject"  # Tooltip help text
    )

    @api.depends('subject_id.professor_ids')  # Trigger when subject professors change
    def _compute_professor(self):
        """
        Computes the professor for the enrollment based on the subject's professors.
        Assigns the first available professor if any exists.
        """
        for record in self:
            record.professor_id = record.subject_id.professor_ids[0] if record.subject_id.professor_ids else False  # Set first professor or False

    @api.depends('student_id', 'student_id.university_id')  # Trigger when student or their university changes
    def _compute_university(self):
        """
        Computes the university for the enrollment based on the student's university.
        """
        for record in self:
            record.university_id = record.student_id.university_id if record.student_id else False  # Set university or False

    @api.onchange('student_id')  # Trigger on student change in form view
    def _onchange_student(self):
        """
        Handles changes in the student field.
        Clears the subject if the universities don't match.
        """
        if self.student_id:
            if self.subject_id and self.subject_id.university_id != self.student_id.university_id:
                self.subject_id = False  # Clear subject if mismatch

    @api.constrains('student_id', 'subject_id')  # Constraint on student and subject fields
    def _check_university_match(self):
        """
        Validates that the student and subject belong to the same university.
        
        Raises:
            ValidationError: If the student and subject universities don't match.
        """
        for record in self:
            if record.student_id and record.subject_id:
                if record.student_id.university_id != record.subject_id.university_id:
                    raise ValidationError(_('Student and subject must belong to the same university.'))  # Raise error if mismatch

    @api.model  # Indicates this method is a model method
    def create(self, vals):
        """
        Override of create method to generate enrollment numbers.
        
        Args:
            vals (dict): Values for creating the enrollment record
            
        Returns:
            record: Newly created enrollment record
        """
        if vals.get('name', 'New') == 'New':  # Check if name needs to be generated
            subject_id = vals.get('subject_id')  # Get subject ID
            date_val = vals.get('date')  # Get enrollment date
            year = datetime.strptime(date_val, "%Y-%m-%d").year if date_val else datetime.today().year  # Extract year

            subject = self.env['university.subject'].browse(subject_id)  # Fetch subject record
            prefix = subject.name[:3].upper() if subject else "UNK"  # Use subject prefix or 'UNK'

            count = self.search_count([
                ('subject_id', '=', subject_id),
                ('date', '>=', f"{year}-01-01"),
                ('date', '<=', f"{year}-12-31")
            ]) + 1  # Count existing enrollments for this subject/year

            seq = str(count).zfill(4)  # Pad sequence number with zeros
            vals['name'] = f"{prefix}/{year}/{seq}"  # Build enrollment number

        return super(UniversityEnrollment, self).create(vals)  # Call original create method