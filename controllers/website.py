"""
This module contains the main controller for university website functionalities.
Handles all public and portal routes related to universities, professors, students and grades.
"""

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.osv import expression
from typing import Dict, Any

class UniversityWebsite(http.Controller):
    """Controller for university website pages"""

    @http.route('/my/grades', type='http', auth='user', website=True)
    def show_portal_grades(self, **kw: Any) -> str:
        """Display grades in user portal"""
        user = request.env.user
        is_admin = user.has_group('base.group_system')
        
        # Redirect if not admin or student
        if not is_admin:
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            if not student:
                return request.redirect('/my')
        
        try:
            university_id = int(kw.get('university_id', 0))
        except (ValueError, TypeError):
            university_id = 0
            
        grade_filter = kw.get('grade_filter', 'all')
        domain = self._build_grades_domain(university_id, grade_filter)
        
        grades, universities = self._get_filtered_grades(user, is_admin, domain)
        
        return request.render('Universidad.portal_grades', {
            'grades': grades,
            'is_admin': is_admin,
            'universities': universities,
            'current_university': university_id,
            'current_filter': grade_filter
        })

    def _build_grades_domain(self, university_id: int, grade_filter: str) -> list:
        """Build search domain for grades"""
        domain = []
        if university_id:
            domain.append(('enrollment_id.university_id', '=', university_id))
        
        if grade_filter == 'passed':
            domain.append(('grade', '>=', 5.0))
        elif grade_filter == 'failed':
            domain.append(('grade', '<', 5.0))
            
        return domain

    def _get_filtered_grades(self, user, is_admin: bool, domain: list) -> tuple:
        """Get grades based on user permissions"""
        Grade = request.env['university.grade'].sudo()
        University = request.env['university.university'].sudo()
        
        if is_admin:
            grades = Grade.search(domain)
            universities = University.search([])
        else:
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', user.id)
            ], limit=1)
            
            if not student:
                raise AccessError("No student record found for current user")
                
            domain.append(('student_id', '=', student.id))
            grades = Grade.search(domain)
            universities = University.search([
                ('id', 'in', grades.mapped('enrollment_id.university_id').ids)
            ])
            
        return grades, universities

    

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw: Any) -> str:
        """Display homepage with external news"""
        return request.render('Universidad.website_homepage', {
            'stats': self._get_university_stats(),
            'featured_universities': self._get_featured_universities(),
            'external_news': self._get_external_news()
        })

    

  

    @http.route(['/'], type='http', auth="public", website=True)
    def index(self, **kw):
      
        
        return request.render('Universidad.website_homepage', {
            'stats': self._get_university_stats(),
            'featured_universities': self._get_featured_universities(),
            'external_news': self._get_external_news()
        })

    