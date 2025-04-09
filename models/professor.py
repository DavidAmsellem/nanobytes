from odoo import models, fields, api

class UniversityProfessor(models.Model):
    _name = 'university.professor'
    _description = 'University Professor'

    name = fields.Char(string='Name', required=True)
    image_1920 = fields.Image("Image", max_width=1920, max_height=1080)

    university_id = fields.Many2one('university.university', string='University', required=True)
    department_id = fields.Many2one('university.department', string='Department')
    subject_ids = fields.Many2many('university.subject', string='Subjects')

    enrollment_ids = fields.One2many('university.enrollment', 'professor_id', string='Enrollments')
    enrollment_count = fields.Integer(string='Enrollment Count', compute='_compute_enrollment_count')

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for prof in self:
            prof.enrollment_count = len(prof.enrollment_ids)

    def action_view_enrollments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enrollments',
            'res_model': 'university.enrollment',
            'view_mode': 'list,form',
            'domain': [('professor_id', '=', self.id)],
            'context': {'default_professor_id': self.id},
        }



