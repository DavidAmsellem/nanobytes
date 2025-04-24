from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

class UniversityPortalGrades(http.Controller):
    """Controller for grades portal.
    
    This controller manages the display and filtering of student grades
    in the website portal, with different access levels for students
    and administrators.
    """

    @http.route('/my/grades', type='http', auth='user', website=True)
    def show_portal_grades(self, **kw: any) -> str:
        """Display grades in user portal.
        
        Args:
            **kw: Keyword arguments containing filtering options.
                university_id (int): ID of the university to filter grades.
                grade_filter (str): Type of grade filter ('all', 'passed', 'failed').
        
        Returns:
            str: Rendered template with grades information.
            
        Redirects:
            /my: If the user is neither admin nor student.
        """
        user = request.env.user
        is_admin = user.has_group('base.group_system')
        
        # Redirect if user is neither admin nor student
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
        """Build search domain for grades filtering.
        
        Args:
            university_id (int): ID of the university to filter.
            grade_filter (str): Type of grade filter ('all', 'passed', 'failed').
            
        Returns:
            list: Domain list for grade search.
        """
        domain = []
        if university_id:
            domain.append(('enrollment_id.university_id', '=', university_id))
        
        if grade_filter == 'passed':
            domain.append(('grade', '>=', 5.0))
        elif grade_filter == 'failed':
            domain.append(('grade', '<', 5.0))
            
        return domain

    def _get_filtered_grades(self, user, is_admin: bool, domain: list) -> tuple:
        """Get grades based on user permissions and filters.
        
        Args:
            user: Current user record.
            is_admin (bool): Whether the user has admin rights.
            domain (list): Search domain for grades filtering.
            
        Returns:
            tuple: Contains (grades, universities) records.
            
        Raises:
            AccessError: If no student record is found for non-admin user.
        """
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
