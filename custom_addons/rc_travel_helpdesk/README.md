# RC Travel Helpdesk (Tes Kompetensi – Bagian 4)

Manajemen tiket helpdesk sederhana untuk agen travel.

## Tujuan

Menyediakan sistem tracking issue sederhana yang terintegrasi dengan Sale Order dan AI Log, dengan logika agregasi cerdas untuk mixed carts.

## Fitur

- **Menu**:
  - Helpdesk -> Tickets
- **Model**: `helpdesk.ticket`.
- **Integrasi**:
  - Link otomatis ke **Sale Order** (asal transaksi).
  - Link otomatis ke **Multi AI Logs** (agregasi dari order lines).
- **Workflow Status**:
  - Draft -> Open -> Done.
- **Logika Agregasi Unik**:
  - Tiket dibuat otomatis saat **Sale Order Confirm**.
  - **Satu Tiket per Order**: Jika order berisi produk dari beberapa sesi AI berbeda (atau campuran), sistem hanya membuat satu tiket.
  - **Deskripsi Komprehensif**: Deskripsi tiket menggabungkan semua pertanyaan/konteks dari berbagai sesi AI yang terlibat dalam order tersebut.

## Cara Pakai

1. Lakukan transaksi penjualan via Website/Backend (yang melibatkan produk rekomendasi AI).
2. Confirm Order.
3. Cek menu **Helpdesk**.
4. Tiket baru akan muncul otomatis dengan:
   - Referensi Order.
   - Daftar AI Log terkait (Many2many).
   - Deskripsi lengkap (Gabungan konteks AI + Produk yang dibeli).
