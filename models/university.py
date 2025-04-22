# Import required Odoo modules
from odoo import models, fields

# Define University class
class University(models.Model):
    # Technical name of the model in the database
    _name = 'university.university'
    # Model description for the user interface
    _description = 'University'

    # Required field for university name
    name = fields.Char(
        string='Name', 
        required=True
    )
    
    # Field to store university image with maximum dimensions
    image_1920 = fields.Image(
        "Image", 
        max_width=1920, 
        max_height=1080
    )

    # University address fields
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    state_id = fields.Many2one(
        'res.country.state', 
        string='State'
    )
    country_id = fields.Many2one(
        'res.country', 
        string='Country'
    )

    # Relationship with university director
    director_id = fields.Many2one(
        'university.professor', 
        string='Director'
    )

    # Relationships and counters for related records
    # Enrollments
    enrollment_ids = fields.One2many(
        'university.enrollment', 
        'university_id', 
        string='Enrollments'
    )
    enrollment_count = fields.Integer(
        string='Enrollment Count', 
        compute='_compute_enrollment_count'
    )

    # Students
    student_ids = fields.One2many(
        'university.student', 
        'university_id', 
        string='Students'
    )
    student_count = fields.Integer(
        string='Student Count', 
        compute='_compute_student_count'
    )

    # Professors
    professor_ids = fields.One2many(
        'university.professor', 
        'university_id', 
        string='Professors'
    )
    professor_count = fields.Integer(
        string='Professor Count', 
        compute='_compute_professor_count'
    )

    # Departments
    department_ids = fields.One2many(
        'university.department', 
        'university_id', 
        string='Departments'
    )
    department_count = fields.Integer(
        string='Department Count', 
        compute='_compute_department_count'
    )

    # Method to calculate number of enrollments
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    # Method to calculate number of students
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    # Method to calculate number of professors
    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

    # Method to calculate number of departments
    def _compute_department_count(self):
        for record in self:
            record.department_count = len(record.department_ids)

    # Action to view university professors list
    def action_view_professors(self):
        return {
            'type': 'ir.actions.act_window',      # Action type
            'name': 'Professors',                  # Window title
            'res_model': 'university.professor',   # Model to display
            'view_mode': 'list',                  # Available view modes
            'domain': [('university_id', '=', self.id)],  # Record filter
            'context': {'default_university_id': self.id},  # Default context
            'target': 'current',                  # Window target
        }

    # Action to view university students list
    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',      # Action type
            'name': 'Students',                   # Window title
            'res_model': 'university.student',    # Model to display
            'view_mode': 'list',                 # View modes to display
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',                 # Current window target
        }

    # Action to view university departments in kanban view
    def action_view_departments(self):
        return {
            'type': 'ir.actions.act_window',      # Action type
            'name': 'Departments',                # Window title
            'res_model': 'university.department', # Model to display
            'view_mode': 'kanban',               # View mode to display
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    # Action to view university enrollments list
    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }




