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
    temperature = fields.Float(string="Suhu (°C)", readonly=True)
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
    temperature = fields.Float(string="Suhu (°C)", readonly=True)
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
