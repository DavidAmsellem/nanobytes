# models/department.py

# Importing necessary Odoo modules
from odoo import models, fields, api

# Definition of the model class, inheriting from models.Model
class UniversityDepartment(models.Model):
    """
    University Department Model.

    This class represents a department within a university.
    It manages the relationship between professors, department heads, and the university.
    """
    _name = 'university.department'  # Technical name of the model in Odoo
    _description = 'University Department'  # Human-readable description of the model

    name = fields.Char(
        string='Name',  # Label shown in the UI
        required=True,  # Field is mandatory
        help="Name of the department"  # Tooltip help text
    )

    university_id = fields.Many2one(
        'university.university',  # Related model: university
        string='University',  # Label shown in the UI
        required=True,  # Field is mandatory
        ondelete='restrict',  # Prevent deletion if linked
        help="University to which this department belongs" 
    )

    head_id = fields.Many2one(
        'university.professor',  # Related model: professor
        string='Department Head',  # Label shown in the UI
        ondelete='restrict', 
        help="Professor who leads this department" 
    )

    image_1920 = fields.Image(
        "Department Image",  # Label shown in the UI
        max_width=1920,  # Maximum image width
        max_height=1080,  # Maximum image height
        help="Department's logo or representative image" 
    )

    professor_ids = fields.One2many(
        'university.professor',  # Related model: professor
        'department_id',  # Inverse field on the professor model
        string='Professors',  # Label shown in the UI
        help="List of professors assigned to this department"  
    )

    professor_count = fields.Integer(
        string='Number of Professors',  # Label shown in the UI
        compute='_compute_professor_count',  # Compute method name
        help="Total number of professors in this department"  # Tooltip help text
    )

    @api.depends('professor_ids')  # This method depends on changes to professor_ids
    def _compute_professor_count(self):
        """
        Compute method to count the total number of professors in the department.
        Automatically triggered when the professor_ids field changes.
        """
        for record in self:
            record.professor_count = len(record.professor_ids)  # Assigns the count of professors to the computed field
