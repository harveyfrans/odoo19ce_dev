# rc_project  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\__init__.py

```
from . import models


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\__manifest__.py

```
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


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\models\__init__.py

```
from . import project_task


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\models\project_task.py

```
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    planned_start = fields.Datetime(string='Planned Start')
    planned_end = fields.Datetime(string='Planned End')
    planned_hours = fields.Float(string='Planned Hours')
    planned_role = fields.Selection([
        ('consultant', 'Consultant'),
        ('pm', 'Project Manager'),
        ('dev', 'Developer'),
        ('tester', 'Tester')
    ], string='Planned Role')

    @api.constrains('planned_start', 'planned_end')
    def _check_planned_dates(self):
        for task in self:
            if task.planned_start and task.planned_end:
                if task.planned_end < task.planned_start:
                    raise ValidationError("Planned End Date cannot be before Planned Start Date.")


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\README.md

```
# RC Project Extensions (Tes Kompetensi â€“ Bagian 1.3)

Modul simulasi "Planning" sederhana pada Project Management Odoo Community Edition.

## Tujuan

Mendemonstrasikan:
- Modifikasi model `project.task` untuk kebutuhan scheduling resourse.
- Penerapan `api.constrains` untuk validasi data.
- Kustomisasi view Form dan Calendar.

---

## Fitur

### Planning Simulation
Fitur ini meniru kemampuan modul Enterprise Planning secara sederhana.

- **Field Baru**:
  - `planned_start`, `planned_end`: Tanggal/jam rencana pengerjaan.
  - `planned_hours`: Estimasi durasi.
  - `planned_role`: Peran yang dibutuhkan (Consultant, PM, Dev, Tester).

- **Validasi**:
  - Sistem menolak penyimpanan jika `Planned End` lebih awal dari `Planned Start`.

- **Calendar View**:
  - Visualisasi task berdasarkan rentang waktu planned.

---

## Cara Pakai

1. Buka menu **Project -> Planning (Sim)**.
2. Anda akan melihat tampilan Calendar.
   - Klik pada slot waktu untuk membuat Task baru, atau
   - Buka list view untuk melihat detail.
3. Saat membuat task, isi:
   - **Planned Start** & **Planned End**
   - **Role** (misal: Consultant)
4. Save.
5. Coba set End Date sebelum Start Date -> Sistem akan memunculkan UserError.

---

## Mapping ke Soal Tes (Bagian 1.3)

- Extend `project.task` dengan field planning: âœ”
- Python Constraint (Start <= End): âœ”
- Menu khusus "Planning (Sim)": âœ”
- Tampilan Calendar: âœ”


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_project\views\project_task_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- 1) Form: add simulated planning fields (low blast-radius, safe) -->
    <record id="view_task_form2_planning" model="ir.ui.view">
        <field name="name">project.task.form.planning</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_form2"/>
        <field name="arch" type="xml">
            <sheet position="inside">
                <group string="Planning (Simulated)" name="planning_simulated">
                    <group>
                        <field name="planned_start"/>
                        <field name="planned_end"/>
                    </group>
                    <group>
                        <field name="planned_hours" widget="float_time"/>
                        <field name="planned_role"/>
                    </group>
                </group>
            </sheet>
        </field>
    </record>

    <!-- 2) Calendar: dedicated simulation view (does NOT override core calendar) -->
    <record id="view_task_calendar_simulation" model="ir.ui.view">
        <field name="name">project.task.calendar.simulation</field>
        <field name="model">project.task</field>
        <field name="arch" type="xml">
            <calendar
                string="Planning Simulation"
                date_start="planned_start"
                date_stop="planned_end">
                <field name="name"/>
            </calendar>
        </field>
    </record>

    <!-- 3) Action: explicitly binds this calendar view to a separate menu -->
    <record id="action_project_task_planning" model="ir.actions.act_window">
        <field name="name">Planning Simulation</field>
        <field name="res_model">project.task</field>
        <field name="view_mode">calendar,list,form</field>
        <field name="view_id" ref="view_task_calendar_simulation"/>
        <field name="domain">[('planned_start', '!=', False)]</field>
    </record>

    <menuitem id="menu_project_planning"
              name="Planning (Sim)"
              parent="project.menu_main_pm"
              action="action_project_task_planning"
              sequence="50"/>

    <!-- 4) Search: add filters anchored to <search> for version robustness -->
    <record id="view_task_search_planning" model="ir.ui.view">
        <field name="name">project.task.search.planning</field>
        <field name="model">project.task</field>
        <field name="inherit_id" ref="project.view_task_search_form"/>
        <field name="arch" type="xml">
            <xpath expr="//search" position="inside">
                <filter string="Has Planning" name="has_planning"
                        domain="[('planned_start', '!=', False)]"/>
                <separator/>
                <filter string="Role: Consultant" name="role_consultant"
                        domain="[('planned_role', '=', 'consultant')]"/>
                <filter string="Role: Dev" name="role_dev"
                        domain="[('planned_role', '=', 'dev')]"/>
            </xpath>
        </field>
    </record>

</odoo>


```
