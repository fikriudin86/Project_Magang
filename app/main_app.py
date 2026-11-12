import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import cv2
import mysql.connector
import pandas as pd
import pytesseract
from PIL import Image, ImageTk
from ultralytics import YOLO

from app.config import APP_TITLE, COLORS, DB_CONFIG, ROLE_HOME, ROLE_LABELS, ROLE_MENUS, TESSERACT_CMD, USERS, YOLO_MODEL_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class ModernMonitoringApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistem Monitoring Kendaraan Dinas")
        self.root.geometry("1360x780")
        self.root.minsize(1180, 720)
        self.root.configure(bg=COLORS["bg"])

        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        self.model = YOLO(YOLO_MODEL_PATH)
        self.cap = self.open_camera()
        self.frame_count = 0
        self.current_page = None
        self.current_role = None
        self.current_user = None
        self.nav_buttons = {}

        self.plate_var = tk.StringVar()
        self.driver_var = tk.StringVar()
        self.vehicle_type_var = tk.StringVar()
        self.kecamatan_var = tk.StringVar()
        self.wilayah_var = tk.StringVar()
        self.lokasi_var = tk.StringVar()
        self.location_distance_var = tk.StringVar(value="0")
        self.fuel_estimate_var = tk.StringVar(value="0")
        self.monitoring_widgets = {}

        self.configure_styles()
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["card"],
            fieldbackground=COLORS["card"],
            foreground=COLORS["text"],
            rowheight=34,
            bordercolor=COLORS["line"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["soft"],
            foreground=COLORS["text"],
            relief="flat",
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#ffffff")])
        style.configure("TCombobox", padding=6, fieldbackground=COLORS["input"], background=COLORS["input"])

    def open_camera(self):
        for camera_index in (0, 1, 2):
            camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if camera.isOpened():
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                camera.set(cv2.CAP_PROP_FPS, 15)
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                return camera
        return cv2.VideoCapture(0)

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.current_role = None
        self.current_user = None
        self.current_page = None
        self.clear_root()
        wrapper = tk.Frame(self.root, bg=COLORS["bg"])
        wrapper.pack(fill="both", expand=True, padx=80, pady=70)

        left = tk.Frame(wrapper, bg=COLORS["sidebar"], width=430)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        icon = tk.Label(left, text="🚚", font=("Segoe UI Emoji", 58), bg=COLORS["sidebar"], fg="white")
        icon.pack(pady=(120, 20))
        tk.Label(
            left,
            text="Sistem Monitoring\nKendaraan Dinas",
            font=("Segoe UI", 23, "bold"),
            bg=COLORS["sidebar"],
            fg="white",
            justify="center",
        ).pack()
        tk.Label(
            left,
            text="Pantau kendaraan, hitung jarak,\ndan optimalkan penggunaan BBM.",
            font=("Segoe UI", 11),
            bg=COLORS["sidebar"],
            fg="#cfe8ff",
            justify="center",
        ).pack(pady=28)

        right = tk.Frame(wrapper, bg=COLORS["card"], padx=48, pady=50)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Login Pengguna", font=("Segoe UI", 20, "bold"), bg=COLORS["card"], fg=COLORS["text"]).pack(
            anchor="w", pady=(100, 24)
        )

        username = self.create_entry(right, "Username")
        password = self.create_entry(right, "Password", show="*")
        remember = tk.BooleanVar()
        tk.Checkbutton(
            right,
            text="Ingat saya",
            variable=remember,
            bg=COLORS["card"],
            fg=COLORS["muted"],
            activebackground=COLORS["card"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(0, 18))

        def login():
            user_key = username.get().strip().lower()
            user_data = USERS.get(user_key)
            if user_data and password.get().strip() == user_data["password"]:
                self.current_user = user_key
                self.current_role = user_data["role"]
                self.show_main_app()
            else:
                messagebox.showerror("Login gagal", "Username atau password tidak sesuai.")

        self.button(right, "Login", login, COLORS["primary"]).pack(fill="x", ipady=7)
        tk.Label(
            right,
            text="Akun: operator/operator | admin/admin | utama/utama",
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=14)

    def show_main_app(self):
        self.clear_root()
        self.nav_buttons = {}
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="🚚  Monitoring Dinas",
            bg=COLORS["sidebar"],
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack(fill="x", padx=16, pady=(22, 24))

        role_label = ROLE_LABELS.get(self.current_role, "Pengguna")
        tk.Label(
            self.sidebar,
            text=f"Akses: {role_label}",
            bg=COLORS["sidebar"],
            fg="#a7d8ff",
            font=("Segoe UI", 9, "bold"),
        ).pack(fill="x", padx=18, pady=(0, 12))

        all_nav_items = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Monitoring", "📷", self.show_monitoring),
            ("Kendaraan", "🚚", self.show_kendaraan),
            ("Driver", "👤", self.show_driver),
            ("Jenis Kendaraan", "🏷", self.show_jenis),
            ("Wilayah", "📍", self.show_wilayah),
            ("Lokasi Layanan", "🗺", self.show_lokasi),
            ("Riwayat & Laporan", "🧾", self.show_laporan),
            ("Statistik", "📈", self.show_statistik),
        ]
        allowed_menus = ROLE_MENUS.get(self.current_role, [])
        nav_items = [item for item in all_nav_items if item[0] in allowed_menus]

        for label, icon, command in nav_items:
            button = tk.Button(
                self.sidebar,
                text=f"{icon}  {label}",
                command=command,
                anchor="w",
                bg=COLORS["sidebar"],
                fg="#d8ecff",
                activebackground=COLORS["sidebar_active"],
                activeforeground="white",
                relief="flat",
                padx=18,
                pady=10,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            button.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[label] = button

        tk.Button(
            self.sidebar,
            text="↩  Logout",
            command=self.show_login,
            anchor="w",
            bg=COLORS["sidebar"],
            fg="#d8ecff",
            activebackground=COLORS["danger"],
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="bottom", fill="x", padx=10, pady=18)

        self.content = tk.Frame(self.root, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        self.open_role_home()

    def open_role_home(self):
        home = ROLE_HOME.get(self.current_role, "Dashboard")
        home_pages = {
            "Dashboard": self.show_dashboard,
            "Monitoring": self.show_monitoring,
            "Kendaraan": self.show_kendaraan,
            "Driver": self.show_driver,
            "Jenis Kendaraan": self.show_jenis,
            "Wilayah": self.show_wilayah,
            "Lokasi Layanan": self.show_lokasi,
            "Riwayat & Laporan": self.show_laporan,
            "Statistik": self.show_statistik,
        }
        home_pages.get(home, self.show_dashboard)()

    def set_active_nav(self, label):
        self.current_page = label
        for name, button in self.nav_buttons.items():
            button.configure(bg=COLORS["sidebar_active"] if name == label else COLORS["sidebar"])

    def has_access(self, label):
        return label in ROLE_MENUS.get(self.current_role, [])

    def clear_content(self, title, subtitle=None):
        if not self.has_access(title):
            self.show_access_denied(title)
            return False
        for widget in self.content.winfo_children():
            widget.destroy()
        self.set_active_nav(title)

        top = tk.Frame(self.content, bg=COLORS["bg"])
        top.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(top, text=title, bg=COLORS["bg"], fg=COLORS["text"], font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(top, text=datetime.now().strftime("%d %B %Y"), bg=COLORS["bg"], fg=COLORS["muted"]).pack(side="right")
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=COLORS["bg"], fg=COLORS["muted"], font=("Segoe UI", 10)).pack(
                anchor="w", padx=24
            )
        return True

    def show_access_denied(self, title):
        for widget in self.content.winfo_children():
            widget.destroy()
        frame = self.card(self.content, "Akses Ditolak", padx=30, pady=26)
        frame.pack(fill="x", padx=24, pady=24)
        role_label = ROLE_LABELS.get(self.current_role, "Pengguna")
        tk.Label(
            frame,
            text=f"{role_label} tidak memiliki akses ke halaman {title}.",
            bg=COLORS["card"],
            fg=COLORS["danger"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")

    def card(self, parent, title=None, padx=16, pady=14):
        frame = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["line"], highlightthickness=1, padx=padx, pady=pady)
        if title:
            tk.Label(frame, text=title, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 12, "bold")).pack(
                anchor="w", pady=(0, 10)
            )
        return frame

    def button(self, parent, text, command, color=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )

    def create_entry(self, parent, placeholder="", show=None):
        entry = tk.Entry(parent, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, font=("Segoe UI", 11), show=show)
        entry.pack(fill="x", ipady=8, pady=(0, 14))
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event: entry.delete(0, tk.END) if entry.get() == placeholder else None)
        return entry

    def fetchall(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def fetchone(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def show_dashboard(self):
        if not self.clear_content("Dashboard", "Ringkasan data kendaraan, driver, monitoring, dan penggunaan BBM."):
            return
        stats = self.get_summary_stats()

        stat_frame = tk.Frame(self.content, bg=COLORS["bg"])
        stat_frame.pack(fill="x", padx=24, pady=12)
        cards = [
            ("Total Kendaraan", stats["vehicles"], "🚚", COLORS["primary"]),
            ("Total Driver", stats["drivers"], "👤", COLORS["success"]),
            ("Total Monitoring", stats["logs"], "🧾", COLORS["warning"]),
            ("Total Estimasi BBM", f"{stats['fuel']:.1f} L", "💧", COLORS["purple"]),
        ]
        for index, (title, value, icon, color) in enumerate(cards):
            frame = tk.Frame(stat_frame, bg=color, padx=18, pady=16)
            frame.grid(row=0, column=index, sticky="nsew", padx=(0, 12))
            stat_frame.grid_columnconfigure(index, weight=1)
            tk.Label(frame, text=icon, bg=color, fg="white", font=("Segoe UI Emoji", 22)).pack(anchor="w")
            tk.Label(frame, text=str(value), bg=color, fg="white", font=("Segoe UI", 22, "bold")).pack(anchor="w")
            tk.Label(frame, text=title, bg=color, fg="#eef8ff", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        middle = tk.Frame(self.content, bg=COLORS["bg"])
        middle.pack(fill="x", padx=24, pady=(4, 12))
        chart = self.card(middle, "Monitoring per Bulan")
        chart.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.draw_monthly_chart(chart)

        donut = self.card(middle, "Penggunaan BBM per Jenis Kendaraan")
        donut.pack(side="left", fill="both", expand=True)
        self.draw_type_summary(donut)

        table_card = self.card(self.content, "Monitoring Terbaru")
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        self.create_table(
            table_card,
            ("Plat", "Driver", "Jenis", "Lokasi", "Jarak", "BBM", "Waktu"),
            self.get_log_rows(limit=8),
        )

    def show_monitoring(self):
        if not self.clear_content("Monitoring", "Deteksi plat kendaraan, lengkapi data, lalu simpan ke riwayat."):
            return
        body = tk.Frame(self.content, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=12)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        left = self.card(body, "Deteksi Plat Kendaraan")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.video_label = tk.Label(left, bg="#0b1220", width=640, height=360)
        self.video_label.pack(fill="x")

        result = tk.Frame(left, bg=COLORS["card"])
        result.pack(fill="x", pady=(14, 0))
        self.detected_preview = tk.Label(result, text="Hasil Deteksi: -", bg=COLORS["soft"], fg=COLORS["text"], font=("Segoe UI", 11, "bold"), padx=12, pady=12)
        self.detected_preview.pack(fill="x")

        right = self.card(body, "Data Monitoring")
        right.grid(row=0, column=1, sticky="nsew")
        self.build_monitoring_form(right)
        self.update_frame()

    def build_monitoring_form(self, parent):
        form_container = tk.Frame(parent, bg=COLORS["card"])
        form_container.pack(fill="both", expand=True)

        form_canvas = tk.Canvas(form_container, bg=COLORS["card"], highlightthickness=0)
        form_scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=form_canvas.yview)
        form_canvas.configure(yscrollcommand=form_scrollbar.set)
        form_canvas.pack(side="left", fill="both", expand=True)
        form_scrollbar.pack(side="right", fill="y")

        form_body = tk.Frame(form_canvas, bg=COLORS["card"])
        form_window = form_canvas.create_window((0, 0), window=form_body, anchor="nw")
        form_body.bind(
            "<Configure>",
            lambda event: form_canvas.configure(scrollregion=form_canvas.bbox("all")),
        )
        form_canvas.bind(
            "<Configure>",
            lambda event: form_canvas.itemconfigure(form_window, width=event.width),
        )

        parent = form_body
        self.monitoring_widgets = {}
        self.plate_var.set("")
        self.driver_var.set("")
        self.vehicle_type_var.set("")
        self.kecamatan_var.set("")
        self.wilayah_var.set("")
        self.lokasi_var.set("")
        self.location_distance_var.set("0")
        self.fuel_estimate_var.set("0")

        self.form_entry(parent, "Plat Nomor", self.plate_var)
        self.button(parent, "Cari Data Plat", lambda: self.load_vehicle_by_plate(self.plate_var.get())).pack(fill="x", ipady=6, pady=(0, 10))

        driver_combo = self.form_combo(parent, "Driver", self.driver_var, self.get_driver_options())
        type_entry = self.form_entry(parent, "Jenis Kendaraan", self.vehicle_type_var, readonly=True)
        kecamatan_combo = self.form_combo(parent, "Daerah / Kecamatan", self.kecamatan_var, self.get_kecamatan_options())
        wilayah_combo = self.form_combo(parent, "Wilayah / Desa / Kelurahan", self.wilayah_var, [])
        wilayah_combo.configure(state="disabled")
        lokasi_combo = self.form_combo(parent, "Lokasi Layanan", self.lokasi_var, [])
        lokasi_combo.configure(state="disabled")
        jarak_entry = self.form_entry(parent, "Jarak (KM)", self.location_distance_var, readonly=True)
        bbm_entry = self.form_entry(parent, "Estimasi BBM (L)", self.fuel_estimate_var, readonly=True)

        self.monitoring_widgets.update(
            {
                "driver": driver_combo,
                "jenis": type_entry,
                "kecamatan": kecamatan_combo,
                "wilayah": wilayah_combo,
                "lokasi": lokasi_combo,
                "jarak": jarak_entry,
                "bbm": bbm_entry,
            }
        )
        kecamatan_combo.bind("<<ComboboxSelected>>", lambda event: self.update_wilayah_options())
        wilayah_combo.bind("<<ComboboxSelected>>", lambda event: self.update_lokasi_options())
        lokasi_combo.bind("<<ComboboxSelected>>", lambda event: self.update_distance_and_fuel())
        self.button(parent, "Submit Data Monitoring", self.save_monitoring, COLORS["primary"]).pack(
            fill="x", ipady=10, pady=(14, 0)
        )

    def update_wilayah_options(self):
        """Isi dropdown desa/kelurahan sesuai kecamatan yang dipilih."""
        wilayah_combo = self.monitoring_widgets.get("wilayah")
        if not wilayah_combo:
            return

        self.wilayah_var.set("")
        kecamatan = self.kecamatan_var.get().strip()
        if kecamatan:
            wilayah_combo.configure(values=self.get_wilayah_options(kecamatan), state="readonly")
        else:
            wilayah_combo.configure(values=[], state="disabled")
        self.update_lokasi_options()

    def update_lokasi_options(self):
        """Isi dropdown lokasi layanan sesuai wilayah yang dipilih."""
        lokasi_combo = self.monitoring_widgets.get("lokasi")
        if not lokasi_combo:
            return

        self.lokasi_var.set("")
        self.location_distance_var.set("0")
        self.fuel_estimate_var.set("0")
        id_wilayah = self.extract_id(self.wilayah_var.get())
        kecamatan = self.kecamatan_var.get().strip()
        if id_wilayah or kecamatan:
            lokasi_combo.configure(values=self.get_lokasi_options(kecamatan, id_wilayah), state="readonly")
        else:
            lokasi_combo.configure(values=[], state="disabled")

    def form_entry(self, parent, label, variable, readonly=False):
        tk.Label(parent, text=label, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 4))
        entry = tk.Entry(parent, textvariable=variable, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, font=("Segoe UI", 10))
        if readonly:
            entry.configure(state="readonly", readonlybackground=COLORS["input"])
        entry.pack(fill="x", ipady=7)
        return entry

    def form_combo(self, parent, label, variable, values):
        tk.Label(parent, text=label, bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 4))
        combo = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", font=("Segoe UI", 10))
        combo.pack(fill="x", ipady=4)
        return combo

    def update_frame(self):
        if self.current_page != "Monitoring" or not hasattr(self, "video_label"):
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 360))
            if self.frame_count % 20 == 0:
                self.detect_plate(frame)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.video_label.configure(image=image)
            self.video_label.image = image
            self.frame_count += 1

        self.root.after(30, self.update_frame)

    def detect_plate(self, frame):
        try:
            results = self.model(frame, imgsz=320, verbose=False)
            for result in results:
                for box in result.boxes.xyxy.cpu().numpy():
                    x1, y1, x2, y2 = map(int, box)
                    crop = frame[y1:y2, x1:x2]
                    if crop.size == 0:
                        continue
                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    text = pytesseract.image_to_string(
                        thresh,
                        config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    )
                    clean_text = re.sub(r"[^A-Z0-9]", "", text)
                    if len(clean_text) >= 4 and not self.plate_var.get():
                        self.plate_var.set(clean_text)
                        self.detected_preview.configure(text=f"Hasil Deteksi: {clean_text}")
                        self.load_vehicle_by_plate(clean_text)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, clean_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        except Exception as error:
            print("Error detection:", error)

    def load_vehicle_by_plate(self, plate):
        if not plate:
            messagebox.showwarning("Info", "Masukkan plat nomor terlebih dahulu.")
            return
        row = self.fetchone(
            """
            SELECT d.id_driver, d.nama_driver, j.nama_jenis, k.konsumsi_km_per_liter
            FROM kendaraan_dinas k
            LEFT JOIN driver d ON k.id_kendaraan = d.id_kendaraan
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            WHERE k.no_plat = %s
            """,
            (plate,),
        )
        if not row:
            self.vehicle_type_var.set("Tidak ditemukan")
            messagebox.showwarning("Info", "Plat tidak ditemukan di database.")
            return

        id_driver, nama_driver, nama_jenis, konsumsi = row
        self.driver_var.set(f"{id_driver} - {nama_driver}" if id_driver else "")
        self.vehicle_type_var.set(nama_jenis or "-")
        self.monitoring_widgets["konsumsi"] = float(konsumsi or 1)
        self.update_distance_and_fuel()

    def update_distance_and_fuel(self):
        lokasi = self.monitoring_widgets.get("lokasi")
        if not lokasi:
            return
        id_lokasi = self.extract_id(lokasi.get())
        row = self.fetchone("SELECT jarak_km FROM lokasi_layanan WHERE id_lokasi=%s", (id_lokasi,)) if id_lokasi else None
        jarak = float(row[0]) if row else 0
        konsumsi = float(self.monitoring_widgets.get("konsumsi", 1) or 1)
        self.location_distance_var.set(str(jarak))
        self.fuel_estimate_var.set(f"{jarak / konsumsi:.2f}" if konsumsi else "0")

    def save_monitoring(self):
        try:
            plat = self.plate_var.get().strip().upper()
            id_driver = self.extract_id(self.driver_var.get())
            id_wilayah = self.extract_id(self.monitoring_widgets["wilayah"].get())
            id_lokasi = self.extract_id(self.monitoring_widgets["lokasi"].get())
            kecamatan = self.kecamatan_var.get().strip()
            if not all([plat, id_driver, kecamatan, id_wilayah, id_lokasi]):
                messagebox.showwarning("Info", "Lengkapi plat, driver, daerah/kecamatan, wilayah, dan lokasi layanan.")
                return

            lokasi, jarak = self.fetchone("SELECT nama_lokasi, jarak_km FROM lokasi_layanan WHERE id_lokasi=%s", (id_lokasi,))
            wilayah_row = self.fetchone(
                "SELECT desa_kelurahan, kecamatan FROM wilayah WHERE id_wilayah=%s AND LOWER(TRIM(kecamatan))=LOWER(TRIM(%s))",
                (id_wilayah, kecamatan),
            )
            if not wilayah_row:
                messagebox.showwarning("Info", "Wilayah tidak sesuai dengan daerah/kecamatan yang dipilih.")
                return
            desa, kecamatan = wilayah_row
            konsumsi = self.fetchone("SELECT konsumsi_km_per_liter FROM kendaraan_dinas WHERE no_plat=%s", (plat,))
            estimasi = float(jarak) / float(konsumsi[0] or 1)

            self.execute(
                """
                INSERT INTO log_monitoring
                (no_plat,waktu,lokasi,jarak_tempuh,estimasi_bbm,desa_kelurahan,kecamatan,id_wilayah,id_lokasi,id_driver)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (plat, datetime.now(), lokasi, jarak, estimasi, desa, kecamatan, id_wilayah, id_lokasi, id_driver),
            )
            self.fuel_estimate_var.set(f"{estimasi:.2f}")
            messagebox.showinfo("Sukses", "Data monitoring berhasil disimpan.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def show_kendaraan(self):
        self.master_page(
            "Kendaraan",
            ("ID", "Plat Nomor", "Jenis Kendaraan", "Konsumsi", "Status"),
            """
            SELECT k.id_kendaraan, k.no_plat, COALESCE(j.nama_jenis, '-'), k.konsumsi_km_per_liter, 'Aktif'
            FROM kendaraan_dinas k
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            ORDER BY k.id_kendaraan
            """,
        )

    def show_driver(self):
        self.master_page(
            "Driver",
            ("ID", "Nama Driver", "Kendaraan", "Plat Nomor"),
            """
            SELECT d.id_driver, d.nama_driver, COALESCE(j.nama_jenis, '-'), COALESCE(k.no_plat, '-')
            FROM driver d
            LEFT JOIN kendaraan_dinas k ON d.id_kendaraan = k.id_kendaraan
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            ORDER BY d.id_driver
            """,
        )

    def show_jenis(self):
        self.master_page("Jenis Kendaraan", ("ID", "Jenis Kendaraan"), "SELECT id_jenis, nama_jenis FROM jenis_kendaraan ORDER BY id_jenis")

    def show_wilayah(self):
        self.master_page("Wilayah", ("ID", "Desa/Kelurahan", "Kecamatan"), "SELECT id_wilayah, desa_kelurahan, kecamatan FROM wilayah ORDER BY id_wilayah")

    def show_lokasi(self):
        self.master_page(
            "Lokasi Layanan",
            ("ID", "Nama Lokasi", "Jarak (KM)", "Klasifikasi Area", "Wilayah"),
            """
            SELECT l.id_lokasi, l.nama_lokasi, l.jarak_km,
                   COALESCE(l.kecamatan, 'Belum diklasifikasikan'),
                   COALESCE(GROUP_CONCAT(DISTINCT w.desa_kelurahan ORDER BY w.desa_kelurahan SEPARATOR ', '), '-')
            FROM lokasi_layanan l
            LEFT JOIN lokasi_wilayah lw ON l.id_lokasi = lw.id_lokasi
            LEFT JOIN wilayah w ON lw.id_wilayah = w.id_wilayah
            GROUP BY l.id_lokasi, l.nama_lokasi, l.jarak_km, l.kecamatan
            ORDER BY l.id_lokasi
            """,
        )

    def master_page(self, title, columns, query):
        if not self.clear_content(title, "Manajemen data master sesuai kebutuhan monitoring kendaraan."):
            return
        card = self.card(self.content)
        card.pack(fill="both", expand=True, padx=24, pady=12)
        top = tk.Frame(card, bg=COLORS["card"])
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text=f"Data {title}", bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 13, "bold")).pack(side="left")
        table_holder = tk.Frame(card, bg=COLORS["card"])
        table_holder.pack(fill="both", expand=True)
        tree = self.create_table(table_holder, columns, self.fetchall(query))

        self.button(top, f"+ Tambah {title}", lambda: self.open_master_dialog(title), COLORS["primary"]).pack(side="right", ipadx=10, ipady=4)
        self.button(top, "Hapus", lambda: self.delete_master_row(title, tree), COLORS["danger"]).pack(side="right", padx=8, ipadx=10, ipady=4)
        self.button(top, "Edit", lambda: self.edit_master_row(title, tree), COLORS["warning"]).pack(side="right", ipadx=10, ipady=4)

    def open_master_dialog(self, title, row_id=None):
        config = self.get_master_config(title)
        if not config:
            return

        current = config["load"](row_id) if row_id else {}
        dialog = tk.Toplevel(self.root)
        dialog.title(("Edit " if row_id else "Tambah ") + title)
        dialog.geometry("420x420")
        dialog.configure(bg=COLORS["card"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text=("Edit " if row_id else "Tambah ") + title,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=22, pady=(20, 12))

        fields = {}
        for field in config["fields"]:
            tk.Label(dialog, text=field["label"], bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 9, "bold")).pack(
                anchor="w", padx=22, pady=(8, 4)
            )
            variable = tk.StringVar(value=str(current.get(field["name"], "")))
            if field.get("options"):
                widget = ttk.Combobox(dialog, textvariable=variable, values=field["options"](), state="readonly")
                widget.pack(fill="x", padx=22, ipady=4)
            else:
                widget = tk.Entry(dialog, textvariable=variable, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1)
                widget.pack(fill="x", padx=22, ipady=7)
            fields[field["name"]] = variable

        def submit():
            try:
                values = {name: variable.get().strip() for name, variable in fields.items()}
                if row_id:
                    config["update"](row_id, values)
                else:
                    config["insert"](values)
                dialog.destroy()
                self.refresh_master_page(title)
            except Exception as error:
                messagebox.showerror("Error", str(error))

        self.button(dialog, "Simpan", submit, COLORS["primary"]).pack(fill="x", padx=22, pady=24, ipady=8)

    def edit_master_row(self, title, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Info", "Pilih data yang ingin diedit.")
            return
        row_id = tree.item(selected[0], "values")[0]
        self.open_master_dialog(title, row_id)

    def delete_master_row(self, title, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Info", "Pilih data yang ingin dihapus.")
            return
        row_id = tree.item(selected[0], "values")[0]
        if not messagebox.askyesno("Konfirmasi", f"Hapus data {title} ID {row_id}?"):
            return
        config = self.get_master_config(title)
        try:
            config["delete"](row_id)
            self.refresh_master_page(title)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def refresh_master_page(self, title):
        refreshers = {
            "Kendaraan": self.show_kendaraan,
            "Driver": self.show_driver,
            "Jenis Kendaraan": self.show_jenis,
            "Wilayah": self.show_wilayah,
            "Lokasi Layanan": self.show_lokasi,
        }
        refreshers[title]()

    def get_master_config(self, title):
        configs = {
            "Kendaraan": {
                "fields": [
                    {"name": "no_plat", "label": "Plat Nomor"},
                    {"name": "konsumsi", "label": "Konsumsi KM/L"},
                    {"name": "id_jenis", "label": "Jenis Kendaraan", "options": self.get_jenis_options},
                ],
                "load": lambda row_id: self.load_kendaraan(row_id),
                "insert": self.insert_kendaraan,
                "update": self.update_kendaraan,
                "delete": lambda row_id: self.execute("DELETE FROM kendaraan_dinas WHERE id_kendaraan=%s", (row_id,)),
            },
            "Driver": {
                "fields": [
                    {"name": "nama_driver", "label": "Nama Driver"},
                    {"name": "id_kendaraan", "label": "Kendaraan", "options": self.get_kendaraan_options},
                ],
                "load": lambda row_id: self.load_driver(row_id),
                "insert": self.insert_driver,
                "update": self.update_driver,
                "delete": lambda row_id: self.execute("DELETE FROM driver WHERE id_driver=%s", (row_id,)),
            },
            "Jenis Kendaraan": {
                "fields": [{"name": "nama_jenis", "label": "Jenis Kendaraan"}],
                "load": lambda row_id: {"nama_jenis": self.fetchone("SELECT nama_jenis FROM jenis_kendaraan WHERE id_jenis=%s", (row_id,))[0]},
                "insert": lambda values: self.execute("INSERT INTO jenis_kendaraan (nama_jenis) VALUES (%s)", (values["nama_jenis"],)),
                "update": lambda row_id, values: self.execute("UPDATE jenis_kendaraan SET nama_jenis=%s WHERE id_jenis=%s", (values["nama_jenis"], row_id)),
                "delete": lambda row_id: self.execute("DELETE FROM jenis_kendaraan WHERE id_jenis=%s", (row_id,)),
            },
            "Wilayah": {
                "fields": [
                    {"name": "desa_kelurahan", "label": "Desa/Kelurahan"},
                    {"name": "kecamatan", "label": "Kecamatan"},
                ],
                "load": lambda row_id: self.load_wilayah(row_id),
                "insert": lambda values: self.execute(
                    "INSERT INTO wilayah (desa_kelurahan, kecamatan) VALUES (%s,%s)",
                    (values["desa_kelurahan"], values["kecamatan"]),
                ),
                "update": lambda row_id, values: self.execute(
                    "UPDATE wilayah SET desa_kelurahan=%s, kecamatan=%s WHERE id_wilayah=%s",
                    (values["desa_kelurahan"], values["kecamatan"], row_id),
                ),
                "delete": lambda row_id: self.execute("DELETE FROM wilayah WHERE id_wilayah=%s", (row_id,)),
            },
            "Lokasi Layanan": {
                "fields": [
                    {"name": "nama_lokasi", "label": "Nama Lokasi"},
                    {"name": "jarak_km", "label": "Jarak KM"},
                    {"name": "kecamatan", "label": "Klasifikasi Area/Kecamatan", "options": self.get_kecamatan_options},
                ],
                "load": lambda row_id: self.load_lokasi(row_id),
                "insert": lambda values: self.execute(
                    "INSERT INTO lokasi_layanan (nama_lokasi, jarak_km, kecamatan) VALUES (%s,%s,%s)",
                    (values["nama_lokasi"], values["jarak_km"], values["kecamatan"]),
                ),
                "update": lambda row_id, values: self.execute(
                    "UPDATE lokasi_layanan SET nama_lokasi=%s, jarak_km=%s, kecamatan=%s WHERE id_lokasi=%s",
                    (values["nama_lokasi"], values["jarak_km"], values["kecamatan"], row_id),
                ),
                "delete": lambda row_id: self.execute("DELETE FROM lokasi_layanan WHERE id_lokasi=%s", (row_id,)),
            },
        }
        return configs.get(title)

    def show_riwayat(self):
        if not self.clear_content("Riwayat Monitoring", "Daftar riwayat perjalanan kendaraan yang sudah tersimpan."):
            return
        card = self.card(self.content, "Riwayat Perjalanan")
        card.pack(fill="both", expand=True, padx=24, pady=12)

        filters = tk.Frame(card, bg=COLORS["soft"], padx=12, pady=10)
        filters.pack(fill="x", pady=(0, 12))
        tk.Label(filters, text="Filter Riwayat", bg=COLORS["soft"], fg=COLORS["text"], font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 8)
        )

        tk.Label(filters, text="Plat kendaraan", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=1, column=0, sticky="w", padx=(0, 8))
        plate_var = tk.StringVar(value="Semua kendaraan")
        plate_box = ttk.Combobox(
            filters,
            textvariable=plate_var,
            values=["Semua kendaraan"] + self.get_report_plate_options(),
            state="readonly",
            width=20,
        )
        plate_box.grid(row=1, column=1, sticky="ew", padx=(0, 14))

        tk.Label(filters, text="Jenis kendaraan", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=1, column=2, sticky="w", padx=(0, 8))
        type_var = tk.StringVar(value="Semua jenis")
        type_box = ttk.Combobox(
            filters,
            textvariable=type_var,
            values=["Semua jenis"] + self.get_report_type_options(),
            state="readonly",
            width=18,
        )
        type_box.grid(row=1, column=3, sticky="ew", padx=(0, 14))

        tk.Label(filters, text="Tanggal mulai", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        date_from = tk.Entry(filters, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, width=22)
        date_from.insert(0, "YYYY-MM-DD")
        date_from.bind("<FocusIn>", lambda event: date_from.delete(0, tk.END) if date_from.get() == "YYYY-MM-DD" else None)
        date_from.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=(8, 0), ipady=5)

        tk.Label(filters, text="Tanggal akhir", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=2, column=2, sticky="w", padx=(0, 8), pady=(8, 0))
        date_to = tk.Entry(filters, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, width=22)
        date_to.insert(0, "YYYY-MM-DD")
        date_to.bind("<FocusIn>", lambda event: date_to.delete(0, tk.END) if date_to.get() == "YYYY-MM-DD" else None)
        date_to.grid(row=2, column=3, sticky="ew", padx=(0, 14), pady=(8, 0), ipady=5)

        for column in (1, 3):
            filters.grid_columnconfigure(column, weight=1)

        table_holder = tk.Frame(card, bg=COLORS["card"])
        table_holder.pack(fill="both", expand=True)
        status_label = tk.Label(card, text="", bg=COLORS["card"], fg=COLORS["muted"], font=("Segoe UI", 9))
        status_label.pack(anchor="w", pady=(8, 0))

        def collect_filters():
            def parse_date(entry, label):
                value = entry.get().strip()
                if not value or value == "YYYY-MM-DD":
                    return None
                for date_format in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                raise ValueError(f"{label} harus berformat YYYY-MM-DD atau DD-MM-YYYY.")

            start_date = parse_date(date_from, "Tanggal mulai")
            end_date = parse_date(date_to, "Tanggal akhir")
            if start_date and end_date and start_date > end_date:
                raise ValueError("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return {
                "plate": "" if plate_var.get() == "Semua kendaraan" else plate_var.get(),
                "vehicle_type": "" if type_var.get() == "Semua jenis" else type_var.get(),
                "date_from": start_date,
                "date_to": end_date,
            }

        def refresh():
            try:
                filters_data = collect_filters()
            except ValueError as error:
                messagebox.showwarning("Filter tanggal", str(error))
                return
            for widget in table_holder.winfo_children():
                widget.destroy()
            rows = self.get_log_rows(filters=filters_data)
            self.create_table(table_holder, ("Plat", "Jenis", "Driver", "Lokasi", "Jarak", "BBM", "Waktu Digunakan"), rows)
            status_label.configure(text=f"Menampilkan {len(rows)} riwayat perjalanan.")

        def reset_filters():
            plate_var.set("Semua kendaraan")
            type_var.set("Semua jenis")
            date_from.delete(0, tk.END)
            date_from.insert(0, "YYYY-MM-DD")
            date_to.delete(0, tk.END)
            date_to.insert(0, "YYYY-MM-DD")
            refresh()

        self.button(filters, "Terapkan Filter", refresh, COLORS["primary"]).grid(row=1, column=4, rowspan=2, padx=(4, 8), ipadx=12, ipady=6)
        self.button(filters, "Reset", reset_filters, COLORS["muted"]).grid(row=1, column=5, rowspan=2, ipadx=12, ipady=6)
        refresh()

    def show_statistik(self):
        if not self.clear_content("Statistik", "Ringkasan, grafik sederhana, dan analisis penggunaan kendaraan."):
            return
        stats = self.get_summary_stats()
        top = tk.Frame(self.content, bg=COLORS["bg"])
        top.pack(fill="x", padx=24, pady=12)
        for index, (label, value) in enumerate(
            [("Total Perjalanan", stats["logs"]), ("Total Jarak", f"{stats['distance']:.0f} KM"), ("Total BBM", f"{stats['fuel']:.1f} L"), ("Rata-rata BBM", f"{stats['avg_fuel']:.2f} L")]
        ):
            frame = self.card(top)
            frame.grid(row=0, column=index, sticky="nsew", padx=(0, 12))
            top.grid_columnconfigure(index, weight=1)
            tk.Label(frame, text=label, bg=COLORS["card"], fg=COLORS["muted"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(frame, text=str(value), bg=COLORS["card"], fg=COLORS["text"], font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(4, 0))

        charts = tk.Frame(self.content, bg=COLORS["bg"])
        charts.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        left = self.card(charts, "Monitoring per Kendaraan")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.draw_vehicle_bar(left)
        right = self.card(charts, "Penggunaan BBM per Bulan")
        right.pack(side="left", fill="both", expand=True)
        self.draw_monthly_chart(right)

    def show_laporan(self):
        if not self.clear_content("Riwayat & Laporan", "Lihat riwayat perjalanan, gunakan filter, dan export laporan monitoring kendaraan."):
            return
        card = self.card(self.content, "Riwayat Monitoring & Laporan")
        card.pack(fill="both", expand=True, padx=24, pady=12)

        filter_card = tk.Frame(card, bg=COLORS["soft"], padx=12, pady=10)
        filter_card.pack(fill="x", pady=(0, 12))
        tk.Label(
            filter_card,
            text="Filter Laporan",
            bg=COLORS["soft"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 8))

        tk.Label(filter_card, text="Plat kendaraan", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=1, column=0, sticky="w", padx=(0, 8))
        vehicle_var = tk.StringVar(value="Semua kendaraan")
        vehicle_box = ttk.Combobox(
            filter_card,
            textvariable=vehicle_var,
            values=["Semua kendaraan"] + self.get_report_plate_options(),
            state="readonly",
            width=20,
        )
        vehicle_box.grid(row=1, column=1, sticky="ew", padx=(0, 14))

        tk.Label(filter_card, text="Jenis kendaraan", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=1, column=2, sticky="w", padx=(0, 8))
        vehicle_type_var = tk.StringVar(value="Semua jenis")
        vehicle_type_box = ttk.Combobox(
            filter_card,
            textvariable=vehicle_type_var,
            values=["Semua jenis"] + self.get_report_type_options(),
            state="readonly",
            width=18,
        )
        vehicle_type_box.grid(row=1, column=3, sticky="ew", padx=(0, 14))

        tk.Label(filter_card, text="Tanggal mulai", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        date_from = tk.Entry(filter_card, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, width=22)
        date_from.insert(0, "YYYY-MM-DD")
        date_from.bind("<FocusIn>", lambda event: date_from.delete(0, tk.END) if date_from.get() == "YYYY-MM-DD" else None)
        date_from.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=(8, 0), ipady=5)

        tk.Label(filter_card, text="Tanggal akhir", bg=COLORS["soft"], fg=COLORS["text"]).grid(row=2, column=2, sticky="w", padx=(0, 8), pady=(8, 0))
        date_to = tk.Entry(filter_card, bg=COLORS["input"], fg=COLORS["text"], relief="solid", bd=1, width=22)
        date_to.insert(0, "YYYY-MM-DD")
        date_to.bind("<FocusIn>", lambda event: date_to.delete(0, tk.END) if date_to.get() == "YYYY-MM-DD" else None)
        date_to.grid(row=2, column=3, sticky="ew", padx=(0, 14), pady=(8, 0), ipady=5)

        for column in (1, 3):
            filter_card.grid_columnconfigure(column, weight=1)

        summary = self.get_summary_stats()
        row = tk.Frame(card, bg=COLORS["card"])
        row.pack(fill="x", pady=(0, 16))
        summary_values = {}
        for label, value in [("Total Perjalanan", summary["logs"]), ("Total Jarak", f"{summary['distance']:.0f} KM"), ("Total BBM", f"{summary['fuel']:.1f} L")]:
            box = tk.Frame(row, bg=COLORS["soft"], padx=16, pady=12)
            box.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(box, text=label, bg=COLORS["soft"], fg=COLORS["muted"]).pack(anchor="w")
            value_label = tk.Label(box, text=str(value), bg=COLORS["soft"], fg=COLORS["text"], font=("Segoe UI", 18, "bold"))
            value_label.pack(anchor="w")
            summary_values[label] = value_label

        table_holder = tk.Frame(card, bg=COLORS["card"])
        table_holder.pack(fill="both", expand=True)
        status_label = tk.Label(card, text="", bg=COLORS["card"], fg=COLORS["muted"], font=("Segoe UI", 9))
        status_label.pack(anchor="w", pady=(8, 0))

        def collect_filters():
            def parse_date(entry, label):
                value = entry.get().strip()
                if not value or value == "YYYY-MM-DD":
                    return None
                for date_format in ("%Y-%m-%d", "%d-%m-%Y"):
                    try:
                        return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                raise ValueError(f"{label} harus berformat YYYY-MM-DD atau DD-MM-YYYY.")

            start_date = parse_date(date_from, "Tanggal mulai")
            end_date = parse_date(date_to, "Tanggal akhir")
            if start_date and end_date and start_date > end_date:
                raise ValueError("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return {
                "plate": "" if vehicle_var.get() == "Semua kendaraan" else vehicle_var.get(),
                "vehicle_type": "" if vehicle_type_var.get() == "Semua jenis" else vehicle_type_var.get(),
                "date_from": start_date,
                "date_to": end_date,
            }

        def refresh():
            try:
                filters = collect_filters()
            except ValueError as error:
                messagebox.showwarning("Filter tanggal", str(error))
                return
            for widget in table_holder.winfo_children():
                widget.destroy()
            filtered_summary = self.get_summary_stats(filters)
            summary_values["Total Perjalanan"].configure(text=str(filtered_summary["logs"]))
            summary_values["Total Jarak"].configure(text=f"{filtered_summary['distance']:.0f} KM")
            summary_values["Total BBM"].configure(text=f"{filtered_summary['fuel']:.1f} L")
            rows = self.get_log_rows(filters=filters)
            self.create_table(table_holder, ("Plat", "Jenis", "Driver", "Lokasi", "Jarak", "BBM", "Waktu Digunakan"), rows)
            status_label.configure(text=f"Menampilkan {len(rows)} perjalanan sesuai filter.")

        def export_filtered():
            try:
                filters = collect_filters()
            except ValueError as error:
                messagebox.showwarning("Filter tanggal", str(error))
                return
            self.export_excel(filters)

        self.button(filter_card, "Terapkan Filter", refresh, COLORS["primary"]).grid(row=1, column=4, rowspan=2, padx=(4, 8), ipadx=12, ipady=6)
        self.button(filter_card, "Reset", lambda: [vehicle_var.set("Semua kendaraan"), vehicle_type_var.set("Semua jenis"), date_from.delete(0, tk.END), date_from.insert(0, "YYYY-MM-DD"), date_to.delete(0, tk.END), date_to.insert(0, "YYYY-MM-DD"), refresh()], COLORS["muted"]).grid(row=1, column=5, rowspan=2, ipadx=12, ipady=6)
        self.button(filter_card, "Export Excel", export_filtered, COLORS["success"]).grid(row=1, column=6, rowspan=2, padx=(8, 0), ipadx=12, ipady=6)

        actions = tk.Frame(card, bg=COLORS["card"])
        actions.pack(fill="x", pady=(12, 0))
        self.button(actions, "Cetak Laporan", lambda: messagebox.showinfo("Info", "Gunakan file Excel untuk dicetak."), COLORS["primary"]).pack(side="left", fill="x", expand=True, ipady=8)
        refresh()

    def create_table(self, parent, columns, rows):
        frame = tk.Frame(parent, bg=COLORS["card"])
        frame.pack(fill="both", expand=True)
        scroll_y = ttk.Scrollbar(frame, orient="vertical")
        scroll_x = ttk.Scrollbar(frame, orient="horizontal")
        tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=135, anchor="center" if column in ("ID", "No", "Jarak", "BBM") else "w")
        for row in rows:
            tree.insert("", "end", values=row)
        return tree

    def get_summary_stats(self, filters=None):
        vehicles = self.fetchone("SELECT COUNT(*) FROM kendaraan_dinas")[0]
        drivers = self.fetchone("SELECT COUNT(*) FROM driver")[0]
        where_sql, params = self.get_log_filter_sql(filters)
        summary = self.fetchone(
            f"""
            SELECT COUNT(*), COALESCE(SUM(l.jarak_tempuh),0),
                   COALESCE(SUM(l.estimasi_bbm),0), COALESCE(AVG(l.estimasi_bbm),0)
            FROM log_monitoring l
            LEFT JOIN kendaraan_dinas k ON l.no_plat = k.no_plat
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            {where_sql}
            """,
            tuple(params),
        )
        logs, distance, fuel, avg_fuel = summary
        return {
            "vehicles": vehicles,
            "drivers": drivers,
            "logs": logs,
            "distance": float(distance or 0),
            "fuel": float(fuel or 0),
            "avg_fuel": float(avg_fuel or 0),
        }

    def get_log_filter_sql(self, filters=None):
        if not filters:
            return "", []
        conditions = []
        params = []
        if filters.get("plate"):
            conditions.append("l.no_plat=%s")
            params.append(filters["plate"])
        if filters.get("vehicle_type"):
            conditions.append("j.nama_jenis=%s")
            params.append(filters["vehicle_type"])
        if filters.get("date_from"):
            conditions.append("DATE(l.waktu)>=%s")
            params.append(filters["date_from"])
        if filters.get("date_to"):
            conditions.append("DATE(l.waktu)<=%s")
            params.append(filters["date_to"])
        return (" WHERE " + " AND ".join(conditions)) if conditions else "", params

    def get_log_rows(self, limit=None, keyword=None, filters=None):
        query = """
            SELECT l.no_plat, COALESCE(j.nama_jenis, '-'), COALESCE(d.nama_driver, '-'), l.lokasi,
                   l.jarak_tempuh, ROUND(l.estimasi_bbm, 2), DATE_FORMAT(l.waktu, '%d-%m-%Y %H:%i')
            FROM log_monitoring l
            LEFT JOIN driver d ON l.id_driver = d.id_driver
            LEFT JOIN kendaraan_dinas k ON l.no_plat = k.no_plat
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
        """
        where_sql, params = self.get_log_filter_sql(filters)
        conditions = []
        if where_sql:
            conditions.append(where_sql[7:])
        if keyword:
            conditions.append("(l.no_plat LIKE %s OR d.nama_driver LIKE %s OR j.nama_jenis LIKE %s OR l.lokasi LIKE %s)")
            params.extend([keyword, keyword, keyword, keyword])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY l.waktu DESC"
        if limit:
            query += f" LIMIT {int(limit)}"
        return self.fetchall(query, tuple(params))

    def get_driver_options(self):
        return [f"{row[0]} - {row[1]}" for row in self.fetchall("SELECT id_driver, nama_driver FROM driver ORDER BY nama_driver")]

    def get_kecamatan_options(self):
        rows = self.fetchall(
            """
            SELECT DISTINCT nama_area
            FROM (
                SELECT TRIM(kecamatan) AS nama_area FROM wilayah
                UNION ALL
                SELECT TRIM(kecamatan) AS nama_area FROM lokasi_layanan
            ) area
            WHERE nama_area IS NOT NULL AND nama_area <> ''
            ORDER BY nama_area
            """
        )
        return [row[0] for row in rows]

    def get_wilayah_options(self, kecamatan=None):
        if not kecamatan:
            return []
        rows = self.fetchall(
            """
            SELECT id_wilayah, desa_kelurahan
            FROM wilayah
            WHERE LOWER(TRIM(kecamatan))=LOWER(TRIM(%s))
            ORDER BY desa_kelurahan
            """,
            (kecamatan.strip(),),
        )
        return [f"{row[0]} - {row[1]}" for row in rows]

    def get_wilayah_master_options(self):
        return [
            f"{row[0]} - {row[1]} ({row[2]})"
            for row in self.fetchall(
                "SELECT id_wilayah, desa_kelurahan, kecamatan FROM wilayah ORDER BY kecamatan, desa_kelurahan"
            )
        ]

    def get_lokasi_options(self, kecamatan=None, id_wilayah=None):
        if not kecamatan and not id_wilayah:
            return []
        conditions = []
        params = []
        if kecamatan:
            conditions.append("LOWER(TRIM(l.kecamatan))=LOWER(TRIM(%s))")
            params.append(kecamatan.strip())
        if id_wilayah:
            conditions.append("EXISTS (SELECT 1 FROM lokasi_wilayah lw WHERE lw.id_lokasi=l.id_lokasi AND lw.id_wilayah=%s)")
            params.append(id_wilayah)
        rows = self.fetchall(
            f"SELECT DISTINCT l.id_lokasi, l.nama_lokasi FROM lokasi_layanan l WHERE {' OR '.join(conditions)} ORDER BY l.nama_lokasi",
            tuple(params),
        )
        return [f"{row[0]} - {row[1]}" for row in rows]

    def get_jenis_options(self):
        return [f"{row[0]} - {row[1]}" for row in self.fetchall("SELECT id_jenis, nama_jenis FROM jenis_kendaraan ORDER BY nama_jenis")]

    def get_report_plate_options(self):
        return [row[0] for row in self.fetchall("SELECT no_plat FROM kendaraan_dinas ORDER BY no_plat")]

    def get_report_type_options(self):
        return [row[0] for row in self.fetchall("SELECT nama_jenis FROM jenis_kendaraan ORDER BY nama_jenis")]

    def get_kendaraan_options(self):
        return [f"{row[0]} - {row[1]}" for row in self.fetchall("SELECT id_kendaraan, no_plat FROM kendaraan_dinas ORDER BY no_plat")]

    def load_kendaraan(self, row_id):
        row = self.fetchone(
            """
            SELECT k.no_plat, k.konsumsi_km_per_liter, k.id_jenis, COALESCE(j.nama_jenis, '')
            FROM kendaraan_dinas k
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            WHERE k.id_kendaraan=%s
            """,
            (row_id,),
        )
        return {
            "no_plat": row[0],
            "konsumsi": row[1],
            "id_jenis": f"{row[2]} - {row[3]}" if row[2] else "",
        }

    def insert_kendaraan(self, values):
        self.execute(
            "INSERT INTO kendaraan_dinas (no_plat, konsumsi_km_per_liter, id_jenis) VALUES (%s,%s,%s)",
            (values["no_plat"].upper(), values["konsumsi"], self.extract_id(values["id_jenis"])),
        )

    def update_kendaraan(self, row_id, values):
        self.execute(
            "UPDATE kendaraan_dinas SET no_plat=%s, konsumsi_km_per_liter=%s, id_jenis=%s WHERE id_kendaraan=%s",
            (values["no_plat"].upper(), values["konsumsi"], self.extract_id(values["id_jenis"]), row_id),
        )

    def load_driver(self, row_id):
        row = self.fetchone(
            """
            SELECT d.nama_driver, d.id_kendaraan, COALESCE(k.no_plat, '')
            FROM driver d
            LEFT JOIN kendaraan_dinas k ON d.id_kendaraan = k.id_kendaraan
            WHERE d.id_driver=%s
            """,
            (row_id,),
        )
        return {
            "nama_driver": row[0],
            "id_kendaraan": f"{row[1]} - {row[2]}" if row[1] else "",
        }

    def insert_driver(self, values):
        self.execute(
            "INSERT INTO driver (nama_driver, id_kendaraan) VALUES (%s,%s)",
            (values["nama_driver"].upper(), self.extract_id(values["id_kendaraan"])),
        )

    def update_driver(self, row_id, values):
        self.execute(
            "UPDATE driver SET nama_driver=%s, id_kendaraan=%s WHERE id_driver=%s",
            (values["nama_driver"].upper(), self.extract_id(values["id_kendaraan"]), row_id),
        )

    def load_wilayah(self, row_id):
        row = self.fetchone("SELECT desa_kelurahan, kecamatan FROM wilayah WHERE id_wilayah=%s", (row_id,))
        return {"desa_kelurahan": row[0], "kecamatan": row[1]}

    def load_lokasi(self, row_id):
        row = self.fetchone(
            """
            SELECT l.nama_lokasi, l.jarak_km, l.kecamatan
            FROM lokasi_layanan l
            WHERE l.id_lokasi=%s
            """,
            (row_id,),
        )
        return {"nama_lokasi": row[0], "jarak_km": row[1], "kecamatan": row[2] or ""}

    def extract_id(self, value):
        if not value:
            return None
        try:
            return int(str(value).split(" - ")[0])
        except ValueError:
            return None

    def draw_monthly_chart(self, parent):
        rows = self.fetchall(
            """
            SELECT MONTH(waktu), COUNT(*)
            FROM log_monitoring
            GROUP BY MONTH(waktu)
            ORDER BY MONTH(waktu)
            """
        )
        data = {month: count for month, count in rows}
        canvas = tk.Canvas(parent, height=230, bg=COLORS["card"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        max_value = max(data.values(), default=1)
        labels = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        for index, label in enumerate(labels):
            value = data.get(index + 1, 0)
            x = 35 + index * 42
            height = int((value / max_value) * 140) if max_value else 0
            canvas.create_rectangle(x, 180 - height, x + 24, 180, fill=COLORS["primary"], outline="")
            canvas.create_text(x + 12, 198, text=label, fill=COLORS["muted"], font=("Segoe UI", 8))
            canvas.create_text(x + 12, 170 - height, text=str(value), fill=COLORS["text"], font=("Segoe UI", 8, "bold"))

    def draw_type_summary(self, parent):
        rows = self.fetchall(
            """
            SELECT COALESCE(j.nama_jenis, 'Tidak diketahui'), COALESCE(SUM(l.estimasi_bbm),0)
            FROM log_monitoring l
            LEFT JOIN kendaraan_dinas k ON l.no_plat = k.no_plat
            LEFT JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis
            GROUP BY j.nama_jenis
            """
        )
        canvas = tk.Canvas(parent, height=230, bg=COLORS["card"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        colors = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["purple"], COLORS["danger"]]
        total = sum(float(row[1] or 0) for row in rows) or 1
        start = 0
        for index, (label, value) in enumerate(rows or [("Belum ada data", 1)]):
            extent = float(value or 0) / total * 359 if rows else 359
            canvas.create_arc(40, 30, 170, 160, start=start, extent=extent, fill=colors[index % len(colors)], outline="white")
            canvas.create_rectangle(220, 45 + index * 26, 234, 59 + index * 26, fill=colors[index % len(colors)], outline="")
            canvas.create_text(242, 52 + index * 26, text=f"{label}  {float(value or 0):.1f} L", anchor="w", fill=COLORS["text"], font=("Segoe UI", 9))
            start += extent

    def draw_vehicle_bar(self, parent):
        rows = self.fetchall(
            """
            SELECT l.no_plat, COUNT(*)
            FROM log_monitoring l
            GROUP BY l.no_plat
            ORDER BY COUNT(*) DESC
            LIMIT 8
            """
        )
        canvas = tk.Canvas(parent, height=280, bg=COLORS["card"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        max_value = max([row[1] for row in rows], default=1)
        for index, (plate, value) in enumerate(rows):
            y = 28 + index * 30
            width = int((value / max_value) * 300)
            canvas.create_text(18, y + 8, text=plate, anchor="w", fill=COLORS["text"], font=("Segoe UI", 9))
            canvas.create_rectangle(120, y, 120 + width, y + 18, fill=COLORS["primary"], outline="")
            canvas.create_text(130 + width, y + 9, text=str(value), anchor="w", fill=COLORS["text"], font=("Segoe UI", 9, "bold"))

    def export_excel(self, filters=None):
        try:
            rows = self.get_log_rows(filters=filters)
            if not rows:
                messagebox.showwarning("Info", "Belum ada data monitoring.")
                return
            os.makedirs("laporan", exist_ok=True)
            file_name = f"laporan/laporan_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df = pd.DataFrame(rows, columns=["Plat", "Jenis Kendaraan", "Driver", "Lokasi", "Jarak", "BBM", "Waktu Digunakan"])
            df.to_excel(file_name, index=False)
            messagebox.showinfo("Sukses", f"Laporan tersimpan:\n{file_name}")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def on_close(self):
        try:
            if self.cap:
                self.cap.release()
            if self.conn:
                self.conn.close()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ModernMonitoringApp().run()
