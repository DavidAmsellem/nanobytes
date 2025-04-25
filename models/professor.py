"""
Module for managing university professors.

This module implements the UniversityProfessor model which handles all professor-related
operations in the university management system, including user creation, department
assignments, and email communications.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class UniversityProfessor(models.Model):
    """
    University Professor Model.
    
    This class represents academic professors within the university system. It manages
    professor information, department assignments, subject assignments, and user access.
    
    Attributes:
        name (Char): Professor's full name
        image_1920 (Image): Profile picture
        university_id (Many2one): Associated university
        department_id (Many2one): Department where professor teaches
        subject_ids (Many2many): Subjects taught by professor
        enrollment_ids (One2many): Student enrollments under this professor
        enrollment_count (Integer): Total number of enrollments (computed)
        professor_email (Char): Professional email address
        user_id (Many2one): Related user account for system access
        partner_id (Many2one): Related partner record
        is_department_head (Boolean): Indicates if professor heads a department
    """
    _name = 'university.professor'
    _description = 'University Professor'

    name = fields.Char(
        string='Name',
        required=True,
        help="Professor's full name"
    )
    
    image_1920 = fields.Image(
        "Profile Picture",
        max_width=1920,
        max_height=1080,
        help="Professor's profile picture"
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True,
        help="University where the professor teaches"
    )
    
    department_id = fields.Many2one(
        'university.department',
        string='Department',
        help="Academic department the professor belongs to"
    )
    
    subject_ids = fields.Many2many(
        'university.subject',
        string='Subjects',
        help="Subjects taught by the professor"
    )

    enrollment_ids = fields.One2many(
        'university.enrollment',
        'professor_id',
        string='Enrollments',
        help="Student enrollments under this professor"
    )
    
    enrollment_count = fields.Integer(
        string='Enrollment Count',
        compute='_compute_enrollment_count',
        help="Total number of student enrollments"
    )

    professor_email = fields.Char(
        string='Email',
        required=True,
        help="Professor's institutional email address"
    )

    user_id = fields.Many2one(
        'res.users',
        string='User Account',
        ondelete='set null',
        help="Related user account for system access"
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        help="Related partner record for communication"
    )

    is_department_head = fields.Boolean(
        string='Department Head',
        compute='_compute_is_department_head',
        store=True,
        help="Indicates if the professor is head of any department"
    )

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        """
        Compute the total number of student enrollments.
        
        This method calculates the total number of enrollments associated with
        the professor and updates the enrollment_count field accordingly.
        """
        for professor in self:
            professor.enrollment_count = len(professor.enrollment_ids)

    @api.depends('department_id', 'department_id.head_id')
    def _compute_is_department_head(self):
        """
        Determine if professor is a department head.
        
        This method checks if the professor is assigned as head of any department
        and updates the is_department_head field accordingly.
        """
        for professor in self:
            professor.is_department_head = bool(
                self.env['university.department'].search_count([
                    ('head_id', '=', professor.id)
                ])
            )

    def action_view_enrollments(self):
        """
        Display enrollments associated with the professor.
        
        Opens a view showing all student enrollments under this professor's courses.
        
        Returns:
            dict: Action dictionary for the enrollment view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('professor_id', '=', self.id)],
            'context': {'default_professor_id': self.id},
        }

    @api.model
    def create(self, vals):
        """
        Create a new professor record.
        
        This method extends the create operation to automatically create a user
        account for new professors with appropriate access rights.
        
        Args:
            vals (dict): Values for creating the professor record
            
        Returns:
            record: Newly created professor record
            
        Raises:
            ValidationError: If a user with the given email already exists
        """
        professor = super().create(vals)

        if not professor.user_id and professor.professor_email:
            if self.env['res.users'].sudo().search([('login', '=', professor.professor_email)]):
                raise ValidationError(_("A user with email %s already exists") % professor.professor_email)

            groups_id = [
                (4, self.env.ref('base.group_user').id),
                (4, self.env.ref('Universidad.group_university_professor').id)
            ]

            user = self.env['res.users'].sudo().create({
                'name': professor.name,
                'login': professor.professor_email,
                'email': professor.professor_email,
                'password': '1234',
                'groups_id': groups_id,
            })

            professor.write({
                'user_id': user.id,
                'partner_id': user.partner_id.id
            })

        return professor

    def write(self, vals):
        """
        Update professor records.
        
        This method extends the write operation to handle email updates and
        synchronize changes with the related user account.
        
        Args:
            vals (dict): Values to update
            
        Returns:
            bool: Result of the write operation
            
        Raises:
            ValidationError: If the new email conflicts with an existing user
        """
        if 'professor_email' in vals and self.user_id:
            if self.env['res.users'].sudo().search_count([
                ('login', '=', vals['professor_email']),
                ('id', '!=', self.user_id.id)
            ]):
                raise ValidationError(_("A user with email %s already exists") % vals['professor_email'])
            
            self.user_id.sudo().write({
                'login': vals['professor_email'],
                'email': vals['professor_email']
            })

        return super().write(vals)

    def action_send_welcome_email(self):
        """
        Send welcome email to professor.
        
        This method prepares and sends a welcome email to the professor using
        a predefined email template.
        
        Returns:
            dict: Action dictionary to open the email wizard
        """
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_professor_welcome')
        template.write({
            'email_to': self.professor_email,
            'partner_to': self.partner_id.id,
            'subject': f'Welcome to {self.university_id.name}',
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Welcome Email',
            'res_model': 'professor.welcome.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }



