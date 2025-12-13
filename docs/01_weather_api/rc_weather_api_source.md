# rc_weather_api  Full Source Code


---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\__init__.py

```
from . import models

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\__manifest__.py

```
{
    "name": "RC Weather API (Tes Kompetensi)",
    "version": "19.0.2.0.0",
    "summary": "Pemeriksa cuaca eksternal sederhana (wttr.in + OpenWeather).",
    "description": """
Reka Cipta - Tes Kompetensi Odoo Developer
Bagian 1.1: Integrasi API Cuaca Sederhana.

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


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\models\__init__.py

```
from . import weather_request

```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\models\weather_request.py

```
from odoo import fields, models
from odoo.exceptions import UserError
import requests
from urllib.parse import quote


# ============================================================
#  A) WTTR.IN (existing) - keep as-is
# ============================================================
class RcWeatherRequest(models.Model):
    _name = "rc.weather.request"
    _description = "Weather Request (Tes Kompetensi) - wttr.in"

    name = fields.Char(
        string="Nama Kota",
        required=True,
        help="Contoh: 'Jakarta', 'Bandung', atau 'Tokyo'.",
    )
    temperature = fields.Float(string="Suhu (Â°C)", readonly=True)
    weather_description = fields.Char(string="Deskripsi Cuaca", readonly=True)
    last_updated = fields.Datetime(string="Terakhir Diperbarui", readonly=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("ok", "OK"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        readonly=True,
    )
    error_message = fields.Text(string="Pesan Error", readonly=True)

    def _get_api_base_url(self):
        """Base URL untuk API cuaca (wttr.in)."""
        return "https://wttr.in"

    def action_get_weather(self):
        """Dipanggil saat tombol 'Dapatkan Cuaca (wttr.in)' diklik."""
        for record in self:
            city = (record.name or "").strip()
            if not city:
                raise UserError("Nama kota tidak boleh kosong.")

            base = record._get_api_base_url().rstrip("/")
            city_slug = quote(city)
            url = f"{base}/{city_slug}"

            params = {"format": "j1"}

            try:
                resp = requests.get(url, params=params, timeout=10)
            except Exception as e:
                record.write({
                    "status": "error",
                    "error_message": f"Gagal menghubungi API cuaca (wttr.in): {e}",
                })
                continue

            if resp.status_code != 200:
                record.write({
                    "status": "error",
                    "error_message": (
                        f"API cuaca (wttr.in) mengembalikan HTTP {resp.status_code} "
                        f"untuk kota '{city}'."
                    ),
                })
                continue

            try:
                data = resp.json()
                current_list = data.get("current_condition") or []
                if not current_list:
                    raise ValueError("Response tidak memiliki current_condition.")

                current = current_list[0]
                temp_c_raw = current.get("temp_C")
                temp_c = float(temp_c_raw) if temp_c_raw not in (None, "") else 0.0

                weather_desc_list = current.get("weatherDesc") or []
                desc = (
                    weather_desc_list[0].get("value")
                    if weather_desc_list and isinstance(weather_desc_list[0], dict)
                    else ""
                )
            except Exception as e:
                record.write({
                    "status": "error",
                    "error_message": f"Gagal membaca data cuaca (wttr.in) untuk '{city}': {e}",
                })
                continue

            record.write({
                "temperature": temp_c,
                "weather_description": desc,
                "last_updated": fields.Datetime.now(),
                "status": "ok",
                "error_message": False,
            })


# ============================================================
#  B) OpenWeather (new) - separate model & menu
# ============================================================
class RcOpenWeatherRequest(models.Model):
    _name = "rc.openweather.request"
    _description = "Weather Request (Tes Kompetensi) - OpenWeather"

    name = fields.Char(
        string="Nama Kota",
        required=True,
        help="Contoh: 'Jakarta', 'Bandung', atau 'Tokyo,JP'.",
    )
    temperature = fields.Float(string="Suhu (Â°C)", readonly=True)
    weather_description = fields.Char(string="Deskripsi Cuaca", readonly=True)
    last_updated = fields.Datetime(string="Terakhir Diperbarui", readonly=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("ok", "OK"),
            ("error", "Error"),
        ],
        string="Status",
        default="draft",
        readonly=True,
    )
    error_message = fields.Text(string="Pesan Error", readonly=True)

    # ---- Helpers ----
    def _get_openweather_base_url(self):
        return "https://api.openweathermap.org/data/2.5/weather"

    def _get_openweather_api_key(self):
        """
        Ambil API key dari System Parameters.

        Key: rc_weather_api.openweather_api_key
        """
        Param = self.env["ir.config_parameter"].sudo()
        return (Param.get_param("rc_weather_api.openweather_api_key", default="") or "").strip()

    # ---- Action ----
    def action_get_openweather(self):
        """Dipanggil saat tombol 'Dapatkan Cuaca (OpenWeather)' diklik."""
        for record in self:
            city = (record.name or "").strip()
            if not city:
                raise UserError("Nama kota tidak boleh kosong.")

            api_key = record._get_openweather_api_key()
            if not api_key:
                raise UserError(
                    "OpenWeather API key belum dikonfigurasi.\n"
                    "Silakan set System Parameter:\n"
                    "- Key: rc_weather_api.openweather_api_key\n"
                    "- Value: <API Key OpenWeather>"
                )

            params = {
                "q": city,
                "appid": api_key,
                "units": "metric",
            }

            try:
                resp = requests.get(record._get_openweather_base_url(), params=params, timeout=10)
            except Exception as e:
                record.write({
                    "status": "error",
                    "error_message": f"Gagal menghubungi API OpenWeather: {e}",
                })
                continue

            # OpenWeather sering balikin JSON error walaupun status != 200
            if resp.status_code != 200:
                msg = ""
                try:
                    data = resp.json()
                    msg = data.get("message") or ""
                except Exception:
                    msg = ""
                if not msg:
                    msg = f"HTTP {resp.status_code}"
                record.write({
                    "status": "error",
                    "error_message": f"OpenWeather error untuk '{city}': {msg}",
                })
                continue

            try:
                data = resp.json()
                main = data.get("main") or {}
                weather_list = data.get("weather") or []
                desc = weather_list[0].get("description") if weather_list else ""

                temp_c = float(main.get("temp") or 0.0)
            except Exception as e:
                record.write({
                    "status": "error",
                    "error_message": f"Gagal parsing response OpenWeather untuk '{city}': {e}",
                })
                continue

            record.write({
                "temperature": temp_c,
                "weather_description": desc,
                "last_updated": fields.Datetime.now(),
                "status": "ok",
                "error_message": False,
            })


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\README.md

```
# RC Weather API (Tes Kompetensi â€“ Bagian 1.1)

Modul integrasi cuaca untuk Odoo 19 Community dengan **2 provider**:

1. **wttr.in** (tanpa API key)
2. **OpenWeather** (butuh API key via System Parameters)

## Tujuan

Mendemonstrasikan:

- Integrasi Odoo 19 dengan layanan eksternal via HTTP (`requests`)
- Form sederhana dengan tombol aksi
- Error handling & result display pada record yang sama
- Konfigurasi API key via `ir.config_parameter` (OpenWeather)

---

## Fitur

### Menu Backend
- **Pemeriksa Cuaca â†’ Pemeriksa Cuaca (wttr.in)**
- **Pemeriksa Cuaca â†’ Pemeriksa Cuaca (OpenWeather)**

### Model
- `rc.weather.request` (provider: wttr.in)
- `rc.openweather.request` (provider: OpenWeather)

### Field
- **Nama Kota** (`name`)
- **Suhu (Â°C)** (`temperature`)
- **Deskripsi Cuaca** (`weather_description`)
- **Terakhir Diperbarui** (`last_updated`)
- **Status** (`status`: Draft / OK / Error)
- **Pesan Error** (`error_message`)

---

## Cara Pakai (wttr.in)

1. Install modul `rc_weather_api`.
2. Buka:
   - **Pemeriksa Cuaca â†’ Pemeriksa Cuaca (wttr.in)**
3. Create record, isi **Nama Kota**
4. Klik **Dapatkan Cuaca (wttr.in)**

API:
- `https://wttr.in/<kota>?format=j1`

---

## Cara Pakai (OpenWeather)

### 1) Set API Key
1. Aktifkan Developer Mode (jika belum).
2. Masuk ke **Settings â†’ Technical â†’ Parameters â†’ System Parameters**
3. Create:
   - **Key**: `rc_weather_api.openweather_api_key`
   - **Value**: `<API key OpenWeather>`
4. Save.

### 2) Test di menu OpenWeather
1. Buka:
   - **Pemeriksa Cuaca â†’ Pemeriksa Cuaca (OpenWeather)**
2. Create record, isi **Nama Kota** (contoh: `Tokyo,JP` atau `Jakarta`)
3. Klik **Dapatkan Cuaca (OpenWeather)**

Endpoint:
- `https://api.openweathermap.org/data/2.5/weather?q=<city>&appid=<key>&units=metric`

---

## Error Handling

- Timeout / koneksi gagal â†’ Status `Error`, detail di **Pesan Error**
- HTTP status != 200 â†’ Status `Error`, detail error message (jika ada)
- JSON tidak sesuai / parsing error â†’ Status `Error`, detail parsing

---

## Mapping ke Soal Tes (Bagian 1.1)

- Menu baru + form + tombol aksi: âœ”
- Panggil API eksternal via Python `requests`: âœ”
- Tampilkan suhu + deskripsi di form yang sama: âœ”
- Validasi & error handling: âœ”
- Konfigurasi API key manual di System Parameters (OpenWeather): âœ”


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\security\ir.model.access.csv

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_rc_weather_request_user,access_rc_weather_request_user,model_rc_weather_request,base.group_user,1,1,1,1
access_rc_openweather_request_user,access_rc_openweather_request_user,model_rc_openweather_request,base.group_user,1,1,1,1


```

---

## C:\dev\odoo19ce_dev\custom_addons\rc_weather_api\views\rc_weather_views.xml

```
<odoo>

    <!-- ===================================================== -->
    <!-- Root Menu -->
    <!-- ===================================================== -->
    <menuitem id="menu_rc_weather_root"
              name="Pemeriksa Cuaca"
              sequence="10"/>

    <!-- ===================================================== -->
    <!-- A) WTTR.IN (existing) -->
    <!-- ===================================================== -->

    <!-- Action -->
    <record id="action_rc_weather_request" model="ir.actions.act_window">
        <field name="name">Pemeriksa Cuaca (wttr.in)</field>
        <field name="res_model">rc.weather.request</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p>Form sederhana untuk mengecek cuaca dari wttr.in berdasarkan nama kota.</p>
        </field>
    </record>

    <!-- Submenu -->
    <menuitem id="menu_rc_weather_request"
              name="Pemeriksa Cuaca (wttr.in)"
              parent="menu_rc_weather_root"
              action="action_rc_weather_request"
              sequence="10"/>

    <!-- List view -->
    <record id="view_rc_weather_request_list" model="ir.ui.view">
        <field name="name">rc.weather.request.list</field>
        <field name="model">rc.weather.request</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="temperature"/>
                <field name="weather_description"/>
                <field name="status"/>
                <field name="last_updated"/>
            </list>
        </field>
    </record>

    <!-- Form view -->
    <record id="view_rc_weather_request_form" model="ir.ui.view">
        <field name="name">rc.weather.request.form</field>
        <field name="model">rc.weather.request</field>
        <field name="arch" type="xml">
            <form string="Pemeriksa Cuaca (wttr.in)">
                <header>
                    <button name="action_get_weather"
                            string="Dapatkan Cuaca (wttr.in)"
                            type="object"
                            class="btn-primary"/>
                    <field name="status" widget="statusbar"
                           statusbar_visible="draft,ok,error"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="temperature" readonly="1"/>
                        <field name="weather_description" readonly="1"/>
                        <field name="last_updated" readonly="1"/>
                    </group>
                    <group>
                        <field name="error_message" readonly="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <!-- ===================================================== -->
    <!-- B) OPENWEATHER (new) -->
    <!-- ===================================================== -->

    <!-- Action -->
    <record id="action_rc_openweather_request" model="ir.actions.act_window">
        <field name="name">Pemeriksa Cuaca (OpenWeather)</field>
        <field name="res_model">rc.openweather.request</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p>Form sederhana untuk mengecek cuaca dari OpenWeather berdasarkan nama kota.</p>
        </field>
    </record>

    <!-- Submenu -->
    <menuitem id="menu_rc_openweather_request"
              name="Pemeriksa Cuaca (OpenWeather)"
              parent="menu_rc_weather_root"
              action="action_rc_openweather_request"
              sequence="20"/>

    <!-- List view -->
    <record id="view_rc_openweather_request_list" model="ir.ui.view">
        <field name="name">rc.openweather.request.list</field>
        <field name="model">rc.openweather.request</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="temperature"/>
                <field name="weather_description"/>
                <field name="status"/>
                <field name="last_updated"/>
            </list>
        </field>
    </record>

    <!-- Form view -->
    <record id="view_rc_openweather_request_form" model="ir.ui.view">
        <field name="name">rc.openweather.request.form</field>
        <field name="model">rc.openweather.request</field>
        <field name="arch" type="xml">
            <form string="Pemeriksa Cuaca (OpenWeather)">
                <header>
                    <button name="action_get_openweather"
                            string="Dapatkan Cuaca (OpenWeather)"
                            type="object"
                            class="btn-primary"/>
                    <field name="status" widget="statusbar"
                           statusbar_visible="draft,ok,error"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="temperature" readonly="1"/>
                        <field name="weather_description" readonly="1"/>
                        <field name="last_updated" readonly="1"/>
                    </group>
                    <group>
                        <field name="error_message" readonly="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

</odoo>


```
