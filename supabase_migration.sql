-- SQL untuk menambahkan kolom baru ke tabel tasks di Supabase
-- Jalankan ini di SQL Editor Supabase Anda

-- Tambah kolom untuk menyimpan gambar (base64 encoded)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS image_data TEXT;

-- Tambah kolom untuk caption teks dari task
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS caption TEXT;

-- Catatan: 
-- 1. image_data akan menyimpan data gambar dalam format base64 (data URL)
-- 2. caption akan menyimpan teks deskripsi/caption untuk gambar
-- 3. Jika hanya ada teks tanpa gambar, caption akan berisi teks tersebut
-- 4. Jika hanya ada gambar tanpa caption, caption akan kosong dan task akan menampilkan "Task dengan gambar"
