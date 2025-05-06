"""
Module for managing university grades.

This module implements the UniversityGrade model which handles all grade-related
operations in the university management system.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# Definition of the UniversityGrade model
class UniversityGrade(models.Model):
    """
    University Grade Model.
    
    This class represents academic grades within the university system. 
    It manages the relationship between students, enrollments, and their performance.
    """
    _name = 'university.grade'  # Technical name of the model
    _description = 'University Grade'  # Human-readable description
    _order = 'date desc'  # Default sorting: most recent grades first
    _rec_name = 'display_name'  # Campo para mostrar como nombre

    student_id = fields.Many2one(  
        'university.student',  # Related model: student
        string='Student',  # Label shown in the UI
        required=True,  # Field is mandatory
        help="The student who received this grade"  # Tooltip help text
    )

    enrollment_id = fields.Many2one(
        'university.enrollment',  # Related model: enrollment
        string='Enrollment',  # Label shown in the UI
        required=True,  # Field is mandatory
        domain="[('student_id', '=', student_id)]",  # Filter enrollments by selected student
        help="The course enrollment associated with this grade"  # Tooltip help text
    )

    university_id = fields.Many2one(
        'university.university',  # Related model: university
        string='University',  # Label shown in the UI
        related='enrollment_id.university_id',  # Fetched from enrollment
        store=True,  # Store in database
        help="The university where this grade was issued"  # Tooltip help text
    )

    subject_id = fields.Many2one(
        'university.subject',  # Modelo relacionado
        string='Subject',      # Etiqueta en la UI
        related='enrollment_id.subject_id',  # Relacionado con la asignatura del enrollment
        store=True,           # Almacenar en base de datos
        readonly=True,        # Solo lectura ya que viene del enrollment
        help="Subject associated with this grade"  # Texto de ayuda
    )

    grade = fields.Float(
        string='Grade',  # Label shown in the UI
        required=True,  # Field is mandatory
        help="Numerical value of the grade (0-10)"  # Tooltip help text
    )

    date = fields.Date(
        string='Date',  # Label shown in the UI
        default=fields.Date.today,  # Default to today's date
        required=True,  # Field is mandatory
        help="Date when the grade was issued"  # Tooltip help text
    )

    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.onchange('student_id')  # Triggered when the student field changes
    def _onchange_student(self):
        """
        Handle student changes in the grade form.

        Clears the current enrollment selection and updates the domain
        for available enrollments based on the selected student.

        Returns:
            dict: Domain filter for enrollment field based on selected student.
        """
        self.enrollment_id = False  # Clear current enrollment
        return {
            'domain': {
                'enrollment_id': [('student_id', '=', self.student_id.id)]  # Only show enrollments for selected student
            }
        }

    @api.constrains('enrollment_id', 'student_id')  # Add constraint on enrollment and student fields
    def _check_student_enrollment(self):
        """
        Validate student-enrollment consistency.

        Ensures that the selected enrollment belongs to the selected student.

        Raises:
            ValidationError: If enrollment doesn't match the selected student.
        """
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError(_(
                    'You can only assign grades to enrollments of the selected student.'  # Error message shown to user
                ))

    @api.depends('subject_id', 'grade')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.subject_id.name} / {record.grade}"

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.subject_id.name} / {record.grade}"
            result.append((record.id, name))
        return result