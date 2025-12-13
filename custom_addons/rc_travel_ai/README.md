# RC Travel AI Simulation (Tes Kompetensi – Bagian 3)

Simulasi AI Assistant sederhana untuk rekomendasi paket travel.

## Tujuan

Mendemonstrasikan logika parsing teks sederhana (Mock AI) untuk merekomendasikan produk travel berdasarkan input natural language dari customer, dengan arsitektur yang mendukung **mixed carts**.

## Fitur

- **Menu**: AI Assistant (Di Website / Backend).
- **Logika Mock AI (Regex/Keyword Parsing)**:
  - Deteksi **Destinasi**: Bali, Bandung, Singapore, dll.
  - Deteksi **Tipe**: Flight, Hotel, Package.
  - Deteksi **Budget/Durasi**: Mengenali angka hari atau mata uang (juta/rb).
- **Rekomendasi Produk**:
  - Mencocokkan input dengan data di `rc_travel_product`.
  - Menampilkan daftar produk yang relevan.
- **Integrasi E-commerce Granular**:
  - `ai_log_id` disimpan di level **Sale Order Line**, bukan Sale Order.
  - Mendukung keranjang belanja campuran (produk rekomendasi AI + produk manual).
  - Data AI diteruskan dari sesi website ke line saat "Add to Cart".

## Cara Pakai

1. Buka menu **Pemeriksa Cuaca -> AI Log** (atau frontend website `/travel/ai`).
2. Masukkan pertanyaan customer, misal:
   > "Saya mau liburan ke Bali selama 5 hari budget 10 juta"
3. Klik **Process**.
4. Log akan terisi otomatis dengan hasil parsing.
5. Klik **Beli Sekarang** pada salah satu produk rekomendasi.
6. Produk akan masuk ke keranjang, dan line tersebut akan ditandai dengan sumber AI Log tersebut.

## Detail Teknis

- Model: `travel.ai.log`.
- Relasi: `sale_line_ids` (One2many ke `sale.order.line`).
- Website Integration: `request.session` menyimpan `rc_ai_log_id` sementara yang kemudian disuntikkan ke `sale.order.line` saat pembuatan.
