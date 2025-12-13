# rc_travel_product  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\__init__.py

```
from . import models

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\__manifest__.py

```
{
    "name": "RC Travel Product",
    "version": "19.0.1.0.0",
    "summary": "Ekstensi produk untuk atribut travel (Tes Kompetensi).",
    "description": """
        Reka Cipta - Tes Kompetensi Odoo Developer
        Bagian 2: Data Master Produk Travel.
    """,
    "author": "Harvey",
    "license": "LGPL-3",
    "depends": ["product", "sale", "website_sale"],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
}

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\models\__init__.py

```
from . import product_template

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\models\product_template.py

```
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    travel_destination = fields.Char(string="Travel Destination")
    travel_days = fields.Integer(string="Travel Days")
    travel_type = fields.Selection([
        ("flight", "Flight"),
        ("hotel", "Hotel"),
        ("package", "Package"),
    ], string="Travel Type")


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\README.md

```
# RC Travel Product (Tes Kompetensi â€“ Bagian 2)

Modul ekstensi untuk produk Odoo agar mendukung atribut travel.

## Tujuan

Menambahkan field spesifik travel pada data produk untuk digunakan dalam paket wisata atau tiket.

## Fitur

- Field tambahan pada `product.template`:
  - **Travel Destination**: Kota/lokasi tujuan.
  - **Travel Days**: Durasi perjalanan (hari).
  - **Travel Type**:
    - Flight
    - Hotel
    - Package

## Detail Teknis

- Model: `product.template` (inherit).
- Modul ini menjadi dependensi dasar untuk `rc_travel_ai`.


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_travel_product\views\product_views.xml

```
<odoo>
    <record id="view_product_form_travel" model="ir.ui.view">
        <field name="name">product.template.travel.form</field>
        <field name="model">product.template</field>
        <field name="inherit_id" ref="product.product_template_only_form_view"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet/notebook" position="inside">
                <page string="Travel Info">
                    <group>
                        <field name="travel_destination"/>
                        <field name="travel_days"/>
                        <field name="travel_type"/>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>

```
