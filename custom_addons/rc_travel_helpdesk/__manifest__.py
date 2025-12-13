{
    "name": "RC Travel Helpdesk",
    "version": "19.0.1.0.0",
    "summary": "Sistem tiket helpdesk sederhana (Tes Kompetensi).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 4: Manajemen Tiket Helpdesk.
    """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": [
        "sale",
        "rc_travel_ai",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/helpdesk_ticket_views.xml",
        "views/sale_order_views.xml",
        "views/helpdesk_menu.xml",
    ],
    "installable": True,
}
