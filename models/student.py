# Importación de módulos necesarios para trabajar con Odoo y excepciones
from odoo import models, fields, api, _  # Importa el módulo para crear modelos y campos en Odoo
from odoo.exceptions import ValidationError  # Importa la excepción para errores de validación
from odoo.exceptions import UserError  # Importa la excepción para errores de usuario
import base64  # Importa base64 (aunque no se está usando en este fragmento de código)
from markupsafe import escape, Markup #importamos el escape

# Definición de la clase 'UniversityStudent', que es un modelo de Odoo
class UniversityStudent(models.Model):
    # Definición del nombre técnico del modelo y su descripción
    _name = 'university.student'  # Nombre técnico del modelo en Odoo
    _description = 'University Student'  # Descripción del modelo para fines de visualización en Odoo

    # Campos definidos en el modelo
    name = fields.Char(string='Name', required=True)  # Campo de texto obligatorio para el nombre del estudiante
    image_1920 = fields.Image(string='Photo')  # Campo de imagen para la foto del estudiante
    university_id = fields.Many2one('university.university', string='University', required=True)  # Relación con la universidad (Many2one)



            
    # Dirección del estudiante
    street = fields.Char(string='Street')  # Dirección
    city = fields.Char(string='City')  # Ciudad
    zip = fields.Char(string='ZIP')  # Código postal
    state_id = fields.Many2one('res.country.state', string='State')  # Relación con el estado
    country_id = fields.Many2one('res.country', string='Country')  # Relación con el país

    # Tutor del estudiante
    tutor_id = fields.Many2one('university.professor', string='Tutor')  # Relación con el tutor (Many2one)
    
    # Relaciones One2many con las matrículas y calificaciones del estudiante
    enrollment_ids = fields.One2many('university.enrollment', 'student_id', string='Enrollments')  # Matrículas del estudiante
    grade_ids = fields.One2many('university.grade', 'student_id', string='Grades')  # Calificaciones del estudiante
    
    # Correo electrónico del estudiante
    email_student = fields.Char(string='Correo electrónico')  # Correo electrónico del estudiante

    # Relación con el contacto vinculado en 'res.partner' (modelo estándar de Odoo para personas y empresas)
    partner_id = fields.Many2one('res.partner', string='Contacto vinculado')  # Relación Many2one con partner (contacto vinculado)
    
    # Relación con el usuario en el portal de Odoo
    user_id = fields.Many2one('res.users', string='Usuario portal vinculado', ondelete='set null')  # Relación con el usuario (Many2one)

    # Campo booleano para activar o desactivar al estudiante
    active = fields.Boolean(default=True)  # Campo booleano que indica si el estudiante está activo

    # Campos computados para contar el número de matrículas y calificaciones
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')  # Contador de matrículas
    grade_count = fields.Integer(string='Grade Count', compute='_compute_grade_count')  # Contador de calificaciones

    # Métodos para calcular los contadores de matrículas y calificaciones
    def _compute_enrollment_count(self):
        for record in self:  # Itera sobre cada registro de estudiante
            record.enrollment_count = len(record.enrollment_ids)  # Calcula la cantidad de matrículas asociadas

    def _compute_grade_count(self):
        for record in self:  # Itera sobre cada registro de estudiante
            record.grade_count = len(record.grade_ids)  # Calcula la cantidad de calificaciones asociadas

    # Acción para ver las matrículas del estudiante
    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',  # Tipo de acción para abrir una ventana
            'name': 'Enrollments',  # Nombre de la ventana
            'res_model': 'university.enrollment',  # Modelo de las matrículas
            'view_mode': 'list,form',  # Tipos de vista disponibles: lista y formulario
            'domain': [('student_id', '=', self.id)],  # Filtra las matrículas por el estudiante actual
            'context': {'default_student_id': self.id},  # Define un contexto con el id del estudiante
            'target': 'current',  # La acción se abrirá en la ventana actual
        }

    # Acción para ver las calificaciones del estudiante
    def action_view_grades(self):
        return {
            'type': 'ir.actions.act_window',  # Tipo de acción para abrir una ventana
            'name': 'Grades',  # Nombre de la ventana
            'res_model': 'university.grade',  # Modelo de las calificaciones
            'view_mode': 'list,form',  # Tipos de vista disponibles: lista y formulario
            'domain': [('student_id', '=', self.id)],  # Filtra las calificaciones por el estudiante actual
            'context': {'default_student_id': self.id},  # Define un contexto con el id del estudiante
            'target': 'current',  # La acción se abrirá en la ventana actual
        }

    # Acción para enviar el informe del estudiante
    def action_send_student_report(self):
        self.ensure_one()

        # Buscar la plantilla de correo
        template = self.env.ref('Universidad.email_template_student_report', raise_if_not_found=False)
        if not template:
            raise UserError("La plantilla de correo no se ha encontrado.")

        # Preparar el contexto
        ctx = {
            'default_model': 'university.student',            # Modelo al que se refiere
            'default_use_template': bool(template),           # Usar plantilla (True)
            'default_template_id': template.id,               # ID de la plantilla de correo
            'default_composition_mode': 'comment',            # Modo de redacción
            'force_email': True,                              # Forzar envío como correo
        }

    # Devolver la acción que abre el wizard
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    # Método para crear un nuevo estudiante
   
    def create(self, vals):
        student = super().create(vals)  # Llama al método 'create' del modelo base para crear el registro

        # Si el estudiante no tiene un usuario asignado, se crea uno automáticamente
        if not student.user_id:
            login = student.name.lower().replace(" ", "") + "@universidad.local"  # Genera un login basado en el nombre del estudiante
            if self.env['res.users'].sudo().search([('login', '=', login)]):  # Verifica si ya existe un usuario con ese login
                raise ValidationError(_("Ya existe un usuario con login %s") % login)  # Si existe, lanza un error de validación

            # Crea un usuario en el portal de Odoo
            user = self.env['res.users'].sudo().create({
                'name': student.name,  # Nombre del usuario
                'login': login,  # Login del usuario
                'email': login,  # Email del usuario (usamos el mismo que el login)
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],  # Asigna el usuario al grupo del portal
            })

            # Asigna el usuario creado al estudiante y su contacto asociado
            student.user_id = user.id
            student.partner_id = user.partner_id

        return student  # Retorna el estudiante recién creado

