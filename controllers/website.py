from odoo import http
from odoo.http import request

class UniversityWebsiteController(http.Controller):

    @http.route('/universidad', auth='public', website=True)
    def list_universities(self, **kw):
        universities = request.env['university.university'].sudo().search([])
        return request.render('Universidad.website_universities', {
            'universities': universities,
        })

    @http.route('/profesores/<int:university_id>', auth='public', website=True)
    def list_professors(self, university_id, **kw):
        professors = request.env['university.professor'].sudo().search([('university_id', '=', university_id)])
        university = request.env['university.university'].sudo().browse(university_id)
        return request.render('Universidad.website_professors', {
            'professors': professors,
            'university': university,
        })

    @http.route('/my/grades', type='http', auth='user', website=True)
    def portal_my_grades(self, **kw):
        user = request.env.user
        student = request.env['university.student'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not student:
            return request.redirect('/my')

        grades = request.env['university.grade'].sudo().search([
            ('student_id', '=', student.id)
        ])

        return request.render('Universidad.portal_grades', {
            'grades': grades,
        })

