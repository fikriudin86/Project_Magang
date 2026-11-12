-- Jalankan pada database parkir_db sebelum import_lokasi_layanan.sql.
-- Kolom kecamatan menyimpan klasifikasi area dari lokasi-layanan.xlsx.

ALTER TABLE lokasi_layanan
  ADD COLUMN kecamatan VARCHAR(100) NULL AFTER jarak_km;

ALTER TABLE lokasi_layanan
  ADD INDEX idx_lokasi_kecamatan (kecamatan);
