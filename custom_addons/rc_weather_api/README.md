# RC Weather API (Tes Kompetensi – Bagian 1.1)

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
- **Pemeriksa Cuaca → Pemeriksa Cuaca (wttr.in)**
- **Pemeriksa Cuaca → Pemeriksa Cuaca (OpenWeather)**

### Model
- `rc.weather.request` (provider: wttr.in)
- `rc.openweather.request` (provider: OpenWeather)

### Field
- **Nama Kota** (`name`)
- **Suhu (°C)** (`temperature`)
- **Deskripsi Cuaca** (`weather_description`)
- **Terakhir Diperbarui** (`last_updated`)
- **Status** (`status`: Draft / OK / Error)
- **Pesan Error** (`error_message`)

---

## Cara Pakai (wttr.in)

1. Install modul `rc_weather_api`.
2. Buka:
   - **Pemeriksa Cuaca → Pemeriksa Cuaca (wttr.in)**
3. Create record, isi **Nama Kota**
4. Klik **Dapatkan Cuaca (wttr.in)**

API:
- `https://wttr.in/<kota>?format=j1`

---

## Cara Pakai (OpenWeather)

### 1) Set API Key
1. Aktifkan Developer Mode (jika belum).
2. Masuk ke **Settings → Technical → Parameters → System Parameters**
3. Create:
   - **Key**: `rc_weather_api.openweather_api_key`
   - **Value**: `<API key OpenWeather>`
4. Save.

### 2) Test di menu OpenWeather
1. Buka:
   - **Pemeriksa Cuaca → Pemeriksa Cuaca (OpenWeather)**
2. Create record, isi **Nama Kota** (contoh: `Tokyo,JP` atau `Jakarta`)
3. Klik **Dapatkan Cuaca (OpenWeather)**

Endpoint:
- `https://api.openweathermap.org/data/2.5/weather?q=<city>&appid=<key>&units=metric`

---

## Error Handling

- Timeout / koneksi gagal → Status `Error`, detail di **Pesan Error**
- HTTP status != 200 → Status `Error`, detail error message (jika ada)
- JSON tidak sesuai / parsing error → Status `Error`, detail parsing

---

## Mapping ke Soal Tes (Bagian 1.1)

- Menu baru + form + tombol aksi: ✔
- Panggil API eksternal via Python `requests`: ✔
- Tampilkan suhu + deskripsi di form yang sama: ✔
- Validasi & error handling: ✔
- Konfigurasi API key manual di System Parameters (OpenWeather): ✔
