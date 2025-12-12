from odoo import fields, models
from odoo.exceptions import UserError
import requests
from urllib.parse import quote


class RcWeatherRequest(models.Model):
    _name = "rc.weather.request"
    _description = "Weather Request (Tes Kompetensi)"

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

    # ---- Helpers ----
    def _get_api_base_url(self):
        """Base URL untuk API cuaca (wttr.in)."""
        return "https://wttr.in"

    # ---- Action ----
    def action_get_weather(self):
        """Dipanggil saat tombol 'Dapatkan Cuaca' diklik."""
        for record in self:
            city = (record.name or "").strip()
            if not city:
                raise UserError("Nama kota tidak boleh kosong.")

            # City harus ada di PATH, bukan di query string
            base = record._get_api_base_url().rstrip("/")
            city_slug = quote(city)  # handle spasi, dll.
            url = f"{base}/{city_slug}"

            params = {
                "format": "j1",  # JSON format
            }

            try:
                resp = requests.get(url, params=params, timeout=10)
            except Exception as e:
                record.write({
                    "status": "error",
                    "error_message": f"Gagal menghubungi API cuaca: {e}",
                })
                continue

            if resp.status_code != 200:
                record.write({
                    "status": "error",
                    "error_message": (
                        f"API cuaca mengembalikan HTTP {resp.status_code} "
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
                    "error_message": (
                        f"Gagal membaca data cuaca untuk '{city}': {e}"
                    ),
                })
                continue

            record.write({
                "temperature": temp_c,
                "weather_description": desc,
                "last_updated": fields.Datetime.now(),
                "status": "ok",
                "error_message": False,
            })
