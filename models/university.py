"""
Module for managing universities.

This module implements the University model which handles all university-related
operations in the university management system, including department management,
staff administration, and student enrollment tracking.
"""

from odoo import models, fields, api

class University(models.Model):
    """
    University Model.
    
    This class represents universities within the system. It manages the core
    entity that contains departments, professors, students, and enrollments.
    
    Attributes:
        name (Char): University name
        image_1920 (Image): University logo or image
        street (Char): Street address
        city (Char): City name
        zip (Char): Postal code
        state_id (Many2one): State/Province
        country_id (Many2one): Country
        director_id (Many2one): University director
        enrollment_ids (One2many): Student enrollments
        student_ids (One2many): Enrolled students
        professor_ids (One2many): Faculty members
        department_ids (One2many): Academic departments
        *_count (Integer): Computed counts for related records
    """
    _name = 'university.university'
    _description = 'University'

    # Basic Information
    name = fields.Char(
        string='Name', 
        required=True,
        help="Official name of the university"
    )
    
    image_1920 = fields.Image(
        "Image", 
        max_width=1920, 
        max_height=1080,
        help="University logo or representative image"
    )

    # Location Information
    street = fields.Char(
        string='Street',
        help="Street address of the university"
    )
    
    city = fields.Char(
        string='City',
        help="City where the university is located"
    )
    
    zip = fields.Char(
        string='ZIP',
        help="Postal code"
    )
    
    state_id = fields.Many2one(
        'res.country.state', 
        string='State',
        help="State or province where the university is located"
    )
    
    country_id = fields.Many2one(
        'res.country', 
        string='Country',
        help="Country where the university is located"
    )

    # Administration
    director_id = fields.Many2one(
        'university.professor', 
        string='Director',
        help="University director or president"
    )

    # Related Records
    enrollment_ids = fields.One2many(
        'university.enrollment', 
        'university_id', 
        string='Enrollments',
        help="Student course enrollments"
    )
    
    enrollment_count = fields.Integer(
        string='Enrollment Count', 
        compute='_compute_enrollment_count',
        help="Total number of course enrollments"
    )

    student_ids = fields.One2many(
        'university.student', 
        'university_id', 
        string='Students',
        help="Students enrolled in the university"
    )
    
    student_count = fields.Integer(
        string='Student Count', 
        compute='_compute_student_count',
        help="Total number of enrolled students"
    )

    professor_ids = fields.One2many(
        'university.professor', 
        'university_id', 
        string='Professors',
        help="Faculty members of the university"
    )
    
    professor_count = fields.Integer(
        string='Professor Count', 
        compute='_compute_professor_count',
        help="Total number of professors"
    )

    department_ids = fields.One2many(
        'university.department', 
        'university_id', 
        string='Departments',
        help="Academic departments"
    )
    
    department_count = fields.Integer(
        string='Department Count', 
        compute='_compute_department_count',
        help="Total number of departments"
    )

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        """
        Calculate total number of enrollments.
        
        This method computes the total number of course enrollments
        across all departments and programs.
        """
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    @api.depends('student_ids')
    def _compute_student_count(self):
        """
        Calculate total number of students.
        
        This method computes the total number of students currently
        enrolled in the university.
        """
        for record in self:
            record.student_count = len(record.student_ids)

    @api.depends('professor_ids')
    def _compute_professor_count(self):
        """
        Calculate total number of professors.
        
        This method computes the total number of faculty members
        currently employed by the university.
        """
        for record in self:
            record.professor_count = len(record.professor_ids)

    @api.depends('department_ids')
    def _compute_department_count(self):
        """
        Calculate total number of departments.
        
        This method computes the total number of academic departments
        within the university.
        """
        for record in self:
            record.department_count = len(record.department_ids)

    def action_view_professors(self):
        """
        Display university professors view.
        
        Opens a window showing all professors associated with this university.
        
        Returns:
            dict: Window action for professors view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Professors',
            'res_model': 'university.professor',
            'view_mode': 'list',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    def action_view_students(self):
        """
        Display university students view.
        
        Opens a window showing all students enrolled in this university.
        
        Returns:
            dict: Window action for students view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'university.student',
            'view_mode': 'list',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    def action_view_departments(self):
        """
        Display university departments view.
        
        Opens a kanban view showing all departments in this university.
        
        Returns:
            dict: Window action for departments kanban view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Departments',
            'res_model': 'university.department',
            'view_mode': 'kanban',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    def action_view_enrollments(self):
        """
        Display university enrollments view.
        
        Opens a window showing all course enrollments in this university.
        
        Returns:
            dict: Window action for enrollments view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }




