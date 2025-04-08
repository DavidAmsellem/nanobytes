{
    'name': 'Universidad',
    'version': '1.0',
    'depends': ['base', 'website', 'web', 'portal'],
    'images': ['static/description/icon.png'],
    'author': 'David Amsellem',
    'category': 'Educación',
    'description': 'Gestión de universidades',
    'data': [
        'views/university_views.xml',
        'data/website_menu.xml',
        'views/website_templates.xml',
        # 'views/university_student_form.xml',
        'data/mail_template_student_report.xml',
        'report/report_grade_views.xml',
        'views/report/report.xml',
        'views/department_views.xml',
        'views/professor_views.xml',
        'views/subject_views.xml',
        'views/student_views.xml',
        'views/enrollment_views.xml',
        'views/grade_views.xml',
        'views/report/report_student.xml',
        'security/ir.model.access.csv',
        # 'static/src/js/toaster_button_widget.xml',
       
        
    ],
    'assets': {
        'web.assets_backend': [
            'Universidad/static/src/scss/university_styles.scss',  
            'purchase/static/src/toaster_button/*',
       
            
        ],
    },
    'installable': True,
    'application': True,
}
