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
    
    state_id = fields.Many2one( #relacion con modelo de provincia
        'res.country.state',  #cada estiante tiene una provincia
        string='State',
        help="State or province"
    )
    
    country_id = fields.Many2one( #relacion con modelo de pais
        'res.country',   #cada estudiante tiene un pais asignado
        string='Country',
        help="Country of residence"
    )

    # Academic Relations
    tutor_id = fields.Many2one(  #relacion con el modelo de profesores
        'university.professor', #cada estudiante tiene un tutor
        string='Tutor',
        help="Academic advisor/tutor"
    )
    
    enrollment_ids = fields.One2many(  #relacion con modelo matriculas
        'university.enrollment', #un estudiante tiene varias matriculas
        'student_id',
        string='Enrollments',
        help="Course enrollments"
    )
    
    grade_ids = fields.One2many( #relacion con modelo de notas
        'university.grade',     #cada estudiante tiene varias notas
        'student_id',
        string='Grades',
        help="Academic grades"
    )

    # System Access and Contact
    email_student = fields.Char( #imprescindible el correo (asi gestionamos notas web)
        string='Email',
        required=True,
        help="Student's institutional email address"
    )
    
    partner_id = fields.Many2one(   #relacion con el modelo de contactos
        'res.partner',  #cada estudiante tiene un contacto
        string='Contact',
        help="Related partner record for communication"
    )
    
    user_id = fields.Many2one( #relacion con el modelo de usuarios
        'res.users',   #cada estudiante tiene un usuario
        string='User Account',
        ondelete='set null', #si se elimina estudiante, es null
        help="Related user account for system access"
    )

    # Record Status
    active = fields.Boolean(  #bool que nos dice si el estudiante esta activo
        default=True,
        help="Whether the student record is active"
    )

    # Computed Fields
    enrollment_count = fields.Integer(  #contador de matriculas
        string='Enrollment Count',
        compute='_compute_enrollment_count', #campo
        help="Total number of course enrollments"
    )
    
    grade_count = fields.Integer( #contador de notas
        string='Grade Count',
        compute='_compute_grade_count', #campo
        help="Total number of grades received"
    )

    @api.depends('enrollment_ids') #trigger de matriculas
    def _compute_enrollment_count(self): #metodo de mcontar matriculas
        """
        Calculate total number of enrollments.
        
        This method computes the total number of course enrollments
        for each student record.
        """
        for student in self:
            student.enrollment_count = len(student.enrollment_ids)

    @api.depends('grade_ids') #trigger de notas
    def _compute_grade_count(self): #metodo de contar notas
        """
        Calculate total number of grades.
        
        This method computes the total number of grades received
        for each student record.
        """
        for student in self:
            student.grade_count = len(student.grade_ids)

    def action_view_enrollments(self): #boton para ver matriculas
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

    def action_view_grades(self): #boton para ver notas
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

    @api.model #modelo, no registros
    def create(self, vals):  #sobreescribimo el metodo de odoo (create) (vals son los valores)
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
        student = super().create(vals) #llamamos a super

        if not student.user_id and student.email_student: #si no hay usuario y hay correo (correo entrar web)
            if self.env['res.users'].sudo().search([('login', '=', student.email_student)]): #comprobamos el correo
                raise ValidationError(_("A user with email %s already exists") % student.email_student) #error

            groups_id = [ #grupos de usuario
                (4, self.env.ref('base.group_portal').id), #grupo estandar de usuario
                (4, self.env.ref('Universidad.group_university_student').id) #grupo de estudiante
            ]   # many2many ()

            user = self.env['res.users'].sudo().create({
                'name': student.name,
                'login': student.email_student,
                'email': student.email_student,
                'password': '1234',
                'groups_id': groups_id,
            })

            student.write({  #escribimos el usuario
                'user_id': user.id,  #asignamos el usuario
                'partner_id': user.partner_id.id #asignamos el partner
            })

        return student

    def _get_customer_information(self): #extraer info templates
        """
        Get student information for email templates.
        
        Returns:
            dict: Dictionary containing student's contact information
        """
        self.ensure_one() #solo contiene un registro
        return {
            'name': self.name, 
            'email': self.email_student or self.partner_id.email, #o email estudiante o el de partner
            'street': self.street,
            'city': self.city,
            'zip': self.zip,
            'state_id': self.state_id.name if self.state_id else '', #solo si existen
            'country_id': self.country_id.name if self.country_id else '',
        }

    def action_print_grades_report(self): #imprimimos el informe con accion
        """
        Generate student grades PDF report.
        
        Returns:
            dict: Action to generate PDF report
        """
        self.ensure_one() #solo un registro
        return {
            'type': 'ir.actions.report',  #accion de tipo informe
            'report_name': 'Universidad.report_student', #nombre del informe
            'report_type': 'qweb-pdf',  #tipo de informe
            'docs': self, #registro actual
            'download': False, #prefiero mostrar en pantalla
            'display_name': f'Grade Report - {self.name}', #Nombre final fichero
        }

    def action_send_report(self, direct_send=False): #mandamos el informe
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
        self.ensure_one() #solo un registro
        # Obtiene la plantilla de correo
        direct_send = self.env.context.get('default_direct_send', direct_send) #busca el contexto / sino falso
        template = self.env.ref('Universidad.email_template_student_report')
        #si no hay email de estudiante
        if not self.email_student:
            raise UserError(_('Student must have an email configured.'))
        #si no hay template
        if not template:
            raise UserError(_('Email template not found.'))
        #forzamos la actualizacion de datos
        template.write({
            'email_to': self.email_student,
            'partner_to': self.partner_id.id,
            'subject': f'Grade Report - {self.name} - {self.university_id.name}',
        })
        #si el envio es directo(A traves de boton en email)
        if direct_send:
            template.send_mail(self.id, force_send=True) #send_mail forzado
            
            return {
                'type': 'ir.actions.client',   #accion de notificacion 
                'tag': 'display_notification',  #display en pantalla
                'params': {                     #info del display
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
            #si el envio no es directo
            return {
                'type': 'ir.actions.act_window', #accion de ventana
                'view_mode': 'form',
                'res_model': 'mail.compose.message',  #abrimos el modelo de mensaje
                'views': [(False, 'form')], #se abrira el formulario
                'view_id': False,
                'target': 'new', #flotante
                'context': {  #composicion de correo
                    'default_model': 'university.student',
                    'default_res_ids': [self.id],
                    'default_use_template': True, #usamos la plantilla
                    'default_template_id': template.id, 
                    'default_composition_mode': 'comment',
                    'default_email_to': self.email_student,
                    'default_subject': f'Grade Report - {self.name} - {self.university_id.name}',
                    'force_email': True,
                },
            }

    #no implementado
    # def action_send_welcome_email(self): #enviar correo de bienvenida(opcional)
    #     """
    #     Send welcome email to student.
        
    #     This method sends a welcome email to the student using a predefined template.
        
    #     Raises:
    #         UserError: If student has no email or template is not found
            
    #     Returns:
    #         dict: Notification of success
    #     """
    #     self.ensure_one() #solo un registro
        
    #     if not self.email_student: #si no hay correo de estudiante
    #         raise UserError(_('Student must have an email configured.'))
    #                     #template de bienvenida
    #     template = self.env.ref('Universidad.email_template_student_welcome')
    #     if not template:
    #         raise UserError(_('Welcome email template not found.'))

    #     template.send_mail(self.id, force_send=True) #metodo send_mail, forzado no en cola
        
    #     return {  #notificacion en pantalla
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Success!'),
    #             'message': _('Welcome email sent successfully to %s', self.name),
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }
