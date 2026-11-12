-- Jalankan setelah tabel lokasi_wilayah sudah tersedia.
-- Relasi lokasi dengan desa disimpan di tabel lokasi_wilayah.

ALTER TABLE lokasi_layanan
  DROP FOREIGN KEY fk_lokasi_wilayah;

ALTER TABLE lokasi_layanan
  DROP INDEX idx_lokasi_wilayah,
  DROP COLUMN id_wilayah;
