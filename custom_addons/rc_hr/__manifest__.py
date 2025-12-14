{
    'name': 'RC HR Extensions (Tes Kompetensi)',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Extensions for HR, Attendance, and Recruitment',
    'description': """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 5: HR Extensions

        Fitur:
        - Geolocation tracking pada Attendance (Check In/Out).
        - Kualifikasi Bahasa Asing pada Job Positions.
        """,
    'author': 'Harvey',
    'depends': ['hr', 'hr_attendance', 'hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_views.xml',
        'views/hr_job_views.xml',
        'views/rc_lang_views.xml',
        'data/rc_lang_demo.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
