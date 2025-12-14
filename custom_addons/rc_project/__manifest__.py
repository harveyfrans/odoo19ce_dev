{
    'name': 'RC Project Extensions (Tes Kompetensi)',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Simulated Planning for Projects',
    'description': """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 6: Project Planning Simulation

        Fitur:
        - Field Planning (Start/End Date, Role, Hours) pada Task.
        - Validasi data (End Date >= Start Date).
        - View Calendar untuk visualisasi planning project.
        """,
    'author': 'Harvey',
    'depends': ['project'],
    'data': [
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
