from odoo import models, fields

class ReportUniversityGrade(models.Model):
    _name = 'report.university.grade'
    _description = 'University Grades Report'
    _auto = False  # Modelo basado en vista SQL

    university_id = fields.Many2one('university.university', string='University', readonly=True)
    professor_id = fields.Many2one('university.professor', string='Professor', readonly=True)
    department_id = fields.Many2one('university.department', string='Department', readonly=True)
    student_id = fields.Many2one('university.student', string='Student', readonly=True)
    subject_id = fields.Many2one('university.subject', string='Subject', readonly=True)
    adjusted_grade = fields.Float(string='Adjusted Grade',  group_operator="avg", readonly=True)

    total_grade = fields.Float(string='Total Grade', readonly=True)
    count_grades = fields.Integer(string='Number of Grades', readonly=True)
    average_grade = fields.Float(string='Average Grade', readonly=True)

    def init(self):
        # Elimina la vista si ya existe
        self.env.cr.execute("DROP VIEW IF EXISTS report_university_grade CASCADE")

        # Crea la nueva vista SQL
        self.env.cr.execute("""
            CREATE VIEW report_university_grade AS (
    SELECT
        MIN(g.id) AS id,
        e.university_id,
        e.professor_id,
        p.department_id,
        g.student_id,
        e.subject_id,
        SUM(g.grade) AS total_grade,
        COUNT(g.id) AS count_grades,
        CASE
            WHEN COUNT(g.id) > 0 THEN ROUND(SUM(g.grade)::numeric / COUNT(g.id), 2)
            ELSE 0
        END AS average_grade,
        CASE
            WHEN COUNT(g.id) > 0 THEN ROUND((SUM(g.grade)::numeric / COUNT(g.id)) / COUNT(g.id), 2)
            ELSE 0
        END AS adjusted_grade
    FROM university_grade g
    JOIN university_enrollment e ON g.enrollment_id = e.id
    JOIN university_professor p ON e.professor_id = p.id
    GROUP BY
        e.university_id,
        e.professor_id,
        p.department_id,
        g.student_id,
        e.subject_id


            )
        """)
