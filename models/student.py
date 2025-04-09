# Importación de módulos necesarios para trabajar con Odoo y excepciones
from odoo import models, fields, api, _  # Importa el módulo para crear modelos y campos en Odoo
from odoo.exceptions import ValidationError  # Importa la excepción para errores de validación
from odoo.exceptions import UserError  # Importa la excepción para errores de usuario
import base64  # Importa base64 (aunque no se está usando en este fragmento de código)
from markupsafe import escape, Markup  # Importamos el escape para HTML seguro

# Definición de la clase 'UniversityStudent', que es un modelo de Odoo
class UniversityStudent(models.Model):
    _name = 'university.student'
    _description = 'University Student'

    # Campos básicos
    name = fields.Char(string='Name', required=True)
    image_1920 = fields.Image(string='Photo')
    university_id = fields.Many2one('university.university', string='University', required=True)

    # Dirección del estudiante
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    # Tutor del estudiante
    tutor_id = fields.Many2one('university.professor', string='Tutor')

    # Relaciones One2many
    enrollment_ids = fields.One2many('university.enrollment', 'student_id', string='Enrollments')
    grade_ids = fields.One2many('university.grade', 'student_id', string='Grades')

    # Correo electrónico y relaciones con usuarios/contactos
    email_student = fields.Char(string='Correo electrónico')
    partner_id = fields.Many2one('res.partner', string='Contacto vinculado')
    user_id = fields.Many2one('res.users', string='Usuario portal vinculado', ondelete='set null')

    # Estado activo
    active = fields.Boolean(default=True)

    # Contadores computados
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')
    grade_count = fields.Integer(string='Grade Count', compute='_compute_grade_count')

    # Métodos computados
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)

    # Acción para ver matrículas
    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
            'target': 'current',
        }

    # Acción para ver calificaciones
    def action_view_grades(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Grades',
            'res_model': 'university.grade',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
            'target': 'current',
        }

    # Acción para enviar el informe del estudiante
    def action_send_student_report(self):
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_student_report')
        
        # Obtener información del remitente y destinatario
        sender = self.env.user.name
        recipient_email = self.email_student or self.partner_id.email
        
        # Envía el correo
        template.send_mail(self.id, force_send=True)

        # Retorna la acción para mostrar el toast con info del envío
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

    # Método para crear estudiante y usuario portal
    def create(self, vals):
        student = super().create(vals)

        if not student.user_id:
            login = student.name.lower().replace(" ", "") + "@universidad.local"
            if self.env['res.users'].sudo().search([('login', '=', login)]):
                raise ValidationError(_("Ya existe un usuario con login %s") % login)

            # Establecemos contraseña inicial como 1234
            user = self.env['res.users'].sudo().create({
                'name': student.name,
                'login': login,
                'email': login,
                'password': '1234',  # Contraseña inicial fija
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            })

            student.user_id = user.id
            student.partner_id = user.partner_id

            # # Opcional: Enviar correo con credenciales
            # template = self.env.ref('Universidad.email_template_new_student_credentials', raise_if_not_found=False)
            # if template:
            #     template.with_context(
            #         password='1234',
            #         login=login
            #     ).send_mail(student.id, force_send=True)

        return student

    # Método necesario para que mail.template funcione sin error
    def _get_customer_information(self):
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
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'Universidad.report_student',
            'report_type': 'qweb-pdf',
            'docs': self,
            'download': False,  # Evita la descarga automática
            'display_name': f'Reporte de Notas - {self.name}',  # Nombre personalizado en el visor
        }
