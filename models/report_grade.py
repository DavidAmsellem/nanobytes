"""
Module for managing university grade reports.

This module implements the ReportUniversityGrade model which handles the analytical
reporting of grades across the university system, including aggregated statistics
and performance metrics.
"""

from odoo import models, fields

class ReportUniversityGrade(models.Model):
    """
    University Grade Report Model.
    
    This class represents a SQL view for grade analytics. It aggregates grade data
    across different dimensions (university, professor, department, etc.) and
    provides various statistical measures.
    
    Attributes:
        university_id (Many2one): Related university
        professor_id (Many2one): Professor who issued the grades
        department_id (Many2one): Academic department
        student_id (Many2one): Student who received the grades
        subject_id (Many2one): Subject being graded
        adjusted_grade (Float): Grade after applying adjustment factor
        total_grade (Float): Sum of all grades
        count_grades (Integer): Total number of grades
        average_grade (Float): Average grade calculation
    """
    _name = 'report.university.grade'
    _description = 'University Grades Report'
    _auto = False  # Indicates this is a SQL view, not a table

    # Relational Fields
    university_id = fields.Many2one( #relacion con la universidad
        'university.university', #un reporte puede tener varias universidades
        string='University',
        readonly=True,
        help="University where the grades were issued"
    )
    
    professor_id = fields.Many2one( #relacion con el profesor
        'university.professor', #un reporte puede tener varios profesores
        string='Professor',
        readonly=True,
        help="Professor who issued the grades"
    )
    
    department_id = fields.Many2one( #relacion con el departamento
        'university.department',  #un reporte puede tener varios departamentos
        string='Department',
        readonly=True,
        help="Academic department responsible for the subject"
    )
    
    student_id = fields.Many2one(
        'university.student',
        string='Student',
        readonly=True,
        help="Student who received the grades"
    )
    
    subject_id = fields.Many2one(
        'university.subject',
        string='Subject',
        readonly=True,
        help="Subject being graded"
    )
    
    # Numerical Fields for Grade Analysis
    adjusted_grade = fields.Float(
        string='Adjusted Grade',
        group_operator="avg",
        readonly=True,
        help="Grade after applying 10% increase factor"
    )
    
    total_grade = fields.Float(
        string='Total Grade',
        readonly=True,
        store=False,
        help="Sum of all grades for the grouping"
    )
    
    count_grades = fields.Integer(
        string='Number of Grades',
        readonly=True,
        help="Total number of grades in the grouping"
    )
    
    average_grade = fields.Float(
        string='Average Grade',
        readonly=True,
        store=False,
        help="Average grade calculation for the grouping"
    )

    def init(self):
        """
        Initialize the SQL view for grade reporting.
        
        This method creates a PostgreSQL view that aggregates grade data
        across multiple dimensions with various statistical calculations.
        The view is recreated each time the server starts.
        """
        # Drop existing view if it exists
        self.env.cr.execute("DROP VIEW IF EXISTS report_university_grade CASCADE")
        
        # Create the analytical view
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
                    ROUND(AVG(g.grade)::numeric, 2) AS average_grade,
                    ROUND(AVG(g.grade)::numeric * 1.1, 2) AS adjusted_grade
                FROM 
                    university_grade g
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
