from odoo import models, fields, api

class ProfessorWelcomeWizard(models.TransientModel):
    _name = 'professor.welcome.wizard'
    _description = 'Professor Welcome Email Wizard'

    professor_ids = fields.Many2many(
        'university.professor', 
        string='Professors',
        domain="[('id', '!=', context.get('active_id')), ('department_id', '=', department_id)]",
        required=True
    )
    department_id = fields.Many2one(
        'university.department',
        string='Department',
        related='current_professor_id.department_id',
        readonly=True
    )
    current_professor_id = fields.Many2one(
        'university.professor',
        default=lambda self: self.env.context.get('active_id'),
        readonly=True
    )

    def action_send_welcome(self):
        self.ensure_one()
        template = self.env.ref('Universidad.email_template_professor_welcome')
        
        for professor in self.professor_ids:
            template.send_mail(professor.id, force_send=True)
        
        return {'type': 'ir.actions.act_window_close'}