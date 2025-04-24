from odoo import http
from odoo.http import request
from typing import Dict, Any

class UniversityWebsiteMain(http.Controller):
    """Controlador para la página principal y funciones comunes"""
    
    def _get_external_news(self) -> list:
        """Get external education news links"""
        return [
            {
                'title': 'Latest Education News',
                'description': 'Stay updated with the latest news in education.',
                'link': 'https://www.educationweek.org/',
                'source': 'Education Week',
                'category': 'education'
            },
            {
                'title': 'World University Rankings',
                'description': 'Check the latest university rankings worldwide.',
                'link': 'https://www.timeshighereducation.com/world-university-rankings',
                'source': 'Times Higher Education',
                'category': 'rankings'
            },
            {
                'title': 'Research & Innovation',
                'description': 'Discover the latest research trends and innovations.',
                'link': 'https://www.sciencedaily.com/',
                'source': 'Science Daily',
                'category': 'research'
            }
        ]

    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw: Any) -> str:
        return request.render('Universidad.website_homepage', {
            'stats': self._get_university_stats(),
            'featured_universities': self._get_featured_universities(),
            'external_news': self._get_external_news()
        })

    def _get_university_stats(self) -> Dict[str, int]:
        """Get statistics for homepage"""
        return {
            'university_count': request.env['university.university'].sudo().search_count([]),
            'professor_count': request.env['university.professor'].sudo().search_count([]),
            'student_count': request.env['university.student'].sudo().search_count([]),
            'department_count': request.env['university.department'].sudo().search_count([])
        }

    def _get_featured_universities(self, limit: int = 3):
        """Get featured universities"""
        return request.env['university.university'].sudo().search([], limit=limit)