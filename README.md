# Sistem Monitoring Kendaraan Dinas

Aplikasi desktop berbasis Python untuk monitoring kendaraan dinas menggunakan kamera laptop, deteksi area plat dengan YOLO, pembacaan teks menggunakan Tesseract OCR, pencatatan perjalanan ke MySQL, klasifikasi wilayah, perhitungan estimasi BBM, riwayat monitoring, statistik, dan export laporan Excel.

## 1. Fitur Aplikasi

- Login dengan tiga role: Operator, Admin, dan Admin Utama.
- Kamera laptop atau webcam untuk proses monitoring.
- Deteksi area plat nomor menggunakan model YOLO.
- Pembacaan plat nomor menggunakan Tesseract OCR.
- Pencarian data kendaraan dan driver berdasarkan plat.
- Penampilan otomatis jenis kendaraan dan konsumsi BBM.
- CRUD kendaraan, driver, jenis kendaraan, wilayah, dan lokasi layanan.
- Filter desa berdasarkan kecamatan.
- Filter lokasi layanan berdasarkan kecamatan dan relasi wilayah/desa.
- Penyimpanan data perjalanan ke tabel `log_monitoring`.
- Perhitungan jarak tempuh dan estimasi BBM.
- Halaman `Riwayat & Laporan` dengan filter plat, jenis kendaraan, dan rentang tanggal.
- Export data yang sudah difilter ke Excel.
- Dashboard dan statistik penggunaan kendaraan.

## 2. Teknologi

- Python 3
- Tkinter dan `ttk` untuk antarmuka desktop
- OpenCV untuk kamera dan pemrosesan gambar
- Ultralytics YOLO untuk deteksi area plat
- Tesseract OCR untuk membaca teks plat
- MySQL/MariaDB melalui XAMPP
- `mysql-connector-python` untuk koneksi database
- Pandas dan OpenPyXL untuk export Excel
- Pillow untuk menampilkan frame kamera pada Tkinter

## 3. Struktur Folder dan File

```text
kp_scan_plat/
├── dashboard_monitoring.py
├── cctv_test.py
├── parkir_db.sql
├── parkir_db_github_safe.sql
├── migrasi_import_lokasi_layanan.sql
├── migrasi_relasi_lokasi_wilayah.sql
├── migrasi_hapus_id_wilayah_lokasi.sql
├── import_lokasi_layanan.sql
├── requirements.txt
├── yolov8n.pt
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── main_app.py
├── plat_dataset/
├── runs/
│   └── detect/train/weights/best.pt
└── laporan/
```

File installer Python, installer XAMPP, script percobaan video lama, migrasi lama, dan README duplikat sudah dihapus karena tidak diperlukan oleh aplikasi utama.

## 4. Fungsi Setiap Source Code

### `dashboard_monitoring.py`

Entry point aplikasi. File ini tidak berisi seluruh logika aplikasi, tetapi mengimpor class utama kemudian menjalankan event loop Tkinter.

```python
from app.main_app import ModernMonitoringApp

if __name__ == "__main__":
    ModernMonitoringApp().run()
```

Jalankan aplikasi melalui file ini:

```powershell
py dashboard_monitoring.py
```

### `app/main_app.py`

Merupakan pusat aplikasi dan berisi class `ModernMonitoringApp`. Fungsi utamanya meliputi:

- Membuat window dan layout aplikasi.
- Membuat halaman login dan memeriksa role pengguna.
- Membuat sidebar sesuai hak akses.
- Membuka kamera laptop atau webcam.
- Menjalankan YOLO dan Tesseract OCR.
- Mencari data kendaraan, driver, dan jenis kendaraan.
- Mengatur pilihan kecamatan, desa, dan lokasi layanan.
- Menyimpan data monitoring.
- Menampilkan dashboard, statistik, dan riwayat.
- Menjalankan CRUD data master.
- Memfilter riwayat berdasarkan plat, jenis, dan tanggal.
- Membuat file laporan Excel.
- Menutup kamera dan koneksi database saat aplikasi ditutup.

Method penting:

| Method | Fungsi |
|---|---|
| `show_login()` | Menampilkan halaman login |
| `show_main_app()` | Membuat layout utama dan sidebar |
| `show_monitoring()` | Menampilkan kamera dan form monitoring |
| `show_dashboard()` | Menampilkan ringkasan sistem |
| `show_kendaraan()` | Menampilkan data kendaraan |
| `show_driver()` | Menampilkan data driver |
| `show_jenis()` | Menampilkan jenis kendaraan |
| `show_wilayah()` | Menampilkan data wilayah |
| `show_lokasi()` | Menampilkan lokasi layanan |
| `show_laporan()` | Menampilkan riwayat, filter, dan export Excel |
| `show_statistik()` | Menampilkan grafik dan ringkasan statistik |
| `get_log_rows()` | Mengambil data riwayat dengan filter |
| `get_summary_stats()` | Menghitung jumlah perjalanan, jarak, dan BBM |
| `export_excel()` | Membuat file `.xlsx` |
| `get_lokasi_options()` | Mengambil lokasi sesuai wilayah terpilih |
| `execute()` | Menjalankan query perubahan data dan commit |

### `app/config.py`

Berisi konfigurasi terpusat aplikasi:

- `DB_CONFIG`: host, user, password, dan nama database.
- `TESSERACT_CMD`: lokasi file executable Tesseract.
- `YOLO_MODEL_PATH`: lokasi model deteksi plat yang digunakan.
- `USERS`: akun demo dan role pengguna.
- `ROLE_MENUS`: daftar menu untuk setiap role.
- `ROLE_HOME`: halaman awal setiap role.
- `COLORS`: warna antarmuka aplikasi.

Jika lokasi Tesseract atau model YOLO berbeda, ubah konfigurasi di file ini.

### `app/__init__.py`

Menandai folder `app` sebagai Python package sehingga modul di dalamnya dapat diimpor oleh `dashboard_monitoring.py`.

### `cctv_test.py`

Script opsional untuk melatih ulang model YOLO dari dataset `plat_dataset`. Script ini bukan bagian dari proses monitoring harian.

```python
model.train(
    data="plat_dataset/data.yaml",
    epochs=50,
    imgsz=640
)
```

### File Database dan Migrasi

- `parkir_db.sql`: struktur dan data awal database.
- `parkir_db_github_safe.sql`: dump aman berisi struktur lengkap dan data dummy untuk GitHub. File ini membuat database `parkir_db_demo` agar tidak menimpa database lokal.
- `migrasi_import_lokasi_layanan.sql`: menyiapkan kolom klasifikasi area pada lokasi layanan.
- `migrasi_relasi_lokasi_wilayah.sql`: membuat tabel penghubung `lokasi_wilayah`.
- `migrasi_hapus_id_wilayah_lokasi.sql`: menghapus kolom lama `lokasi_layanan.id_wilayah`.
- `import_lokasi_layanan.sql`: mengisi data lokasi dan relasinya berdasarkan sumber Excel.

### Model dan Dataset

- `yolov8n.pt`: model dasar YOLOv8 untuk pelatihan.
- `runs/detect/train/weights/best.pt`: model hasil training yang digunakan aplikasi sesuai `YOLO_MODEL_PATH`.
- `plat_dataset/train`: gambar dan label untuk training.
- `plat_dataset/valid`: data validasi model.
- `plat_dataset/test`: data pengujian model.
- `plat_dataset/data.yaml`: konfigurasi lokasi dataset dan class YOLO.

### Output

- `laporan/`: tempat penyimpanan file Excel hasil export.
- Nama file laporan mengikuti pola `laporan_monitoring_YYYYMMDD_HHMMSS.xlsx`.

## 5. Instalasi dan Menjalankan Aplikasi

### Persyaratan

- Windows.
- Python 3.
- XAMPP dengan MySQL aktif.
- Tesseract OCR.
- Kamera laptop atau webcam.
- Model YOLO pada path yang ditentukan di `app/config.py`.

### Instalasi Paket

Jika paket belum tersedia, jalankan:

```powershell
py -m pip install opencv-python pillow pytesseract ultralytics mysql-connector-python pandas openpyxl
```

### Setup Database

1. Buka XAMPP Control Panel.
2. Jalankan service MySQL.
3. Buka `http://localhost/phpmyadmin`.
4. Buat database bernama `parkir_db`.
5. Pilih database tersebut.
6. Import `parkir_db.sql`.

Untuk repository GitHub atau demonstrasi publik, gunakan `parkir_db_github_safe.sql`. File tersebut otomatis membuat database `parkir_db_demo` dengan data dummy dan tidak berisi nomor plat atau nama driver asli. Jika ingin menjalankan aplikasi menggunakan database demo, ubah nilai `database` pada `app/config.py` menjadi `parkir_db_demo` hanya pada komputer lokal.

Untuk database lama yang belum memiliki klasifikasi lokasi terbaru, jalankan migrasi berikut secara berurutan setelah memilih database `parkir_db`:

```text
migrasi_import_lokasi_layanan.sql
migrasi_relasi_lokasi_wilayah.sql
import_lokasi_layanan.sql
migrasi_hapus_id_wilayah_lokasi.sql
```

Jika database sudah dibuat dari `parkir_db.sql` versi terbaru, migrasi tidak perlu dijalankan ulang.

`parkir_db.sql` sengaja dimasukkan ke `.gitignore` karena dapat berisi data operasional. Jika file tersebut pernah terlanjur dilacak Git, keluarkan dari index dengan:

```powershell
git rm --cached parkir_db.sql
```

Perintah tersebut tidak menghapus file lokal, tetapi mencegahnya ikut dikirim ke repository berikutnya.

### Akun Demo

| Role | Username | Password |
|---|---|---|
| Operator | `operator` | `operator` |
| Admin | `admin` | `admin` |
| Admin Utama | `utama` | `utama` |

### Hak Akses

- **Operator**: Monitoring dan Riwayat & Laporan.
- **Admin**: Dashboard, seluruh data master, Riwayat & Laporan, dan Statistik.
- **Admin Utama**: Dashboard, Riwayat & Laporan, dan Statistik. Tidak dapat mengubah data master atau melakukan input monitoring.

## 6. Alur Kerja Sistem

```text
Login pengguna
    ↓
Pemeriksaan role dan hak akses
    ↓
Halaman sesuai role
    ↓
Kamera mengambil frame
    ↓
YOLO mendeteksi area plat
    ↓
Tesseract membaca teks plat
    ↓
Sistem mencari kendaraan dan driver
    ↓
Pengguna memilih kecamatan
    ↓
Sistem menampilkan desa pada kecamatan tersebut
    ↓
Pengguna memilih desa
    ↓
Sistem menampilkan lokasi layanan yang sesuai
    ↓
Sistem menghitung jarak dan estimasi BBM
    ↓
Operator menekan Submit Data Monitoring
    ↓
Data masuk ke log_monitoring
    ↓
Riwayat dan laporan dapat difilter serta diekspor
```

## 7. Relasi Database

Database menggunakan model relasional MySQL/MariaDB. Tabel utama yang digunakan adalah:

### `jenis_kendaraan`

Menyimpan master jenis kendaraan.

- Primary key: `id_jenis`
- Kolom penting: `nama_jenis`

### `kendaraan_dinas`

Menyimpan kendaraan yang dapat dimonitor.

- Primary key: `id_kendaraan`
- Unique key: `no_plat`
- Foreign key: `id_jenis` → `jenis_kendaraan.id_jenis`
- Kolom penting: `no_plat`, `konsumsi_km_per_liter`

### `driver`

Menyimpan driver dan kendaraan yang digunakan.

- Primary key: `id_driver`
- Foreign key: `id_kendaraan` → `kendaraan_dinas.id_kendaraan`
- Kolom penting: `nama_driver`

### `wilayah`

Menyimpan desa/kelurahan dan kecamatan.

- Primary key: `id_wilayah`
- Kolom penting: `desa_kelurahan`, `kecamatan`

### `lokasi_layanan`

Menyimpan lokasi tujuan layanan.

- Primary key: `id_lokasi`
- Kolom penting: `nama_lokasi`, `jarak_km`, `kecamatan`
- Tidak menggunakan kolom `id_wilayah`.

### `lokasi_wilayah`

Tabel penghubung antara lokasi layanan dan wilayah.

- Primary key gabungan: `id_lokasi`, `id_wilayah`
- Foreign key: `id_lokasi` → `lokasi_layanan.id_lokasi`
- Foreign key: `id_wilayah` → `wilayah.id_wilayah`
- Memungkinkan satu lokasi terhubung ke beberapa desa dan satu desa memiliki beberapa lokasi.

### `log_monitoring`

Menyimpan transaksi perjalanan kendaraan.

- Primary key: `id`
- Foreign key: `id_wilayah` → `wilayah.id_wilayah`
- Foreign key: `id_lokasi` → `lokasi_layanan.id_lokasi`
- Foreign key: `id_driver` → `driver.id_driver`
- Kolom penting: `no_plat`, `waktu`, `lokasi`, `jarak_tempuh`, `estimasi_bbm`, `desa_kelurahan`, dan `kecamatan`

### Diagram Relasi

```text
jenis_kendaraan 1 ──────< kendaraan_dinas 1 ──────< driver
                                  │                    │
                                  │                    └──────< log_monitoring
                                  │
                                  └──────< log_monitoring melalui no_plat

wilayah 1 ──────< lokasi_wilayah >────── 1 lokasi_layanan
   │                                      │
   └──────────────< log_monitoring >──────┘
```

Relasi `lokasi_wilayah` digunakan agar filter lokasi tidak bergantung pada satu kolom kecamatan saja. Saat operator memilih kecamatan dan desa, aplikasi mencari lokasi melalui relasi wilayah tersebut.

## 8. Perhitungan Estimasi BBM

Rumus yang digunakan:

```text
estimasi_bbm = jarak_tempuh / konsumsi_km_per_liter
```

Contoh kendaraan dengan jarak `10 km` dan konsumsi `5 km/liter`:

```text
10 / 5 = 2 liter
```

## 9. Metode Pengembangan Agile

Pengembangan sistem menggunakan Agile dengan pendekatan Prototype dan Incremental. Setiap fitur dikembangkan dalam sprint singkat, diuji, dievaluasi, dan diperbaiki berdasarkan masukan pengguna.

### Siklus Agile

```text
Analisis kebutuhan
    ↓
Product backlog
    ↓
Sprint planning
    ↓
Desain dan implementasi
    ↓
Pengujian
    ↓
Sprint review dengan pengguna
    ↓
Retrospective
    └──── backlog diperbarui untuk sprint berikutnya
```

### Contoh Pembagian Sprint

| Sprint | Pekerjaan |
|---|---|
| 1 | Analisis kebutuhan, ERD, dan database |
| 2 | Login dan hak akses |
| 3 | CRUD data master |
| 4 | Kamera, YOLO, dan OCR |
| 5 | Klasifikasi wilayah dan lokasi layanan |
| 6 | Input monitoring, jarak, BBM, dan riwayat |
| 7 | Filter laporan dan export Excel |
| 8 | Evaluasi pengguna, perbaikan UI, dan dokumentasi |

Metode ini cocok karena kebutuhan tampilan, filter, hak akses, dan laporan dapat berubah setelah diuji langsung oleh operator dan admin.

## 10. Pengujian Sistem

### Black Box Testing

Black Box Testing digunakan sebagai metode pengujian fungsional utama. Penguji memeriksa input dan output melalui antarmuka tanpa melihat kode program.

| ID | Fitur | Input/Kondisi | Hasil yang diharapkan |
|---|---|---|---|
| BB-01 | Login | Username dan password benar | Masuk sesuai role |
| BB-02 | Login | Password salah | Pesan login gagal tampil |
| BB-03 | Hak akses | Operator membuka data master | Akses ditolak atau menu tidak tampil |
| BB-04 | Kamera | Kamera tersedia | Frame kamera tampil |
| BB-05 | Deteksi plat | Plat terlihat pada frame | Area plat terdeteksi dan OCR dijalankan |
| BB-06 | Pencarian plat | Plat terdaftar | Driver dan jenis kendaraan tampil |
| BB-07 | Wilayah | Kecamatan dipilih | Desa pada kecamatan tersebut tampil |
| BB-08 | Lokasi | Desa dipilih | Lokasi sesuai wilayah tampil |
| BB-09 | Input | Data tidak lengkap | Sistem menolak penyimpanan |
| BB-10 | Input | Data lengkap | Data tersimpan ke `log_monitoring` |
| BB-11 | BBM | Jarak dan konsumsi tersedia | Estimasi BBM sesuai rumus |
| BB-12 | Riwayat | Filter plat dipilih | Hanya plat tersebut tampil |
| BB-13 | Riwayat | Filter jenis dan tanggal | Data sesuai filter tampil |
| BB-14 | Export | Export setelah filter | Excel berisi data sesuai filter |
| BB-15 | CRUD | Tambah, ubah, hapus data | Perubahan tersimpan sesuai operasi |
| BB-16 | Logout | Tombol logout ditekan | Kembali ke halaman login |

Status pengujian dicatat dengan format:

| ID | Hasil aktual | Hasil yang diharapkan | Status |
|---|---|---|---|
| BB-01 | Diisi saat pengujian | Masuk sebagai Operator | Berhasil/Gagal |

### User Acceptance Testing

UAT dilakukan setelah Black Box Testing dengan melibatkan pengguna sebenarnya.

- Operator menguji monitoring, input, filter wilayah, riwayat, dan laporan.
- Admin menguji CRUD, dashboard, statistik, filter, dan export.
- Admin Utama menguji pemantauan dashboard, riwayat, statistik, dan laporan.

Sistem dinyatakan diterima apabila fungsi utama berjalan, data tersimpan benar, hak akses sesuai, dan pengguna dapat menjalankan proses tanpa bantuan teknis.

### Pengujian Tambahan

- **Integration Testing**: menguji koneksi aplikasi dengan MySQL, kamera, YOLO, dan Tesseract.
- **Accuracy Testing**: mengukur ketepatan deteksi area plat dan pembacaan OCR.
- **Usability Testing**: menilai kemudahan navigasi, warna, form, filter, dan tabel.
- **Performance Testing**: mengamati waktu membuka kamera, pencarian database, filter, dan export.

## 11. Troubleshooting

### `Unknown database 'parkir_db'`

Database belum dibuat atau belum di-import. Buat database `parkir_db` di phpMyAdmin kemudian import `parkir_db.sql`.

### `No database selected`

File SQL di-import tanpa memilih database. Klik database `parkir_db` terlebih dahulu, lalu lakukan import.

### Kamera tidak muncul

- Pastikan kamera tidak digunakan aplikasi lain.
- Aktifkan izin kamera pada Windows.
- Coba webcam lain.
- Pastikan index kamera yang digunakan tersedia.

### Tesseract tidak ditemukan

Periksa `TESSERACT_CMD` pada `app/config.py` dan sesuaikan dengan lokasi `tesseract.exe`.

### Model YOLO tidak ditemukan

Periksa `YOLO_MODEL_PATH` pada `app/config.py`. Secara default aplikasi menggunakan:

```text
runs/detect/train/weights/best.pt
```

### Lokasi layanan tidak muncul

Pastikan:

- Kecamatan dan desa tersedia di tabel `wilayah`.
- Lokasi tersedia di `lokasi_layanan`.
- Relasi lokasi dan wilayah tersedia di `lokasi_wilayah`.
- Nama area dan kecamatan sudah sesuai.

## 12. Pengelolaan File yang Dihapus

File berikut tidak digunakan oleh aplikasi utama dan telah dihapus dari proyek:

- `anpr_video.py`: script percobaan membaca plat dari file video yang path videonya tidak tersedia.
- `simulasi_monitoring_7_hari.py`: script data dummy yang tidak digunakan oleh proses aplikasi utama.
- `migrasi_lokasi_wilayah.sql`: migrasi lama yang sudah digantikan oleh `migrasi_relasi_lokasi_wilayah.sql`.
- Installer Python dan XAMPP: hanya installer lingkungan kerja, bukan bagian runtime aplikasi.

Model dasar `yolov8n.pt`, dataset `plat_dataset`, script `cctv_test.py`, dan hasil training `runs/` tetap dipertahankan karena dibutuhkan apabila model ingin dilatih atau dievaluasi ulang.

## 13. Ringkasan

Aplikasi ini menggabungkan deteksi plat, database kendaraan, klasifikasi wilayah, pencatatan perjalanan, perhitungan BBM, pengelolaan role, riwayat, statistik, dan laporan Excel dalam satu sistem desktop. Struktur database memakai relasi normal dan tabel penghubung `lokasi_wilayah` agar pemfilteran lokasi layanan berdasarkan wilayah dapat dilakukan secara fleksibel.
