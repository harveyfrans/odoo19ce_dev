# RC Travel AI Simulation (Tes Kompetensi – Bagian 3)

Simulasi AI Assistant sederhana untuk rekomendasi paket travel.

## Tujuan

Mendemonstrasikan logika parsing teks sederhana (Mock AI) untuk merekomendasikan produk travel berdasarkan input natural language dari customer.

## Fitur

- **Menu**: AI Assistant (Di Website / Backend).
- **Logika Mock AI (Regex/Keyword Parsing)**:
  - Deteksi **Destinasi**: Bali, Bandung, Singapore, dll.
  - Deteksi **Tipe**: Flight, Hotel, Package.
  - Deteksi **Budget/Durasi**: Mengenali angka hari atau mata uang (juta/rb).
- **Rekomendasi Produk**:
  - Mencocokkan input dengan data di `rc_travel_product`.
  - Menampilkan daftar produk yang relevan.
- **Konversi ke Sale Order**:
  - Membuat SO dari hasil rekomendasi AI.

## Cara Pakai

1. Buka menu **Pemeriksa Cuaca -> AI Log**.
2. Klik **New**.
3. Masukkan pertanyaan customer, misal:
   > "Saya mau liburan ke Bali selama 5 hari budget 10 juta"
4. Klik **Process**.
5. Log akan terisi otomatis dengan:
   - Destinasi: Bali
   - Durasi: 5 Hari
   - Budget Max: 10.000.000
   - Produk Rekomendasi: (Daftar produk yang cocok).

## Detail Teknis

- Model: `travel.ai.log`.
- Parsing dilakukan via Python string manipulation (bukan LLM asli) sesuai spesifikasi soal.
