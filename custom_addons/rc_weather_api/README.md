# RC Weather API (Tes Kompetensi – Bagian 1.1)

Integrasi API cuaca sederhana menggunakan layanan publik `wttr.in` (tanpa API key).

## Tujuan

Mendemonstrasikan:

- Integrasi Odoo 19 dengan layanan eksternal via HTTP (`requests`).
- Form sederhana dengan tombol aksi.
- Penanganan error dan tampilan hasil di field yang sama.

## Fitur

- Menu backend: **Pemeriksa Cuaca → Pemeriksa Cuaca Eksternal**.
- Model: `rc.weather.request`.
- Field utama:
  - **Nama Kota** (`name`)
  - **Suhu (°C)` (`temperature`)
  - **Deskripsi Cuaca** (`weather_description`)
  - **Terakhir Diperbarui** (`last_updated`)
  - **Status** (`status`: Draft / OK / Error)
  - **Pesan Error** (`error_message`)
- Tombol **Dapatkan Cuaca**:
  - Memanggil layanan `https://wttr.in/<kota>?format=j1`
  - Mengambil suhu dalam °C dan deskripsi cuaca
  - Menyimpan hasil di record yang sama

## Cara Pakai

1. Pastikan modul `rc_weather_api` terinstall.
2. Buka menu:

   - **Pemeriksa Cuaca → Pemeriksa Cuaca Eksternal**

3. Klik **New**, isi:

   - **Nama Kota** – contoh: `Jakarta`, `Bandung`, `Tokyo`.

4. Klik tombol **Dapatkan Cuaca**:

   - Jika sukses:
     - **Suhu (°C)** dan **Deskripsi Cuaca** terisi.
     - **Status** = `OK`.
     - **Pesan Error** kosong.
   - Jika gagal (jaringan / format response / HTTP error):
     - **Status** = `Error`.
     - Detail disimpan di **Pesan Error**.

## Detail Teknis

- Layanan eksternal: `wttr.in` JSON (`?format=j1`).
- Library HTTP: `requests`.
- Parsing data:
  - `current_condition[0].temp_C` → `temperature`
  - `current_condition[0].weatherDesc[0].value` → `weather_description`
- Error handling:
  - Timeout / koneksi → pesan error disimpan di field *Pesan Error*.
  - HTTP status ≠ 200 → pesan error berisi kode HTTP dan nama kota.
  - Struktur JSON tidak sesuai → pesan error dengan detail parsing.

## Mapping ke Soal Tes (Bagian 1.1)

- **Menu baru**: ✔ `Pemeriksa Cuaca Eksternal`.
- **Form view** dengan field kota + tombol aksi: ✔
- **Panggil API eksternal** menggunakan Python + `requests`: ✔
- **Tampilkan suhu + deskripsi cuaca** di form yang sama: ✔
- **Validasi & error handling**: ✔
- **Output**: modul kustom penuh + siap untuk di-screenshot dari Odoo. ✔
