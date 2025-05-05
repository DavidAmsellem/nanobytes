"""
Module for managing university professors.

This module implements the UniversityProfessor model which handles all professor-related
operations in the university management system, including user creation, department
assignments, and email communications.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# Definition of the UniversityProfessor model
class UniversityProfessor(models.Model):
    """
    University Professor Model.

    This class represents academic professors within the university system. 
    It manages professor information, department assignments, subject assignments, and user access.
    """
    _name = 'university.professor'  # Technical name of the model
    _description = 'University Professor'  # Human-readable description

    # Basic Information Fields
    name = fields.Char(
        string='Name',  
        required=True,  # Field is mandatory
        help="Professor's full name"  # Tooltip help text
    )
    
    image_1920 = fields.Image(
        "Profile Picture", 
        max_width=1920,  # Maximum image width
        max_height=1080,  # Maximum image height
        help="Professor's profile picture"  
    )

    university_id = fields.Many2one(
        'university.university',  # Enlazado con el modelo universidad
        string='University',  #Una universidad puede tener varios profesores
        required=True,  
        help="University where the professor teaches"  
    )
    
    department_id = fields.Many2one(
        'university.department',  # Renlazado con depart
        string='Department',  #El departamento pueden tener varios profesores
        help="Academic department the professor belongs to"  
    )
    
    subject_ids = fields.Many2many(
        'university.subject',  # Enlazado con asignaturas
        string='Subjects',  #Varios profesores pueden dar varias asignaturas
        help="Subjects taught by the professor"  # Tooltip help text
    )

    enrollment_ids = fields.One2many(
        'university.enrollment',  # Enlazado con matriculas
        'professor_id',  # El profesor puede tener varias matriculas
        string='Enrollments', 
        help="Student enrollments under this professor"  
    )
    
    enrollment_count = fields.Integer(
        string='Enrollment Count',  # Label shown in the UI
        compute='_compute_enrollment_count',  # Computed field
        help="Total number of student enrollments"  # Tooltip help text
    )

    professor_email = fields.Char(
        string='Email',  # Label shown in the UI
        required=True,  # Field is mandatory
        help="Professor's institutional email address"  # Tooltip help text
    )

    user_id = fields.Many2one(
        'res.users',  # enlazado con los user 
        string='User Account',  # los profesores tienen un usuario
        ondelete='set null',  
        help="Related user account for system access"  
    )

    partner_id = fields.Many2one(
        'res.partner',  # enlazado con los contactos
        string='Contact', # los profesores tienen un contacto
        help="Related partner record for communication" 
    )

    is_department_head = fields.Boolean(
        string='Department Head',  # Pabemos si tenemos jefe de departamento
        compute='_compute_is_department_head',  # campo
        store=True,  
        help="Indicates if the professor is head of any department"  
    )

    @api.depends('enrollment_ids')  # Trigger when enrollment_ids change
    def _compute_enrollment_count(self):
        """
        Compute the total number of student enrollments.

        This method calculates the number of enrollments linked to 
        the professor and updates enrollment_count.
        """
        for professor in self:
            professor.enrollment_count = len(professor.enrollment_ids)  # Count linked enrollments

    @api.depends('department_id', 'department_id.head_id')  # Trigger when department or head changes
    def _compute_is_department_head(self):
        """
        Determine if professor is a department head.

        Checks if this professor is assigned as head of any department
        and updates is_department_head accordingly.
        """
        for professor in self:
            professor.is_department_head = bool(
                self.env['university.department'].search_count([
                    ('head_id', '=', professor.id)  # Search for departments where this professor is head
                ])
            )

    def action_view_enrollments(self):
        """
        Display enrollments associated with the professor.

        Opens a view showing all student enrollments linked to this professor.

        Returns:
            dict: Action dictionary for the enrollment view
        """
        return {
            'type': 'ir.actions.act_window',  # Action type
            'name': 'Enrollments',  # Window title
            'res_model': 'university.enrollment',  # Model to display
            'view_mode': 'list,form',  # View modes
            'domain': [('professor_id', '=', self.id)],  # Filter by current professor
            'context': {'default_professor_id': self.id},  # Default context
        }

    @api.model  # Marks this as a model-level method
    def create(self, vals):
        """
        Create a new professor record.

        Extends the create method to automatically generate a user account 
        for new professors with default access rights.

        Args:
            vals (dict): Values for creating the professor record

        Returns:
            record: Newly created professor record

        Raises:
            ValidationError: If a user with the same email already exists
        """
        professor = super().create(vals)  # Call the parent create method

        # If no user assigned and email provided, create new user
        if not professor.user_id and professor.professor_email:
            if self.env['res.users'].sudo().search([('login', '=', professor.professor_email)]):
                raise ValidationError(_("A user with email %s already exists") % professor.professor_email)  # Prevent duplicate users

            groups_id = [
                (4, self.env.ref('base.group_user').id),  # Assign base user group
                (4, self.env.ref('Universidad.group_university_professor').id)  # Assign professor group
            ]

            user = self.env['res.users'].sudo().create({
                'name': professor.name,  # User's name
                'login': professor.professor_email,  # User login
                'email': professor.professor_email,  # User email
                'password': '1234',  # Default password (should be changed later)
                'groups_id': groups_id,  # Assigned groups
            })

            professor.write({
                'user_id': user.id,  # Link created user
                'partner_id': user.partner_id.id  # Link partner record
            })

        return professor

    def write(self, vals):
        """
        Update professor records.

        Extends the write method to handle email updates 
        and sync changes with the related user account.

        Args:
            vals (dict): Values to update

        Returns:
            bool: Result of the write operation

        Raises:
            ValidationError: If the new email is already used by another user
        """
        # If email is changing, update linked user account
        if 'professor_email' in vals and self.user_id:
            if self.env['res.users'].sudo().search_count([
                ('login', '=', vals['professor_email']),
                ('id', '!=', self.user_id.id)
            ]):
                raise ValidationError(_("A user with email %s already exists") % vals['professor_email'])  # Prevent duplicates
            
            self.user_id.sudo().write({
                'login': vals['professor_email'],  # Update login
                'email': vals['professor_email']  # Update email
            })

        return super().write(vals)  # Call the parent write method

    def action_send_welcome_email(self):
        """
        Send welcome email to professor.

        Prepares and sends a welcome email using 
        a predefined email template.

        Returns:
            dict: Action dictionary to open the email wizard
        """
        self.ensure_one()  # Ensure only one record is processed
        template = self.env.ref('Universidad.email_template_professor_welcome')  # Get email template
        template.write({
            'email_to': self.professor_email,  # Set recipient email
            'partner_to': self.partner_id.id,  # Set recipient partner
            'subject': f'Welcome to {self.university_id.name}',  # Customize subject line
        })
        return {
            'type': 'ir.actions.act_window',  # Action type
            'name': 'Send Welcome Email',  # Window title
            'res_model': 'professor.welcome.wizard',  # Model for wizard
            'view_mode': 'form',  # Open form view
            'target': 'new',  # Open in a new popup window
            'context': {'active_id': self.id},  # Pass current professor ID
        }