# RC Project Extensions (Tes Kompetensi – Bagian 1.3)

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

- Extend `project.task` dengan field planning: ✔
- Python Constraint (Start <= End): ✔
- Menu khusus "Planning (Sim)": ✔
- Tampilan Calendar: ✔
