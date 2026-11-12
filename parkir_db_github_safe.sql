-- Database sample aman untuk repository GitHub.
-- Tidak berisi nama, nomor plat, atau riwayat operasional asli.
-- Database ini sengaja menggunakan nama parkir_db_demo agar tidak menimpa database lokal.

CREATE DATABASE IF NOT EXISTS parkir_db_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE parkir_db_demo;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS log_monitoring;
DROP TABLE IF EXISTS lokasi_wilayah;
DROP TABLE IF EXISTS driver;
DROP TABLE IF EXISTS kendaraan_dinas;
DROP TABLE IF EXISTS jenis_kendaraan;
DROP TABLE IF EXISTS lokasi_layanan;
DROP TABLE IF EXISTS wilayah;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE jenis_kendaraan (
  id_jenis INT NOT NULL AUTO_INCREMENT,
  nama_jenis VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_jenis)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE kendaraan_dinas (
  id_kendaraan INT NOT NULL AUTO_INCREMENT,
  no_plat VARCHAR(20) NOT NULL,
  konsumsi_km_per_liter FLOAT NOT NULL,
  id_jenis INT NOT NULL,
  PRIMARY KEY (id_kendaraan),
  UNIQUE KEY uk_kendaraan_no_plat (no_plat),
  KEY idx_kendaraan_jenis (id_jenis),
  CONSTRAINT fk_kendaraan_jenis
    FOREIGN KEY (id_jenis) REFERENCES jenis_kendaraan (id_jenis)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE driver (
  id_driver INT NOT NULL AUTO_INCREMENT,
  nama_driver VARCHAR(100) NOT NULL,
  id_kendaraan INT NOT NULL,
  PRIMARY KEY (id_driver),
  KEY idx_driver_kendaraan (id_kendaraan),
  CONSTRAINT fk_driver_kendaraan
    FOREIGN KEY (id_kendaraan) REFERENCES kendaraan_dinas (id_kendaraan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE wilayah (
  id_wilayah INT NOT NULL AUTO_INCREMENT,
  desa_kelurahan VARCHAR(100) NOT NULL,
  kecamatan VARCHAR(100) NOT NULL,
  PRIMARY KEY (id_wilayah),
  KEY idx_wilayah_kecamatan (kecamatan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE lokasi_layanan (
  id_lokasi INT NOT NULL AUTO_INCREMENT,
  nama_lokasi VARCHAR(100) NOT NULL,
  jarak_km FLOAT NOT NULL,
  kecamatan VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (id_lokasi),
  KEY idx_lokasi_kecamatan (kecamatan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE lokasi_wilayah (
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

CREATE TABLE log_monitoring (
  id INT NOT NULL AUTO_INCREMENT,
  no_plat VARCHAR(20) NOT NULL,
  waktu DATETIME NOT NULL,
  lokasi VARCHAR(100) NOT NULL,
  jarak_tempuh FLOAT NOT NULL,
  estimasi_bbm FLOAT NOT NULL,
  desa_kelurahan VARCHAR(100) DEFAULT NULL,
  kecamatan VARCHAR(100) DEFAULT NULL,
  id_wilayah INT DEFAULT NULL,
  id_lokasi INT DEFAULT NULL,
  id_driver INT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_log_waktu (waktu),
  KEY idx_log_plat (no_plat),
  KEY idx_log_wilayah (id_wilayah),
  KEY idx_log_lokasi (id_lokasi),
  KEY idx_log_driver (id_driver),
  CONSTRAINT fk_log_wilayah
    FOREIGN KEY (id_wilayah) REFERENCES wilayah (id_wilayah),
  CONSTRAINT fk_log_lokasi
    FOREIGN KEY (id_lokasi) REFERENCES lokasi_layanan (id_lokasi),
  CONSTRAINT fk_log_driver
    FOREIGN KEY (id_driver) REFERENCES driver (id_driver)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO jenis_kendaraan (id_jenis, nama_jenis) VALUES
  (1, 'Truk ArmRoll'),
  (2, 'Dump Truk'),
  (3, 'Pick Up'),
  (4, 'Roda Tiga');

INSERT INTO kendaraan_dinas (id_kendaraan, no_plat, konsumsi_km_per_liter, id_jenis) VALUES
  (1, 'DEMO-001', 5, 1),
  (2, 'DEMO-002', 5, 2),
  (3, 'DEMO-003', 8, 3),
  (4, 'DEMO-004', 18, 4);

INSERT INTO driver (id_driver, nama_driver, id_kendaraan) VALUES
  (1, 'DRIVER DEMO A', 1),
  (2, 'DRIVER DEMO B', 2),
  (3, 'DRIVER DEMO C', 3),
  (4, 'DRIVER DEMO D', 4);

INSERT INTO wilayah (id_wilayah, desa_kelurahan, kecamatan) VALUES
  (1, 'Desa Contoh A', 'Kecamatan Demo A'),
  (2, 'Desa Contoh B', 'Kecamatan Demo A'),
  (3, 'Desa Contoh C', 'Kecamatan Demo B'),
  (4, 'Desa Contoh D', 'Kecamatan Demo B');

INSERT INTO lokasi_layanan (id_lokasi, nama_lokasi, jarak_km, kecamatan) VALUES
  (1, 'Lokasi Demo A', 4, 'Kecamatan Demo A'),
  (2, 'Lokasi Demo B', 8, 'Kecamatan Demo A'),
  (3, 'Lokasi Demo C', 10, 'Kecamatan Demo B');

INSERT INTO lokasi_wilayah (id_lokasi, id_wilayah) VALUES
  (1, 1),
  (1, 2),
  (2, 1),
  (2, 2),
  (3, 3),
  (3, 4);

INSERT INTO log_monitoring
  (no_plat, waktu, lokasi, jarak_tempuh, estimasi_bbm,
   desa_kelurahan, kecamatan, id_wilayah, id_lokasi, id_driver)
VALUES
  ('DEMO-001', '2026-01-10 08:00:00', 'Lokasi Demo A', 4, 0.80,
   'Desa Contoh A', 'Kecamatan Demo A', 1, 1, 1),
  ('DEMO-003', '2026-01-10 10:00:00', 'Lokasi Demo B', 8, 1.00,
   'Desa Contoh B', 'Kecamatan Demo A', 2, 2, 3),
  ('DEMO-002', '2026-01-11 09:00:00', 'Lokasi Demo C', 10, 2.00,
   'Desa Contoh C', 'Kecamatan Demo B', 3, 3, 2);
