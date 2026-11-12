-- Relasi many-to-many lokasi layanan dengan wilayah/desa.
-- Satu lokasi yang diklasifikasikan pada satu kecamatan dapat tersedia
-- pada banyak desa di dalam kecamatan tersebut.

CREATE TABLE IF NOT EXISTS lokasi_wilayah (
  id_lokasi INT NOT NULL,
  id_wilayah INT NOT NULL,
  PRIMARY KEY (id_lokasi, id_wilayah),
  KEY idx_lokasi_wilayah_wilayah (id_wilayah),
  CONSTRAINT fk_lokasi_wilayah_lokasi
    FOREIGN KEY (id_lokasi) REFERENCES lokasi_layanan (id_lokasi)
    ON DELETE CASCADE,
  CONSTRAINT fk_lokasi_wilayah_wilayah
    FOREIGN KEY (id_wilayah) REFERENCES wilayah (id_wilayah)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
