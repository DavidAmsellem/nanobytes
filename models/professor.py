from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class UniversityProfessor(models.Model):
    """
    Model representing a University Professor.
    This class manages all professor-related information including personal details,
    assignments, and relationships with other university entities.
    """
    _name = 'university.professor'
    _description = 'University Professor'

    name = fields.Char(
        string='Name',
        required=True
    )
    
    image_1920 = fields.Image(
        "Image",
        max_width=1920,
        max_height=1080
    )

    university_id = fields.Many2one(
        'university.university',
        string='University',
        required=True
    )
    
    department_id = fields.Many2one(
        'university.department',
        string='Department'
    )
    
    subject_ids = fields.Many2many(
        'university.subject',
        string='Subjects'
    )

    enrollment_ids = fields.One2many(
        'university.enrollment',
        'professor_id',
        string='Enrollments'
    )
    
    enrollment_count = fields.Integer(
        string='Enrollment Count',
        compute='_compute_enrollment_count'
    )

    professor_email = fields.Char(
        string='Professor Email',
        required=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='Linked User',
        ondelete='set null'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Linked Contact'
    )

    is_department_head = fields.Boolean(
        string='Is Department Head',
        compute='_compute_is_department_head',
        store=True,
        help="Indicates if the professor is head of any department"
    )

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        """
        Compute method to count the number of enrollments for each professor.
        Updates the enrollment_count field based on the length of enrollment_ids.
        """
        for professor in self:
            professor.enrollment_count = len(professor.enrollment_ids)

    @api.depends('department_id', 'department_id.head_id')
    def _compute_is_department_head(self):
        """
        Computes whether the professor is a department head.
        A professor is considered a department head if they are set as the head_id
        of any department.
        """
        for professor in self:
            professor.is_department_head = bool(
                self.env['university.department'].search_count([
                    ('head_id', '=', professor.id)
                ])
            )

    def action_view_enrollments(self):
        """
        Opens a window showing all enrollments associated with the professor.
        
        Returns:
            dict: Action dictionary containing view parameters and domain filters
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
        Override of create method to handle user creation for new professors.
        
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

    def action_send_welcome_email(self):
        """Open the wizzard to send the salute emial"""
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_professor_welcome')
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Welcome Email',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'university.professor',
              
                'default_use_template': True,
                'default_template_id': template.id,
                'force_email': True
            }
        }



