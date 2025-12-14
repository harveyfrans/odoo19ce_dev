# RC Payroll Simulation (Tes Kompetensi – Bagian 1.4)

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

- Master data Payroll Rule: ✔
- Transaction data Payroll Run: ✔
- Logic menghitung jumlah hari hadir (count ID): ✔
- Logic pencocokan Rule (Bonus/Penalty): ✔
