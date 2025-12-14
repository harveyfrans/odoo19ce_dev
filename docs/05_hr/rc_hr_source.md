# rc_hr  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\__init__.py

```
from . import models


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\__manifest__.py

```
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


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\data\rc_lang_demo.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="lang_en" model="rc.lang">
            <field name="name">English</field>
            <field name="code">EN</field>
        </record>
        <record id="lang_ja" model="rc.lang">
            <field name="name">Japanese</field>
            <field name="code">JA</field>
        </record>
        <record id="lang_zh" model="rc.lang">
            <field name="name">Mandarin</field>
            <field name="code">ZH</field>
        </record>
        <record id="lang_de" model="rc.lang">
            <field name="name">German</field>
            <field name="code">DE</field>
        </record>
        <record id="lang_ar" model="rc.lang">
            <field name="name">Arabic</field>
            <field name="code">AR</field>
        </record>
    </data>
</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\models\__init__.py

```
from . import rc_lang
from . import hr_attendance
from . import hr_job


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\models\hr_attendance.py

```
from odoo import models, fields, api
import hashlib

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_lat = fields.Float(string='Check-in Latitude', readonly=True)
    check_in_lng = fields.Float(string='Check-in Longitude', readonly=True)
    check_out_lat = fields.Float(string='Check-out Latitude', readonly=True)
    check_out_lng = fields.Float(string='Check-out Longitude', readonly=True)
    geo_source = fields.Selection([
        ('dummy', 'Dummy'),
        ('manual', 'Manual'),
        ('sim_api', 'Sim API')
    ], string='Geolocation Source', default='dummy')
    geo_note = fields.Char(string='Geolocation Note')

    def _get_dummy_coordinates(self, employee_id):
        """Generate dummy coordinates based on employee ID hash to be stable per employee."""
        if not employee_id:
            return 0.0, 0.0

        emp_hash = int(hashlib.sha256(str(employee_id).encode('utf-8')).hexdigest(), 16)

        # Base coordinates (Jakarta roughly)
        base_lat = -6.2
        base_lng = 106.8

        # Generate offset (-0.05 to +0.05)
        lat_offset = (emp_hash % 1000) / 10000.0 - 0.05
        lng_offset = ((emp_hash >> 10) % 1000) / 10000.0 - 0.05

        return base_lat + lat_offset, base_lng + lng_offset

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('geo_source', 'dummy') != 'dummy':
                continue

            employee_id = vals.get('employee_id')
            if not employee_id:
                continue

            lat, lng = self._get_dummy_coordinates(employee_id)

            # check-in coords (existing behavior)
            if vals.get('check_in') and not vals.get('check_in_lat'):
                vals['check_in_lat'] = lat
                vals['check_in_lng'] = lng

            # NEW: if check_out is already provided at create time (backfill), fill check-out coords too
            if vals.get('check_out') and not vals.get('check_out_lat'):
                vals['check_out_lat'] = lat
                vals['check_out_lng'] = lng

        return super().create(vals_list)

    def write(self, vals):
        # Guard to prevent recursion when we write geo fields ourselves
        if self.env.context.get('skip_rc_geo'):
            return super().write(vals)

        res = super().write(vals)

        # After check_out is set, backfill dummy check-out coordinates if missing
        if vals.get('check_out'):
            for record in self:
                if record.geo_source == 'dummy' and (not record.check_out_lat or not record.check_out_lng):
                    lat, lng = self._get_dummy_coordinates(record.employee_id.id)
                    record.with_context(skip_rc_geo=True).write({
                        'check_out_lat': lat,
                        'check_out_lng': lng,
                    })

        return res


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\models\hr_job.py

```
from odoo import models, fields

class HrJob(models.Model):
    _inherit = 'hr.job'

    foreign_language_ids = fields.Many2many(
        'rc.lang', 
        string='Kualifikasi Bahasa Asing'
    )


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\models\rc_lang.py

```
from odoo import models, fields

class RcLang(models.Model):
    _name = 'rc.lang'
    _description = 'Foreign Language Qualification'

    name = fields.Char(string='Language Name', required=True)
    code = fields.Char(string='Code', size=2)
    active = fields.Boolean(default=True)


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\README.md

```
# RC HR Extensions (Tes Kompetensi â€“ Bagian 1.2)

Modul ekstensi HR untuk Odoo 19 Community yang mencakup fitur Geolocation pada absensi dan kualifikasi bahasa pada lowongan kerja.

## Tujuan

Mendemonstrasikan:
- Modifikasi model standar (`hr.attendance`, `hr.job`).
- Penambahan field baru dan view inheritance.
- Logika backend sederhana (override `create`/`write`).

---

## Fitur

### 1. Geolocation pada Attendance
- **Field Baru**: `check_in_lat`, `check_in_lng`, `check_out_lat`, `check_out_lng`, `geo_source`.
- **Logic**: Secara otomatis mengisi koordinat "dummy" jika tidak tersedia dari frontend (simulasi hardware/kiosk).

### 2. Kualifikasi Bahasa (Job Positions)
- **Model Baru**: `rc.lang` (Master Data Bahasa).
- **Relasi**: Many2many antara Job Position (`hr.job`) dan Bahasa (`rc.lang`).

---

## Cara Pakai

### Simulasi Geolocation
1. Install modul `rc_hr`.
2. Masuk sebagai Employee, lakukan **Check In** / **Check Out**.
   - Sistem akan otomatis mendeteksi (atau mengisi dummy) koordinat.
3. Buka menu **Attendances** (Manager View).
4. Buka salah satu record absensi, cek tab **Geolocation**.

### Kualifikasi Bahasa
1. Buka menu **Recruitment -> Configuration -> Job Positions**.
2. Pilih Job Position (misal: "Developer").
3. Masuk tab **Qualifications**.
4. Tambahkan bahasa pada field **Kualifikasi Bahasa Asing**.

---

## Mapping ke Soal Tes (Bagian 1.2)

- Extend `hr.attendance` dengan field geo: âœ”
- Logic pengisian otomatis geo coordinates: âœ”
- Master data bahasa (`rc.lang`): âœ”
- Relasi `hr.job` ke `rc.lang`: âœ”



```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\security\ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_rc_lang_user,rc.lang.user,model_rc_lang,base.group_user,1,1,1,1


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\views\hr_attendance_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_hr_attendance_form_geo" model="ir.ui.view">
        <field name="name">hr.attendance.form.geo</field>
        <field name="model">hr.attendance</field>
        <field name="inherit_id" ref="hr_attendance.hr_attendance_view_form"/>
        <field name="arch" type="xml">
            <sheet position="inside">
                <group string="Geolocation" name="geolocation">
                    <group>
                        <field name="geo_source"/>
                        <field name="geo_note"/>
                    </group>
                    <group>
                        <field name="check_in_lat"/>
                        <field name="check_in_lng"/>
                        <field name="check_out_lat"/>
                        <field name="check_out_lng"/>
                    </group>
                </group>
            </sheet>
        </field>
    </record>

    <record id="view_hr_attendance_filter_geo" model="ir.ui.view">
        <field name="name">hr.attendance.filter.geo</field>
        <field name="model">hr.attendance</field>
        <field name="inherit_id" ref="hr_attendance.hr_attendance_view_filter"/>
        <field name="arch" type="xml">
            <xpath expr="//search" position="inside">
                <filter string="Has Coordinates"
                        name="has_coordinates"
                        domain="[('check_in_lat', '!=', False)]"/>
            </xpath>
        </field>
    </record>

    <record id="view_hr_attendance_tree_geo" model="ir.ui.view">
        <field name="name">hr.attendance.tree.geo</field>
        <field name="model">hr.attendance</field>
        <field name="inherit_id" ref="hr_attendance.view_attendance_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='check_out']" position="after">
                <field name="check_in_lat" string="Latitude (In)"/>
                <field name="check_in_lng" string="Longitude (In)"/>
                <field name="check_out_lat" string="Latitude (Out)"/>
                <field name="check_out_lng" string="Longitude (Out)"/>
            </xpath>
        </field>
    </record>

</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\views\hr_job_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_hr_job_form_lang" model="ir.ui.view">
        <field name="name">hr.job.form.lang</field>
        <field name="model">hr.job</field>
        <field name="inherit_id" ref="hr.view_hr_job_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page string="Qualifications">
                    <group>
                        <field name="foreign_language_ids" widget="many2many_tags"/>
                    </group>
                </page>
            </xpath>
        </field>
    </record>

    <record id="view_hr_job_tree_lang" model="ir.ui.view">
        <field name="name">hr.job.tree.lang</field>
        <field name="model">hr.job</field>
        <field name="inherit_id" ref="hr.view_hr_job_tree"/>
        <field name="arch" type="xml">
            <field name="department_id" position="after">
                <field name="foreign_language_ids" widget="many2many_tags" optional="show"/>
            </field>
        </field>
    </record>
</odoo>


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_hr\views\rc_lang_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_rc_lang_tree" model="ir.ui.view">
        <field name="name">rc.lang.tree</field>
        <field name="model">rc.lang</field>
        <field name="arch" type="xml">
            <list string="Languages" editable="bottom">
                <field name="name"/>
                <field name="code"/>
                <field name="active" widget="boolean_toggle"/>
            </list>
        </field>
    </record>

    <record id="view_rc_lang_form" model="ir.ui.view">
        <field name="name">rc.lang.form</field>
        <field name="model">rc.lang</field>
        <field name="arch" type="xml">
            <form string="Language">
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="code"/>
                        </group>
                        <group>
                            <field name="active"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_rc_lang" model="ir.actions.act_window">
        <field name="name">Foreign Languages</field>
        <field name="res_model">rc.lang</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
          <p class="o_view_nocontent_smiling_face">
            Create a new foreign language
          </p>
        </field>
    </record>

    <menuitem 
        id="menu_rc_lang_config" 
        name="Foreign Languages" 
        parent="hr.menu_human_resources_configuration" 
        action="action_rc_lang" 
        sequence="50"
    />
</odoo>


```
