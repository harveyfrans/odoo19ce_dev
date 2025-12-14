{
    "name": "RC Weather API (Tes Kompetensi)",
    "version": "19.0.2.0.0",
    "summary": "Pemeriksa cuaca eksternal sederhana (wttr.in + OpenWeather).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 1: Integrasi API Cuaca Sederhana.

        Provider:
        - wttr.in (tanpa API key)
        - OpenWeather (butuh API key via System Parameters)
        """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/rc_weather_views.xml",
    ],
    "installable": True,
    "application": False,
}
