{
    'name': 'Universidad',
    'version': '1.0',
    'license': 'LGPL-3', 
    'depends': ['base', 'website', 'web', 'portal'],
    'images': ['static/description/icon.png'],
    'author': 'David Amsellem',
    'category': 'Educación',
    'description': 'Gestión de universidades',
    'data': [
        # Seguridad
        'security/ir.model.access.csv',
        
        # Vistas
        'views/menu_views.xml',
        'views/university_views.xml',
        'views/department_views.xml',
        'views/professor_views.xml',
        'views/subject_views.xml',
        'views/student_views.xml',
        'views/enrollment_views.xml',
        'views/grade_views.xml',
        
        # Datos
        'data/website_menu.xml',
        'data/mail_template.xml',
        
        # Reportes
        'report/report_grade_views.xml',
        'views/report/report.xml',
        'views/report/report_student.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'Universidad/static/src/scss/university_styles.scss',
            'Universidad/static/src/img/default_university.png',
        ],
    },
    'installable': True,
    'application': True,
}
