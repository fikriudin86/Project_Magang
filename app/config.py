APP_TITLE = "Monitoring Dinas"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "parkir_db",
}

TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
YOLO_MODEL_PATH = "runs/detect/train/weights/best.pt"

USERS = {
    "operator": {
        "password": "operator",
        "role": "operator",
        "name": "Operator",
    },
    "admin": {
        "password": "admin",
        "role": "admin",
        "name": "Admin",
    },
    "utama": {
        "password": "utama",
        "role": "admin_utama",
        "name": "Admin Utama",
    },
}

ROLE_LABELS = {
    "operator": "Operator",
    "admin": "Admin",
    "admin_utama": "Admin Utama",
}

ROLE_MENUS = {
    "operator": [
        "Monitoring",
        "Riwayat & Laporan",
    ],
    "admin": [
        "Dashboard",
        "Kendaraan",
        "Driver",
        "Jenis Kendaraan",
        "Wilayah",
        "Lokasi Layanan",
        "Riwayat & Laporan",
        "Statistik",
    ],
    "admin_utama": [
        "Dashboard",
        "Riwayat & Laporan",
        "Statistik",
    ],
}

ROLE_HOME = {
    "operator": "Monitoring",
    "admin": "Dashboard",
    "admin_utama": "Dashboard",
}

COLORS = {
    "bg": "#f4f9ff",
    "sidebar": "#0b3558",
    "sidebar_active": "#1677d2",
    "primary": "#147bd1",
    "primary_dark": "#0c5fa8",
    "success": "#21b573",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#7c3aed",
    "card": "#ffffff",
    "soft": "#eaf5ff",
    "line": "#d6e8f8",
    "text": "#073763",
    "muted": "#6b86a3",
    "input": "#f8fbff",
}
