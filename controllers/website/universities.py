from odoo import http
from odoo.http import request
from typing import Dict, Any

class UniversityWebsiteUniversities(http.Controller):
    """Controlador para las páginas de universidades"""

    def _get_theme_color(self, university_id: int) -> Dict[str, str]:
        """
        Obtiene los colores del tema para una universidad específica basado en su ID.
        
        Args:
            university_id (int): ID de la universidad
            
        Returns:
            Dict[str, str]: Diccionario con colores de fondo y borde
            
        Example:
            >>> self._get_theme_color(1)
            {'bg': '#e8f4f2', 'border': '#92d3c7'}
        """
        THEME_COLORS = {
            0: {'bg': '#ffecee', 'border': '#ff9eaa'},  # Rosa suave
            1: {'bg': '#e8f4f2', 'border': '#92d3c7'},  # Verde menta
            2: {'bg': '#fff4e3', 'border': '#ffd699'},  # Amarillo pastel
            3: {'bg': '#eae4f2', 'border': '#b39ddb'},  # Púrpura suave
            4: {'bg': '#e3f2ff', 'border': '#90caf9'},  # Azul claro
            5: {'bg': '#f0f8e5', 'border': '#aed581'}   # Verde lima
        }
        return THEME_COLORS[university_id % 6]

    @http.route('/universities', type='http', auth='public', website=True)
    def list_universities(self, **kw: Any) -> str:
        """
        Muestra la lista de todas las universidades en el sitio web.
        Incluye funcionalidad de búsqueda.
        """
        domain = []
        search_term = kw.get('search', '').strip()
        
        if search_term:
            domain = [
                '|',
                ('name', 'ilike', search_term),
                ('city', 'ilike', search_term)
            ]
        
        universities = request.env['university.university'].sudo().search(domain)
        
        return request.render('Universidad.website_universities', {
            'universities': universities,
            'search': search_term,
        })