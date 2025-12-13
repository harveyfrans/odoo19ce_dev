{
    "name": "RC Travel AI Simulation",
    "version": "19.0.2.0.0",
    "summary": "Simulasi AI untuk rekomendasi travel (Tes Kompetensi).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 3: Simulasi AI Assistant & Rekomendasi.
    """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
        "sale",
        "rc_travel_product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/travel_ai_templates.xml",
        "views/travel_ai_menu.xml",
    ],
    "installable": True,
}
