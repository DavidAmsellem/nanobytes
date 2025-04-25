"""
Module for managing university students.

This module implements the UniversityStudent model which handles all student-related
operations in the university management system, including personal information,
academic records, and system access management.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
from markupsafe import escape, Markup

class UniversityStudent(models.Model):
    """
    University Student Model.
    
    This class represents students within the university system. It manages
    personal information, academic records, contact details, and system access.
    
    Attributes:
        name (Char): Student's full name
        image_1920 (Image): Student's profile picture
        university_id (Many2one): Associated university
        street (Char): Street address
        city (Char): City of residence
        zip (Char): Postal code
        state_id (Many2one): State/Province
        country_id (Many2one): Country
        tutor_id (Many2one): Academic tutor
        enrollment_ids (One2many): Course enrollments
        grade_ids (One2many): Academic grades
        email_student (Char): Student's email address
        partner_id (Many2one): Related partner record
        user_id (Many2one): Related user account
        active (Boolean): Record active status
        enrollment_count (Integer): Total enrollments (computed)
        grade_count (Integer): Total grades (computed)
    """
    _name = 'university.student'
    _description = 'University Student'

    # Basic Information Fields
    name = fields.Char(
        string='Name',
        required=True,
        help="Student's full name"
    )
    
    image_1920 = fields.Image(
        "Profile Picture",
        max_width=1920,
        max_height=1080,
        help="Student's profile picture"
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True,
        help="University where the student is enrolled"
    )

    # Address Information
    street = fields.Char(
        string='Street',
        help="Street address"
    )
    
    city = fields.Char(
        string='City',
        help="City of residence"
    )
    
    zip = fields.Char(
        string='ZIP',
        help="Postal code"
    )
    
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        help="State or province"
    )
    
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        help="Country of residence"
    )

    # Academic Relations
    tutor_id = fields.Many2one(
        'university.professor',
        string='Tutor',
        help="Academic advisor/tutor"
    )
    
    enrollment_ids = fields.One2many(
        'university.enrollment',
        'student_id',
        string='Enrollments',
        help="Course enrollments"
    )
    
    grade_ids = fields.One2many(
        'university.grade',
        'student_id',
        string='Grades',
        help="Academic grades"
    )

    # System Access and Contact
    email_student = fields.Char(
        string='Email',
        required=True,
        help="Student's institutional email address"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        help="Related partner record for communication"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User Account',
        ondelete='set null',
        help="Related user account for system access"
    )

    # Record Status
    active = fields.Boolean(
        default=True,
        help="Whether the student record is active"
    )

    # Computed Fields
    enrollment_count = fields.Integer(
        string='Enrollment Count',
        compute='_compute_enrollment_count',
        help="Total number of course enrollments"
    )
    
    grade_count = fields.Integer(
        string='Grade Count',
        compute='_compute_grade_count',
        help="Total number of grades received"
    )

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        """
        Calculate total number of enrollments.
        
        This method computes the total number of course enrollments
        for each student record.
        """
        for student in self:
            student.enrollment_count = len(student.enrollment_ids)

    @api.depends('grade_ids')
    def _compute_grade_count(self):
        """
        Calculate total number of grades.
        
        This method computes the total number of grades received
        for each student record.
        """
        for student in self:
            student.grade_count = len(student.grade_ids)

    def action_view_enrollments(self):
        """
        Display student enrollments view.
        
        Opens a window showing all course enrollments for the current student.
        
        Returns:
            dict: Window action for enrollment view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
            'target': 'current',
        }

    def action_view_grades(self):
        """
        Display student grades view.
        
        Opens a window showing all grades for the current student.
        
        Returns:
            dict: Window action for grades view
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Grades',
            'res_model': 'university.grade',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        """
        Create a new student record.
        
        This method extends the create operation to automatically create
        a portal user account for new students with appropriate access rights.
        
        Args:
            vals (dict): Values for creating the student record
            
        Returns:
            record: Newly created student record
            
        Raises:
            ValidationError: If a user with the given email already exists
        """
        student = super().create(vals)

        if not student.user_id and student.email_student:
            if self.env['res.users'].sudo().search([('login', '=', student.email_student)]):
                raise ValidationError(_("A user with email %s already exists") % student.email_student)

            groups_id = [
                (4, self.env.ref('base.group_portal').id),
                (4, self.env.ref('Universidad.group_university_student').id)
            ]

            user = self.env['res.users'].sudo().create({
                'name': student.name,
                'login': student.email_student,
                'email': student.email_student,
                'password': '1234',
                'groups_id': groups_id,
            })

            student.write({
                'user_id': user.id,
                'partner_id': user.partner_id.id
            })

        return student

    def _get_customer_information(self):
        """
        Get student information for email templates.
        
        Returns:
            dict: Dictionary containing student's contact information
        """
        self.ensure_one()
        return {
            'name': self.name,
            'email': self.email_student or self.partner_id.email,
            'street': self.street,
            'city': self.city,
            'zip': self.zip,
            'state_id': self.state_id.name if self.state_id else '',
            'country_id': self.country_id.name if self.country_id else '',
        }

    def action_print_grades_report(self):
        """
        Generate student grades PDF report.
        
        Returns:
            dict: Action to generate PDF report
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'Universidad.report_student',
            'report_type': 'qweb-pdf',
            'docs': self,
            'download': False,
            'display_name': f'Grade Report - {self.name}',
        }

    def action_send_welcome_email(self):
        """
        Send welcome email to student.
        
        This method sends a welcome email to the student using a predefined template.
        
        Raises:
            UserError: If student has no email or template is not found
            
        Returns:
            dict: Notification of success
        """
        self.ensure_one()
        
        if not self.email_student:
            raise UserError(_('Student must have an email configured.'))

        template = self.env.ref('Universidad.email_template_student_welcome')
        if not template:
            raise UserError(_('Welcome email template not found.'))

        template.send_mail(self.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success!'),
                'message': _('Welcome email sent successfully to %s', self.name),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_send_report(self, direct_send=False):
        """
        Send student report via email.
        
        This method either sends the report directly or opens the email composer wizard.
        
        Args:
            direct_send (bool): If True, sends directly. If False, opens composer.
            
        Returns:
            dict: Email composer action or send notification
            
        Raises:
            UserError: If student has no email or template is not found
        """
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_student_report')
        
        if not self.email_student:
            raise UserError(_('Student must have an email configured.'))
        
        if not template:
            raise UserError(_('Email template not found.'))
        
        template.write({
            'email_to': self.email_student,
            'partner_to': self.partner_id.id,
            'subject': f'Grade Report - {self.name} - {self.university_id.name}',
        })

        if direct_send:
            template.send_mail(self.id, force_send=True)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Report Sent',
                    'message': f'''
                        Sent by: {self.env.user.name}
                        To: {self.name}
                        Email: {self.email_student}
                    ''',
                    'type': 'success',
                    'sticky': False
                }
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_model': 'university.student',
                    'default_res_ids': [self.id],
                    'default_use_template': True,
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                    'default_email_to': self.email_student,
                    'default_subject': f'Grade Report - {self.name} - {self.university_id.name}',
                    'force_email': True,
                },
            }
    
    def action_send_student_report(self):
        """
        Envía el informe del estudiante por correo electrónico.
        Returns:
            dict: Notificación del resultado del envío
        """
        self.ensure_one()  # Asegura que solo se procesa un registro
        
        # Obtiene la plantilla de correo
        template = self.env.ref('Universidad.email_template_student_report')
        
        # Obtiene información de remitente y destinatario
        sender = self.env.user.name
        recipient_email = self.email_student or self.partner_id.email
        
        # Envía el correo
        template.send_mail(self.id, force_send=True)

        # Retorna notificación de éxito
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reporte Enviado',
                'message': f'''
                    Enviado por: {sender}
                    Para: {self.name}
                    Email: {recipient_email}
                ''',
                'type': 'success',
                'sticky': False
            }
        }
