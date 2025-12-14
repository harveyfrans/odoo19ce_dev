# RC HR Extensions (Tes Kompetensi – Bagian 1.2)

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

- Extend `hr.attendance` dengan field geo: ✔
- Logic pengisian otomatis geo coordinates: ✔
- Master data bahasa (`rc.lang`): ✔
- Relasi `hr.job` ke `rc.lang`: ✔

