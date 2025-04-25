"""
Module for managing university subjects.

This module implements the UniversitySubject model which handles all subject-related
operations in the university management system, including department assignments,
professor associations, and enrollment tracking.
"""

from odoo import models, fields, api

class UniversitySubject(models.Model):
    """
    University Subject Model.
    
    This class represents academic subjects within the university system. It manages
    the relationship between departments, professors, and student enrollments.
    
    Attributes:
        name (Char): Subject name
        university_id (Many2one): Associated university
        department_id (Many2one): Department offering the subject
        professor_ids (Many2many): Professors teaching the subject
        enrollment_ids (One2many): Student enrollments in this subject
        enrollment_count (Integer): Total number of enrollments (computed)
        image_1920 (Image): Subject's representative image
    """
    _name = 'university.subject'
    _description = 'University Subject'

    # Basic Information
    name = fields.Char(
        string='Name',
        required=True,
        help="Name of the subject"
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True,
        help="University offering this subject"
    )

    department_id = fields.Many2one(
        'university.department',
        string='Department',
        required=True,
        domain="[('university_id', '=', university_id)]",
        help="Department responsible for this subject"
    )

    # Teaching Staff
    professor_ids = fields.Many2many(
        'university.professor',
        string='Professors',
        domain="[('department_id', '=', department_id)]",
        help="Professors teaching this subject"
    )

    # Enrollment Information
    enrollment_ids = fields.One2many(
        'university.enrollment',
        'subject_id',
        string='Enrollments',
        help="Student enrollments in this subject"
    )

    enrollment_count = fields.Integer(
        string='Enrollment Count',
        compute='_compute_enrollment_count',
        help="Total number of student enrollments"
    )

    # Media
    image_1920 = fields.Image(
        string="Image",
        help="Subject's representative image"
    )

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        """
        Calculate total number of enrollments.
        
        This method computes the total number of student enrollments
        for each subject record.
        """
        for subject in self:
            subject.enrollment_count = len(subject.enrollment_ids)

    def action_view_enrollments(self):
        """
        Display subject enrollments view.
        
        Opens a window showing all student enrollments for the current subject.
        
        Returns:
            dict: Window action for enrollment view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('subject_id', '=', self.id)],
            'context': {'default_subject_id': self.id},
            'target': 'current',
        }
