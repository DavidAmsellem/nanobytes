from odoo import models, fields

class University(models.Model):
    _name = 'university.university'
    _description = 'University'

    name = fields.Char(string='Name', required=True)
    
    # Image
    image_1920 = fields.Image("Image", max_width=1920, max_height=1080)

    # Address fields
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')

    director_id = fields.Many2one('university.professor', string='Director')

    # Related records with counts and filtered views
    enrollment_ids = fields.One2many('university.enrollment', 'university_id', string='Enrollments')
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')

    student_ids = fields.One2many('university.student', 'university_id', string='Students')
    student_count = fields.Integer(string='Student Count', compute='_compute_student_count')

    professor_ids = fields.One2many('university.professor', 'university_id', string='Professors')
    professor_count = fields.Integer(string='Professor Count', compute='_compute_professor_count')

    department_ids = fields.One2many('university.department', 'university_id', string='Departments')
    department_count = fields.Integer(string='Department Count', compute='_compute_department_count')

    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

    def action_view_professors(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Professors',
            'res_model': 'university.professor',
            'view_mode': 'list,form',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }


    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'university.student',
            'view_mode': 'kanban,list,form',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
       }




    def action_view_departments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Departments',
            'res_model': 'university.department',
            'view_mode': 'list,form',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }

    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id},
            'target': 'current',
        }


    def _compute_department_count(self):
        for record in self:
            record.department_count = len(record.department_ids)




