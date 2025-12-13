# RC Travel Product (Tes Kompetensi – Bagian 2)

Modul ekstensi untuk produk Odoo agar mendukung atribut travel.

## Tujuan

Menambahkan field spesifik travel pada data produk untuk digunakan dalam paket wisata atau tiket.

## Fitur

- Field tambahan pada `product.template`:
  - **Travel Destination**: Kota/lokasi tujuan.
  - **Travel Days**: Durasi perjalanan (hari).
  - **Travel Type**:
    - Flight
    - Hotel
    - Package

## Detail Teknis

- Model: `product.template` (inherit).
- Modul ini menjadi dependensi dasar untuk `rc_travel_ai`.
