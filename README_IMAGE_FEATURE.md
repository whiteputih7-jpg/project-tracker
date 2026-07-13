# Fitur Input Gambar untuk Task

## Cara Menggunakan

### 1. Update Database Supabase
Pertama, jalankan SQL migration di Supabase SQL Editor:

```sql
-- Tambah kolom untuk menyimpan gambar (base64 encoded)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS image_data TEXT;

-- Tambah kolom untuk caption teks dari task
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS caption TEXT;
```

### 2. Cara Input Task dengan Gambar

Sekarang ada 3 cara untuk input task:

#### A. Task dengan Teks Saja (seperti biasa)
- Ketik teks di input field
- Tekan Enter atau klik tombol "+"

#### B. Task dengan Gambar + Caption
1. Klik tombol kamera (📷)
2. Pilih gambar dari device Anda
3. Preview gambar akan muncul
4. Ketik caption di input field (opsional)
5. Tekan Enter atau klik tombol "+"

#### C. Task dengan Gambar Tanpa Caption
1. Klik tombol kamera (📷)
2. Pilih gambar dari device Anda
3. Preview gambar akan muncul
4. Langsung klik tombol "+" (tanpa ketik caption)
5. Task akan ditampilkan dengan tulisan "Task dengan gambar"

### 3. Tampilan Task

- **Task dengan gambar**: Gambar akan ditampilkan di card task
- **Task dengan gambar + caption**: Gambar ditampilkan dengan caption di bawahnya
- **Task dengan caption saja**: Caption ditampilkan sebagai teks biasa

### 4. Riwayat Task Selesai

Task yang sudah selesai dan memiliki gambar juga akan menampilkan gambar di riwayat.

## Catatan Teknis

- Gambar disimpan dalam format base64 (data URL) di database
- Ukuran gambar yang disarankan: < 500KB untuk performa optimal
- Format gambar yang didukung: semua format yang didukung browser (JPG, PNG, GIF, WebP, dll)
