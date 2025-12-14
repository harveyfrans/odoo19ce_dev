{
    'name': 'RC Payroll Simulation (Tes Kompetensi)',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Simulate payroll adjustments based on attendance',
    'description': """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 7: Payroll Simulation

        Fitur:
        - Master data Payroll Rules (Bonus/Penalty).
        - Wizard/Action untuk generate adjustment bulanan berdasarkan kehadiran.
        - Link dengan modul rc_hr (Attendance Count).
        """,
    'author': 'Harvey',
    'depends': ['hr', 'hr_attendance', 'rc_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/rc_payroll_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
