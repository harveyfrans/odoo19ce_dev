# rc_payroll_sim  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\__init__.py

```
from . import models


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\__manifest__.py

```
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


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\models\__init__.py

```
from . import rc_payroll_rule
from . import rc_payroll_run
from . import rc_payroll_adjustment


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\models\rc_payroll_adjustment.py

```
from odoo import models, fields

class RcPayrollAdjustment(models.Model):
    _name = 'rc.payroll.adjustment'
    _description = 'Payroll Adjustment Line'

    run_id = fields.Many2one('rc.payroll.run', string='Payroll Run', ondelete='cascade', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    attendance_days = fields.Integer(string='Attendance Days', readonly=True)
    rule_id = fields.Many2one('rc.payroll.rule', string='Applied Rule')
    amount = fields.Float(string='Adjustment Amount', readonly=True)
    note = fields.Text(string='Note')


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\models\rc_payroll_rule.py

```
from odoo import models, fields

class RcPayrollRule(models.Model):
    _name = 'rc.payroll.rule'
    _description = 'Payroll Simulation Rule'

    name = fields.Char(string='Rule Name', required=True)
    rule_type = fields.Selection([
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty')
    ], string='Rule Type', required=True, default='bonus')
    amount = fields.Float(string='Amount', required=True, help="Positive value")
    min_attendance_days = fields.Integer(string='Min Attendance Days', default=0)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True)


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\models\rc_payroll_run.py

```
from odoo import models, fields, api
from datetime import timedelta

class RcPayrollRun(models.Model):
    _name = 'rc.payroll.run'
    _description = 'Payroll Simulation Run'

    name = fields.Char(string='Name', required=True, default='New Payroll Run')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft')
    line_ids = fields.One2many('rc.payroll.adjustment', 'run_id', string='Adjustment Lines')
    
    def action_compute(self):
        self.ensure_one()
        # Clear existing lines
        self.line_ids.unlink()
        
        # Get all employees
        employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id)])
        
        # Get active rules
        rules = self.env['rc.payroll.rule'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True)
        ])
        
        adjustment_vals = []
        
        for employee in employees:
            # Count attendance days
            # Simplest: count distinct date(check_in)
            # Need to convert date_to to datetime end of day to include full day for search if fields were datetime, 
            # but attendance check_in is datetime.
            
            start_dt = fields.Datetime.to_datetime(self.date_from)
            end_dt = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1, seconds=-1)
            
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt)
            ])
            
            # Distinct days
            worked_days = len(set(att.check_in.date() for att in attendances if att.check_in))
            
            # Apply rules
            applied_rule = None
            amount = 0.0
            note = ''
            
            # Find first matching rule? Or specific logic?
            # Goal: If attendance days >= min_attendance_days -> apply bonus
            # If attendance days < min_attendance_days -> apply penalty?
            # User requirement: "If attendance days >= min_attendance_days -> apply bonus. If attendance days < min_attendance_days -> apply penalty (depending on type)"
            # This implies rules define conditions.
            
            # Let's iterate rules and see if any match.
            # But conflicting rules? "Apply the first matching rule" as per requirement.
            
            for rule in rules:
                if rule.rule_type == 'bonus':
                    if worked_days >= rule.min_attendance_days:
                        applied_rule = rule
                        amount = rule.amount
                        note = f"Bonus applied: Worked {worked_days} days (>= {rule.min_attendance_days})"
                        break
                elif rule.rule_type == 'penalty':
                    if worked_days < rule.min_attendance_days:
                        applied_rule = rule
                        amount = -rule.amount # Penalty is negative adjustment
                        note = f"Penalty applied: Worked {worked_days} days (< {rule.min_attendance_days})"
                        break
            
            if applied_rule:
                adjustment_vals.append({
                    'run_id': self.id,
                    'employee_id': employee.id,
                    'attendance_days': worked_days,
                    'rule_id': applied_rule.id,
                    'amount': amount,
                    'note': note,
                })
        
        self.env['rc.payroll.adjustment'].create(adjustment_vals)
        self.state = 'computed'

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'

    def action_reset_draft(self):
        self.ensure_one()
        self.state = 'draft'


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\README.md

```
# RC Payroll Simulation (Tes Kompetensi â€“ Bagian 1.4)

Modul simulasi perhitungan "Adjustment" gaji (Bonus/Denda) berdasarkan rekap kehadiran (Jumlah Hari Masuk) per bulan.

## Tujuan

Mendemonstrasikan:
- Pembuatan Master Data sederhana (`rc.payroll.rule`).
- Business logic untuk menghitung data berdasarkan periode (Date Range).
- Batch processing sederhana (One-click generation untuk banyak Employee).

---

## Fitur

### 1. Payroll Rules (Master Data)
- Mendefinisikan aturan main. Contoh:
  - "Jika hadir >= 20 hari, bonus Rp 500.000"
  - "Jika hadir < 10 hari, denda Rp 200.000"

### 2. Payroll Run (Transaksi Bulanan)
- Object untuk menjalankan perhitungan massal dalam periode tertentu (misal: Desember 2025).
- Menghitung jumlah hari kehadiran (`hr.attendance`) tiap karyawan tanpa absen (per employee).
- Mencocokkan dengan Rule yang berlaku.
- Menghasilkan line adjustment.

---

## Cara Pakai

1. **Setup Rules**:
   - Buka **Payroll Sim -> Payroll Rules**.
   - Buat Rule baru:
     - Name: "Rajin Pangkal Kaya"
     - Type: **Bonus**
     - Min Days: **20**
     - Amount: **1,000,000**
2. **Setup Rules (Optional - Penalty)**:
   - Buat Rule baru:
     - Name: "Malas"
     - Type: **Penalty**
     - Min Days: **0** (Logic disesuaikan, misal logic < X belum ada di simple implementation ini, tapi kita pakai logic >= Min Days for simplicity). *Catatan: Logic saat ini adalah "Match highest Min Days rule".*
3. **Execute Run**:
   - Buka **Payroll Sim -> Payroll Runs**.
   - Create Baru: "Desember 2025".
   - Set Tanggal: 1 Des - 31 Des.
   - Klik **Compute Adjustments**.
4. **Cek Hasil**:
   - Lihat tab **Adjustments**.
   - Sistem akan melist karyawan yang memenuhi kriteria rule.

---

## Mapping ke Soal Tes (Bagian 1.4)

- Master data Payroll Rule: âœ”
- Transaction data Payroll Run: âœ”
- Logic menghitung jumlah hari hadir (count ID): âœ”
- Logic pencocokan Rule (Bonus/Penalty): âœ”


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\security\ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_rc_payroll_rule_user,rc.payroll.rule.user,model_rc_payroll_rule,base.group_user,1,1,1,1
access_rc_payroll_run_user,rc.payroll.run.user,model_rc_payroll_run,base.group_user,1,1,1,1
access_rc_payroll_adjustment_user,rc.payroll.adjustment.user,model_rc_payroll_adjustment,base.group_user,1,1,1,1


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_payroll_sim\views\rc_payroll_views.xml

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Payroll Rules Views -->
    <record id="view_rc_payroll_rule_tree" model="ir.ui.view">
        <field name="name">rc.payroll.rule.tree</field>
        <field name="model">rc.payroll.rule</field>
        <field name="arch" type="xml">
            <list string="Payroll Rules">
                <field name="name"/>
                <field name="rule_type"/>
                <field name="min_attendance_days"/>
                <field name="amount"/>
                <field name="company_id" groups="base.group_multi_company"/>
                <field name="active" widget="boolean_toggle"/>
            </list>
        </field>
    </record>

    <record id="view_rc_payroll_rule_form" model="ir.ui.view">
        <field name="name">rc.payroll.rule.form</field>
        <field name="model">rc.payroll.rule</field>
        <field name="arch" type="xml">
            <form string="Payroll Rule">
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="rule_type"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="active"/>
                        </group>
                        <group>
                            <field name="min_attendance_days"/>
                            <field name="amount"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Payroll Run Views -->
    <record id="view_rc_payroll_run_tree" model="ir.ui.view">
        <field name="name">rc.payroll.run.tree</field>
        <field name="model">rc.payroll.run</field>
        <field name="arch" type="xml">
            <list string="Payroll Runs" decoration-info="state == 'draft'" decoration-muted="state == 'confirmed'">
                <field name="name"/>
                <field name="date_from"/>
                <field name="date_to"/>
                <field name="company_id" groups="base.group_multi_company"/>
                <field name="state" widget="badge" decoration-info="state == 'draft'" decoration-success="state == 'confirmed'"/>
            </list>
        </field>
    </record>

    <record id="view_rc_payroll_run_form" model="ir.ui.view">
        <field name="name">rc.payroll.run.form</field>
        <field name="model">rc.payroll.run</field>
        <field name="arch" type="xml">
            <form string="Payroll Run">
                <header>
                    <button name="action_compute" string="Compute Adjustments" type="object" invisible="state != 'draft'" class="oe_highlight"/>
                    <button name="action_confirm" string="Confirm" type="object" invisible="state != 'computed'" class="oe_highlight"/>
                    <button name="action_reset_draft" string="Reset to Draft" type="object" invisible="state == 'draft'"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                        <group>
                            <field name="date_from"/>
                            <field name="date_to"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Adjustments">
                            <field name="line_ids" readonly="1">
                                <list>
                                    <field name="employee_id"/>
                                    <field name="attendance_days"/>
                                    <field name="rule_id"/>
                                    <field name="amount" sum="Total"/>
                                    <field name="note"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Actions -->
    <record id="action_rc_payroll_rule" model="ir.actions.act_window">
        <field name="name">Payroll Rules</field>
        <field name="res_model">rc.payroll.rule</field>
        <field name="view_mode">list,form</field>
    </record>

    <record id="action_rc_payroll_run" model="ir.actions.act_window">
        <field name="name">Payroll Runs</field>
        <field name="res_model">rc.payroll.run</field>
        <field name="view_mode">list,form</field>
    </record>

    <!-- Menus -->
    <menuitem id="menu_rc_payroll_root" name="Payroll Sim" web_icon="hr,static/description/icon.png" sequence="20"/>
    <menuitem id="menu_rc_payroll_run" name="Payroll Runs" parent="menu_rc_payroll_root" action="action_rc_payroll_run" sequence="10"/>
    <menuitem id="menu_rc_payroll_rule" name="Payroll Rules" parent="menu_rc_payroll_root" action="action_rc_payroll_rule" sequence="20"/>
</odoo>


```
