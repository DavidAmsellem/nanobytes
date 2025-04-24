{
    'name': 'University',
    'version': '1.2',
    'license': 'LGPL-3', 
    'depends': [
        'base',
        'web',
        'website',
        'portal',
        'web_editor',
        'website_sale',
    ],
    'images': ['static/description/icon.png'],
    'author': 'David Amsellem',
    'category': 'Education',
    'description': 'University Management System',
    'summary': 'A comprehensive system for managing universities, students, professors, and courses.',
    'data': [
        # Seguridad
        'security/security.xml',
        'security/ir.rule.xml',  
        'security/ir.model.access.csv',
        
        # Vistas
        'views/university_views.xml',
        'views/department_views.xml',
        'views/professor_views.xml',
        'views/subject_views.xml',
        'views/student_views.xml',
        'views/enrollment_views.xml',
        'views/grade_views.xml',
        
        # Datos
        'data/mail_template_student_report.xml',
        'data/mail_template_professor.xml',
        
        # Website Templates
        'views/templates/website/layout/website_menu.xml', 
        'views/templates/website/universities/university_list.xml',
        'views/templates/website/professors/professor_list.xml',
        'views/templates/website/students/student_list.xml',
        'views/templates/website/portal/grades.xml',
     
        'views/templates/website/layout/website_homepage.xml',
        
        # Wizard
        'wizard/mail_compose_message_view.xml',
        
        # Reportes
        'report/report_grade_views.xml',
        'views/report/report.xml',
        'views/report/report_student.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'Universidad/static/src/scss/university_styles.scss',
            'Universidad/static/src/img/default_university.png',
        ],
        'web.assets_frontend': [
            # SCSS
            'Universidad/static/src/scss/homepage.scss',
            'Universidad/static/src/scss/universities.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'i18n_languages': ['es_ES'],
}
