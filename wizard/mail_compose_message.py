from odoo import models

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        result = super().onchange_template_id(template_id=template_id, composition_mode=composition_mode, model=model, res_id=res_id)
        if model == 'university.student':
            student = self.env['university.student'].browse(res_id)
            result['value'].update({
                'attachment_ids': [(0, 0, {
                    'name': f'Informe_{student.name}.pdf',
                    'datas': self.env.ref('Universidad.action_report_student')._render_qweb_pdf([res_id])[0],
                    'mimetype': 'application/pdf'
                })]
            })
        return result