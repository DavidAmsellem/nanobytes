# models/department.py
# Importación de los módulos necesarios de Odoo
from odoo import models, fields, api

# Definición de la clase del modelo heredando de models.Model
class UniversityDepartment(models.Model):
    """
    University Department Model.
    
    This class represents a department within a university. It manages the relationship
    between professors, department heads, and the university itself.
    
    Attributes:
        name (Char): Department name
        university_id (Many2one): Related university
        head_id (Many2one): Department head professor
        image_1920 (Image): Department image
        professor_ids (One2many): List of professors in the department
        professor_count (Integer): Total number of professors (computed)
    """
    _name = 'university.department'
    _description = 'University Department'

    name = fields.Char(
        string='Name',
        required=True,
        help="Name of the department"
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True,
        ondelete='restrict',
        help="University to which this department belongs"
    )

    head_id = fields.Many2one(
        'university.professor',
        string='Department Head',
        ondelete='restrict',
        help="Professor who leads this department"
    )

    image_1920 = fields.Image(
        "Department Image",
        max_width=1920,
        max_height=1080,
        help="Department's logo or representative image"
    )

    professor_ids = fields.One2many(
        'university.professor',
        'department_id',
        string='Professors',
        help="List of professors assigned to this department"
    )

    professor_count = fields.Integer(
        string='Number of Professors',
        compute='_compute_professor_count',
        help="Total number of professors in this department"
    )

    @api.depends('professor_ids')
    def _compute_professor_count(self):
        """
        Compute method to count the total number of professors in the department.
        This method is triggered when the professor_ids field changes.
        """
        for record in self:
            record.professor_count = len(record.professor_ids)

