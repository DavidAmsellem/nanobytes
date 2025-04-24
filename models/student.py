# Importación de módulos necesarios de Odoo
from odoo import models, fields, api, _  # Core de Odoo
from odoo.exceptions import ValidationError  # Excepciones de validación
from odoo.exceptions import UserError  # Excepciones de usuario
import base64  # Para codificación/decodificación de datos binarios
from markupsafe import escape, Markup  # Para manejo seguro de HTML

class UniversityStudent(models.Model):
    """
    Modelo que representa a un estudiante universitario.
    Gestiona la información personal, académica y de contacto de los estudiantes.
    """
    # Configuración básica del modelo
    _name = 'university.student'  # Identificador técnico del modelo
    _description = 'University Student'  # Descripción para la interfaz de usuario

    # Campos de información básica del estudiante
    name = fields.Char(
        string='Name',
        required=True,  # Campo obligatorio
    )
    image_1920 = fields.Image(
        string='Photo',  # Foto del estudiante
    )
    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True,  # Universidad obligatoria
    )

    # Campos para la dirección del estudiante
    street = fields.Char(string='Street')  # Calle
    city = fields.Char(string='City')  # Ciudad
    zip = fields.Char(string='ZIP')  # Código postal
    state_id = fields.Many2one(
        'res.country.state',
        string='State'  # Estado/Provincia
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country'  # País
    )

    # Relaciones académicas
    tutor_id = fields.Many2one(
        'university.professor',
        string='Tutor'  # Profesor tutor
    )
    enrollment_ids = fields.One2many(
        'university.enrollment',
        'student_id',
        string='Enrollments'  # Matrículas del estudiante
    )
    grade_ids = fields.One2many(
        'university.grade',
        'student_id',
        string='Grades'  # Calificaciones del estudiante
    )

    # Campos de contacto y acceso al sistema
    email_student = fields.Char(
        string='Correo electrónico',
        required=True  # Email obligatorio
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto vinculado'  # Contacto en el sistema
    )
    user_id = fields.Many2one(
        'res.users',
        string='Usuario portal vinculado',
        ondelete='set null'  # Comportamiento al eliminar
    )

    # Control de registro activo
    active = fields.Boolean(
        default=True  # Por defecto el estudiante está activo
    )

    # Campos computados para estadísticas
    enrollment_count = fields.Integer(
        string='Enrollment Count',
        compute='_compute_enrollment_count'  # Método de cálculo
    )
    grade_count = fields.Integer(
        string='Grade Count',
        compute='_compute_grade_count'  # Método de cálculo
    )

    # Métodos de cálculo para campos computados
    def _compute_enrollment_count(self):
        """Calcula el número total de matrículas del estudiante"""
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_grade_count(self):
        """Calcula el número total de calificaciones del estudiante"""
        for record in self:
            record.grade_count = len(record.grade_ids)

    def action_view_enrollments(self):
        """
        Abre la vista de matrículas filtrada para el estudiante actual.
        Returns:
            dict: Acción de ventana para mostrar matrículas
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
        Abre la vista de calificaciones filtrada para el estudiante actual.
        Returns:
            dict: Acción de ventana para mostrar calificaciones
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
        """Sobrescribe el método create para crear usuario del portal"""
        student = super().create(vals)

        if not student.user_id and student.email_student:
            # Verifica si existe el usuario
            if self.env['res.users'].sudo().search([('login', '=', student.email_student)]):
                raise ValidationError(_("Ya existe un usuario con el email %s") % student.email_student)

            # Asigna grupos de acceso para estudiantes
            groups_id = [
                (4, self.env.ref('base.group_portal').id),
                (4, self.env.ref('Universidad.group_university_student').id)
            ]

            # Crea el usuario con los grupos asignados
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
        Obtiene la información del estudiante para las plantillas de correo.
        Returns:
            dict: Información del estudiante
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
        Genera el reporte PDF de calificaciones del estudiante.
        Returns:
            dict: Acción para generar el reporte
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'Universidad.report_student',
            'report_type': 'qweb-pdf',
            'docs': self,
            'download': False,
            'display_name': f'Reporte de Notas - {self.name}',
        }

# Extensión del modelo UniversityStudent
class UniversityStudent(models.Model):
    """Extensión del modelo estudiante para funcionalidad adicional"""
    _inherit = 'university.student'

    def action_send_welcome_email(self):
        """
        Envía el email de bienvenida al estudiante.
        Raises:
            UserError: Si no hay email configurado o no se encuentra la plantilla
        Returns:
            dict: Notificación del resultado
        """
        self.ensure_one()
        
        # Validaciones
        if not self.email_student:
            raise UserError(_('El estudiante debe tener un email configurado.'))

        template = self.env.ref('Universidad.email_template_student_welcome')
        if not template:
            raise UserError(_('No se encontró la plantilla de correo de bienvenida.'))

        # Envía el correo
        template.send_mail(self.id, force_send=True)
        
        # Notificación de éxito
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('¡Éxito!'),
                'message': _('Email de bienvenida enviado correctamente a %s', self.name),
                'type': 'success',
                'sticky': False,
            }
        }

    # Redefinición del campo email_student
    email_student = fields.Char(
        string='Email',
        required=False,
        help='Email del estudiante para comunicaciones'
    )

    def action_send_report(self, direct_send=False):
        """
        Envía o abre el asistente para enviar el reporte del estudiante.
        Args:
            direct_send (bool): Si es True, envía directamente. Si es False, abre el asistente.
        Returns:
            dict: Acción para abrir el compositor de correo o notificación de envío
        """
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_student_report')
        
        # Verificaciones comunes
        if not self.email_student:
            raise UserError(_('El estudiante debe tener un email configurado.'))
        
        if not template:
            raise UserError(_('No se encontró la plantilla de correo.'))
        
        # Actualiza la plantilla
        template.write({
            'email_to': self.email_student,
            'partner_to': self.partner_id.id,
            'subject': f'Informe de Calificaciones - {self.name} - {self.university_id.name}',
        })

        # Envío directo o asistente según el parámetro
        if direct_send:
            # Envía el correo directamente
            template.send_mail(self.id, force_send=True)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Reporte Enviado',
                    'message': f'''
                        Enviado por: {self.env.user.name}
                        Para: {self.name}
                        Email: {self.email_student}
                    ''',
                    'type': 'success',
                    'sticky': False
                }
            }
        else:
            # Abre el asistente de composición
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
                    'default_subject': f'Informe de Calificaciones - {self.name} - {self.university_id.name}',
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
