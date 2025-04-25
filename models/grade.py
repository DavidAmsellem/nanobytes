"""
Module for managing university grades.

This module implements the UniversityGrade model which handles all grade-related
operations in the university management system.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class UniversityGrade(models.Model):
    """
    University Grade Model.
    
    This class represents academic grades within the university system. It manages
    the relationship between students, enrollments, and their academic performance.
    
    Attributes:
        name (Many2one): Grade identifier and student reference
        student_id (Many2one): Related student
        enrollment_id (Many2one): Related course enrollment
        university_id (Many2one): Related university (computed from enrollment)
        grade (Float): Numerical grade value
        date (Date): Date when the grade was issued
    """
    _name = 'university.grade'
    _description = 'University Grade'
    _order = 'date desc'

    student_id = fields.Many2one(
        'university.student',
        string='Student',
        required=True,
        help="The student who received this grade"
    )

    enrollment_id = fields.Many2one(
        'university.enrollment',
        string='Enrollment',
        required=True,
        domain="[('student_id', '=', student_id)]",
        help="The course enrollment associated with this grade"
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        related='enrollment_id.university_id',
        store=True,
        help="The university where this grade was issued"
    )

    grade = fields.Float(
        string='Grade',
        required=True,
        help="Numerical value of the grade (0-10)"
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        help="Date when the grade was issued"
    )

    @api.onchange('student_id')
    def _onchange_student(self):
        """
        Handle student changes in the grade form.

        This method is triggered when the student field is modified.
        It clears the current enrollment selection and updates the
        available enrollments based on the selected student.

        Returns:
            dict: Domain filter for enrollment field based on selected student
        """
        self.enrollment_id = False
        return {
            'domain': {
                'enrollment_id': [('student_id', '=', self.student_id.id)]
            }
        }

    @api.constrains('enrollment_id', 'student_id')
    def _check_student_enrollment(self):
        """
        Validate student-enrollment consistency.

        This constraint ensures that grades can only be assigned to enrollments
        that belong to the selected student. It prevents accidental grade
        assignments to wrong student-enrollment combinations.

        Raises:
            ValidationError: If trying to assign a grade to an enrollment
                           that doesn't belong to the selected student
        """
        for record in self:
            if record.enrollment_id.student_id != record.student_id:
                raise ValidationError(_(
                    'You can only assign grades to enrollments of the selected student.'
                ))

