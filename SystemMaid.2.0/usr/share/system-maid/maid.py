#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTextEdit, 
    QCheckBox, QGroupBox, QScrollArea, QDialog, 
    QStackedWidget, QFrame, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QProcess, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QProgressBar

# Pardus/Debian uyumluluğu ve Fusion stili zorlaması
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_PLUGIN_PATH'] = ''
# Wayland desteği ve X11 geri dönüşü (Fallback)
os.environ['QT_QPA_PLATFORM'] = 'wayland;xcb'
# Yüksek çözünürlüklü ekran desteği (HIDPI)
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

# Betiğin bulunduğu dizini al
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "maid.png")
ICONS_DIR = os.path.join(BASE_DIR, "icons")

class DefragCheckDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HDD Fragmentation Check")
        self.setFixedSize(400, 200)
        self.layout = QVBoxLayout(self)
        
        self.info_label = QLabel("Click 'Start' to analyze the fragmentation score of the root partition (/).\nThis may take a minute.")
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Meşgul (indeterminant) mod
        self.progress.setValue(0)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False) # Başta yüzde görünmesin
        self.layout.addWidget(self.progress)
        
        self.btn_start = QPushButton("Start Analysis")
        self.btn_start.clicked.connect(self.start_analysis)
        self.layout.addWidget(self.btn_start)
        
        self.process = QProcess()
        self.process.finished.connect(self.on_finished)

    def start_analysis(self):
        self.btn_start.setEnabled(False)
        self.progress.setRange(0, 0) # Meşgul (sonsuz döngü) modu başlat
        self.info_label.setText("Analyzing system... Please wait.")
        # e4defrag -c komutuyla analiz yapar
        self.process.start("pkexec", ["bash", "-c", "e4defrag -c /"])

    def on_finished(self):
        self.progress.setRange(0, 100) # Meşgul modundan çık
        self.progress.setValue(100)
        self.btn_start.setEnabled(True)
        
        output = self.process.readAllStandardOutput().data().decode()
        
        # e4defrag çıktısını daha hassas ayıklıyoruz (Regex yerine güvenli string kontrolü)
        score_line = ""
        for line in output.split('\n'):
            if "Fragmentation score" in line:
                score_line = line.strip()
                break
        
        if score_line:
            try:
                # Satırdaki son rakamı çekelim ve skor olarak çıktı ekranına basalım.
                score_val = int(score_line.split()[-1])
                
                # Durum belirleme
                if score_val <= 30:
                    status, color = "GOOD", "#27ae60"
                elif score_val <= 55:
                    status, color = "FAIR", "#f39c12"
                else:
                    status, color = "POOR", "#e74c3c"
                
                result_html = (
                    f"<div style='text-align: center;'>"
                    f"<span style='font-size: 13pt; font-weight: bold;'>Analysis Complete</span><br><br>"
                    f"Fragmentation Score: <span style='font-size: 14pt; color: {color}; font-weight: bold;'>{score_val}</span><br>"
                    f"System Status: <b style='color: {color};'>{status}</b><br><br>"
                    f"<small style='color: #7f8c8d;'>(0-30: Good | 31-55: Fair | 56+: Poor)</small>"
                    f"</div>"
                )
                self.info_label.setText(result_html)
            except Exception as e:
                # Eğer sayısal analiz başarısız olursa ham sonucu göstersin
                self.info_label.setText(f"Analysis Finished:<br><br><b>{score_line}</b>")
        else:
            self.info_label.setText("No fragmentation score found. Your disk might be an SSD or the partition is unsupported.")

class SystemMaid(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.VERSION = "2.0.0" # Yeni GUI ile sürüm atlatıldı bir sonraki sürümde dinamik dil getiricem.
        self.current_lang = 'tr' 
        self.process = None
        self.output_log = None
        
        # Pencere Ayarları
        self.setWindowTitle(f"System Maid v{self.VERSION}")
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(100, 100, 970, 700)
        
        # Fusion stilini ayarla
        self.setStyle(QApplication.style()) 
        QApplication.setStyle("Fusion")
        
        self.setup_ui()
        
    def setup_ui(self):
        
        # Ana Merkezi Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Ana Yatay Düzen (Sol Menü | Sağ İçerik)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- SOL PANEL (SIDEBAR) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250) #Bu şimdilik yeter buna ellemicem artık. 
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                border-left: 5px solid transparent;
                padding: 15px;
                text-align: left;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton[active="true"] {
                background-color: #34495e;
                border-left: 5px solid #3498db;
                color: #3498db;
            }
        """)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 20, 0, 0)
        self.sidebar_layout.setSpacing(5)
        
        # Logo ve Başlık (Yatay Düzen)
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(15, 10, 10, 10)
        
        # Logo Görseli
        self.logo_img = QLabel()
        if os.path.exists(ICON_PATH):
            self.logo_img.setPixmap(QPixmap(ICON_PATH).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            # İkon bulunamazsa boş kalmasın diye genişlik veriyoruz
            self.logo_img.setFixedWidth(72)
        
        # Yazı Alanı için Dikey Düzen (Başlık + Alt Yazı)
        self.text_container_vbox = QVBoxLayout()
        self.text_container_vbox.setSpacing(2)

        # Ana Başlık
        self.logo_text = QLabel("System Maid")
        self.logo_text.setStyleSheet("color: white; font-size: 17pt; font-weight: bold;")
        
        # Alt Başlık (Slogan)
        self.slogan_text = QLabel("Advanced System Cleaner\nfor Debian based systems")
        self.slogan_text.setStyleSheet("color: #bdc3c7; font-size: 9pt; font-weight: normal;")
        self.slogan_text.setWordWrap(True)

        self.text_container_vbox.addWidget(self.logo_text)
        self.text_container_vbox.addWidget(self.slogan_text)
        
        # Bileşenleri Ana Yatay Layout'a Ekle
        self.header_layout.addWidget(self.logo_img)
        self.header_layout.addLayout(self.text_container_vbox)
        self.header_layout.addStretch(1)
        
        # Widget'ı Sidebar'a Ekle
        self.sidebar_layout.addWidget(self.header_widget)
        
        # Menü Butonları (İkonlu ve Büyük Boyutlu)
        icon_size = 32
        
        self.btn_nav_garbage = QPushButton(QIcon(os.path.join(ICONS_DIR, "junk-privacy.png")), " Junk-Privacy Cleanup")
        self.btn_nav_garbage.setIconSize(QSize(icon_size, icon_size))
        
        self.btn_nav_apt = QPushButton(QIcon(os.path.join(ICONS_DIR, "apt-package.png")), " APT Package Cleanup")
        self.btn_nav_apt.setIconSize(QSize(icon_size, icon_size))
        
        self.btn_nav_opt = QPushButton(QIcon(os.path.join(ICONS_DIR, "system-optimization.png")), " System Optimization")
        self.btn_nav_opt.setIconSize(QSize(icon_size, icon_size))
        
        # Butonları bir gruba dahil ederek sadece birinin seçili kalmasını sağlıyoruz
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        for i, btn in enumerate([self.btn_nav_garbage, self.btn_nav_apt, self.btn_nav_opt]):
            btn.setCheckable(True)
            self.nav_group.addButton(btn, i)
            self.sidebar_layout.addWidget(btn)
            
        self.sidebar_layout.addStretch(1)
        
        
        # Alt Bilgi (Sürüm)
        self.ver_label = QLabel(f"v{self.VERSION}")
        self.ver_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        self.ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(self.ver_label)
        
        self.main_layout.addWidget(self.sidebar)
        
        # --- SAĞ PANEL (İÇERİK) ---
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(10)
        
        # Üst Araç Çubuğu (Dil ve Hakkında)
        self.top_bar = QHBoxLayout()
        self.btn_lang = QPushButton("Language")
        self.btn_about = QPushButton("About")
        self.btn_about.clicked.connect(self.show_about)
        self.btn_lang.clicked.connect(lambda: QMessageBox.information(self, "Language / Dil", "Language support has not yet been added to the program.\nBut it will be added in future versions."))
        # Butonların stili ve boyut sınırları
        
        self.btn_lang.setFixedWidth(100)
        self.btn_about.setFixedWidth(100)
        
        self.top_bar.addStretch(1)
        self.top_bar.addWidget(self.btn_lang)
        self.top_bar.addSpacing(10)
        self.top_bar.addWidget(self.btn_about)
        
        self.right_layout.addLayout(self.top_bar)
        
        # Sayfa Değiştirici (Stacked Widget)
        self.pages = QStackedWidget()
        self.page_garbage = self.create_garbage_page()
        self.page_apt = self.create_apt_page()
        self.page_opt = self.create_opt_page()
        
        self.pages.addWidget(self.page_garbage)
        self.pages.addWidget(self.page_apt)
        self.pages.addWidget(self.page_opt)
        
        self.right_layout.addWidget(self.pages)
        
        # Log Alanı (Sabit Alt Kısım)
        self.output_log = QTextEdit()
        self.output_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Monospace';
                font-size: 10pt;
                border: 2px solid #34495e;
            }
        """)
        self.output_log.setReadOnly(True)
        self.output_log.setMaximumHeight(150)
        self.output_log.setPlaceholderText("The transaction logs will appear here...")
        self.right_layout.addWidget(self.output_log)
        
        self.main_layout.addWidget(self.right_container)
        
        # Sinyal Bağlantıları
        self.btn_nav_garbage.clicked.connect(lambda: self.switch_page(0))
        self.btn_nav_apt.clicked.connect(lambda: self.switch_page(1))
        self.btn_nav_opt.clicked.connect(lambda: self.switch_page(2))
        
        # Varsayılan sayfa
        self.switch_page(0)
        
    def show_about(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About System Maid")
        about_dialog.setFixedSize(450, 480)
        layout = QVBoxLayout(about_dialog)
        layout.setSpacing(15)

        # Logo
        logo_label = QLabel()
        if os.path.exists(ICON_PATH):
            logo_label.setPixmap(QPixmap(ICON_PATH).scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Başlık ve İçerik
        title = QLabel("System Maid")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info_text = (
            "<b>Version:</b> 2.0.0<br>"
            "<b>License:</b> GNU GPLv3<br>"
            "<b>GUI/UX:</b> PyQt6<br>"
            "<b>Developer:</b> A. Serhat KILIÇOĞLU (shampuan)<br>"
            "<b>Github:</b> <a href='https://www.github.com/shampuan' style='color: #3498db;'>www.github.com/shampuan</a>"
        )
        
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)

        description = QLabel(
            "This program is a system cleaner alternative to CCleaner or WiseCleaner for Debian-based Linux systems. "
            "It aims to improve performance by safely making certain system settings without damage, while protecting "
            "your privacy by cleaning unnecessary waste on your system.\n\n"
            "This program comes with ABSOLUTELY NO WARRANTY."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #bdc3c7; font-size: 10pt;")
        layout.addWidget(description)

        copyright_label = QLabel("Copyright © 2026 - A. Serhat KILIÇOĞLU")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        layout.addWidget(copyright_label)

        # Kapat Butonu
        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(about_dialog.accept)
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        btn_lay.addWidget(btn_close)
        btn_lay.addStretch()
        layout.addLayout(btn_lay)

        about_dialog.exec()

    def show_defrag_check_dialog(self):
        dialog = DefragCheckDialog(self)
        dialog.exec()

    def switch_page(self, index):
        # Sayfayı değiştir
        self.pages.setCurrentIndex(index)
        
        # Butonların stilini güncellemek için zorunlu yenileme
        for btn in self.nav_group.buttons():
            is_active = (self.nav_group.id(btn) == index)
            btn.setChecked(is_active)
            btn.setProperty("active", is_active)
            
            # CSS'in dinamik özelliklerini (active=true/false) yeniden yükle
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    # --- SAYFA OLUŞTURUCULAR ---

    def create_garbage_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Unnecessary Files and Privacy Cleanup")
        g_layout = QVBoxLayout(group)

        # Güvenli Silme
        self.chk_secure = QCheckBox("Enable Secure Erase (shred)")
        
        lbl_secure = QLabel("This option overwrites deleted data with complex data to prevent its recovery.")
        lbl_secure.setWordWrap(True)
        lbl_secure.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Çöp Kutusu
        self.chk_trash = QCheckBox("Empty the Trash")
        
        lbl_trash = QLabel("Clears files from the current user's Trash.")
        lbl_trash.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Son Kullanılanlar (XBEL ve Geçmiş) 
        self.chk_recent = QCheckBox("Clear Recently Used Items and History")
        self.chk_recent.setChecked(True)
        
        lbl_recent = QLabel("Deletes .xbel files, the RecentDocuments folder, and the Zeitgeist history.") # <- Diğer masaüstü ortamlarını da düşünmek zorundayım.
        lbl_recent.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # thumbs.db
        self.chk_thumbs_db = QCheckBox("Clean up Windows thumbs.db files.")
        self.chk_thumbs_db.setChecked(True)
        
        lbl_thumbs_db = QLabel("Cleans up leftover thumbs.db files from Windows shares in the Home directory.")
        lbl_thumbs_db.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Thumbnail Önbelleği
        self.chk_thumbnails = QCheckBox("Clear Thumbnail Cache")
        self.chk_thumbnails.setChecked(True)
        
        lbl_thumbs = QLabel("Removes preview images. May temporarily slow down folder opening times but increases privacy.")
        lbl_thumbs.setWordWrap(True)
        lbl_thumbs.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Widget'ları ekle
        widgets = [
            (self.chk_secure, lbl_secure),
            (self.chk_trash, lbl_trash),
            (self.chk_recent, lbl_recent),
            (self.chk_thumbs_db, lbl_thumbs_db),
            (self.chk_thumbnails, lbl_thumbs)
        ]

        # İkon listesini tanımla
        icons = ["shred.png", "trash-empty.png", "recently-used-items.png", "windows-db.png", "thumbnail.png"]

        for (chk, lbl), icon_name in zip(widgets, icons):
            item_layout = QHBoxLayout()
            
            # Sol İkon
            icon_label = QLabel()
            pix = QPixmap(os.path.join(ICONS_DIR, icon_name))
            icon_label.setPixmap(pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setFixedWidth(60)
            
            # Sağ metin alanı (Check + Açıklama)
            text_vbox = QVBoxLayout()
            text_vbox.addWidget(chk)
            text_vbox.addWidget(lbl)
            
            item_layout.addWidget(icon_label)
            item_layout.addLayout(text_vbox)
            g_layout.addLayout(item_layout)
        
        g_layout.addStretch(1)
        layout.addWidget(group)
        
        self.btn_clean_garbage = QPushButton("Start Selected Cleanup")
        self.btn_clean_garbage.setStyleSheet("background-color: #004700; color: white;")
        self.btn_clean_garbage.setFixedSize(250, 35)
        self.btn_clean_garbage.clicked.connect(self.run_clean)
        garbage_btn_layout = QHBoxLayout()
        garbage_btn_layout.addWidget(self.btn_clean_garbage)
        garbage_btn_layout.addStretch(1) # Butonun uzamasını engeller
        layout.addLayout(garbage_btn_layout)
        return page

    def create_apt_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Advanced Package and System Cleanup (APT)")
        g_layout = QVBoxLayout(group)

        # Autoremove
        self.chk_apt_autoremove = QCheckBox("Remove unnecessary dependencies (autoremove)")
        self.chk_apt_autoremove.setChecked(True)
        
        lbl_auto = QLabel("Removes packages that are no longer needed by the system.")
        lbl_auto.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Autoclean
        self.chk_apt_autoclean = QCheckBox("Clean up old package archives (autoclean)")
        self.chk_apt_autoclean.setChecked(True)
        
        lbl_clean = QLabel("Deletes old package files that are no longer in the repositories.")
        lbl_clean.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        # Fix Missing
        self.chk_apt_fix_missing = QCheckBox("Repair Broken Dependencies")
        # Full Clean
        self.chk_apt_full_clean = QCheckBox("Clear All Package Cache (full clean)")
        
        lbl_full_clean = QLabel("Deletes all downloaded .deb files from the cache. Saves maximum space.")
        lbl_full_clean.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")
        lbl_fix = QLabel("Attempts to repair the corrupted package database and incomplete installations.")
        lbl_fix.setStyleSheet("color: #7f8c8d; margin-bottom: 10px; margin-left: 20px;")

        apt_items = [
            (self.chk_apt_autoremove, lbl_auto, "unnecessary-depends.png"),
            (self.chk_apt_autoclean, lbl_clean, "old-package.png"),
            (self.chk_apt_fix_missing, lbl_fix, "repair-depends.png"),
            (self.chk_apt_full_clean, lbl_full_clean, "trash-empty.png") 
        ]

        for chk, lbl, icon_name in apt_items:
            item_layout = QHBoxLayout()
            icon_label = QLabel()
            pix = QPixmap(os.path.join(ICONS_DIR, icon_name))
            icon_label.setPixmap(pix.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            icon_label.setFixedWidth(60)
            
            text_vbox = QVBoxLayout()
            text_vbox.addWidget(chk)
            text_vbox.addWidget(lbl)
            
            item_layout.addWidget(icon_label)
            item_layout.addLayout(text_vbox)
            g_layout.addLayout(item_layout)

        g_layout.addStretch(1)
        layout.addWidget(group)
        
        self.btn_clean_apt = QPushButton("Execute Package Operations")
        self.btn_clean_apt.setStyleSheet("background-color: #004700; color: white;")
        self.btn_clean_apt.setFixedSize(250, 35)
        self.btn_clean_apt.clicked.connect(self.run_apt_clean)
        apt_btn_layout = QHBoxLayout()
        apt_btn_layout.addWidget(self.btn_clean_apt)
        apt_btn_layout.addStretch(1) # Butonun uzamasını engellemek için sınırlı streç ekliyoruz.
        layout.addLayout(apt_btn_layout)
        return page

    def run_clean(self):
        commands = []
        # Güvenli silme kontrolü (shred)
        shred_prefix = "shred -u -n 1 -z " if self.chk_secure.isChecked() else "rm -rf "

        if self.chk_trash.isChecked():
            commands.append(f"find ~/.local/share/Trash/files/ -mindepth 1 -exec {shred_prefix} {{}} +")
            commands.append(f"find ~/.local/share/Trash/info/ -mindepth 1 -exec rm -f {{}} +")

        if self.chk_recent.isChecked():
            commands.append(f"{shred_prefix} ~/.local/share/recently-used.xbel")
            commands.append(f"find ~/.local/share/RecentDocuments/ -mindepth 1 -exec {shred_prefix} {{}} + 2>/dev/null || true")
            commands.append("find ~/.local/share/zeitgeist -mindepth 1 -delete 2>/dev/null || true")

        if self.chk_thumbnails.isChecked():
            commands.append(f"find ~/.cache/thumbnails/ -type f -exec {shred_prefix} {{}} +")

        if self.chk_thumbs_db.isChecked():
            commands.append("find ~ -name 'thumbs.db' -type f -delete")
            commands.append("find ~ -name 'Thumbs.db' -type f -delete")

        if commands:
            full_command = " && ".join(commands)
            self.start_process(full_command, "Privacy and Junk Cleanup")
        else:
            QMessageBox.information(self, "Information", "Please select the items to be cleaned.")

    def run_apt_clean(self):
        commands = []
        
        # Her işlemden önce paket listesini güncellemek hataları önler
        commands.append("apt-get update")

        if self.chk_apt_autoremove.isChecked():
            commands.append("apt-get autoremove -y")
        
        if self.chk_apt_autoclean.isChecked():
            commands.append("apt-get autoclean")
            
        if self.chk_apt_full_clean.isChecked():
            commands.append("apt-get clean")
            
        if self.chk_apt_fix_missing.isChecked():
            commands.append("apt-get install -f -y")

        if len(commands) > 1: # Sadece update eklenmişse (hiçbir şey seçilmemişse) çalıştırma
            full_command = " && ".join(commands)
            # pkexec bash -c kullanımı yetki sorunlarını çözer
            self.start_process(f"pkexec bash -c '{full_command}'", "APT Package Management")
        else:
            QMessageBox.information(self, "Information", "Please select an APT operation.")

    def start_process(self, command, task_name):
        self.output_log.clear()
        if self.process is None:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
        
        # Önceki bağlantıları güvenli bir şekilde temizle
        try:
            self.process.finished.disconnect()
        except (TypeError, RuntimeError):
            pass
        self.process.finished.connect(lambda code, status, name=task_name: self.handle_finished(code, status, name))

        self.output_log.append(f"\n--- {task_name} Started ---")
        # Eski programdaki gibi log_message yapısı yerine doğrudan output_log'a yazıyoruz
        self.process.start("/bin/bash", ["-c", command])

    def handle_stdout(self):
        data = bytes(self.process.readAllStandardOutput()).decode().strip()
        if data:
            self.output_log.append(data)
            # Otomatik aşağı kaydır
            self.output_log.verticalScrollBar().setValue(
                self.output_log.verticalScrollBar().maximum()
            )

    def handle_stderr(self):
        data = bytes(self.process.readAllStandardError()).decode().strip()
        if data:
            self.output_log.append(f"ERROR: {data}")
    
    def handle_finished(self, exitCode, exitStatus, task_name):
        if exitCode == 0:
            self.output_log.append(f"\n>>> {task_name} completed successfully.")
        else:
            self.output_log.append(f"\n>>> {task_name} finished with an error or was cancelled.")
        
        # Otomatik aşağı kaydır
        self.output_log.verticalScrollBar().setValue(
            self.output_log.verticalScrollBar().maximum()
        )

    def create_opt_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        
        # Kaydırılabilir alan (Seçenekler çoğalırsa sayfa bozulmasın diye)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20) # Bölümler arası boşluk

        # --- LOG TEMİZLİĞİ ---
        log_group = QGroupBox("System Logs")
        log_h_main = QHBoxLayout(log_group) # Yatay ana düzen
        
        # Grup İkonu
        log_icon = QLabel()
        log_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "limit-log.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        log_icon.setFixedWidth(60)
        
        log_vbox = QVBoxLayout()
        log_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        log_desc = QLabel("Cleans system log entries older than 3 days or larger than 50MB to save disk space.")
        log_desc.setWordWrap(True)
        log_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        btn_log = QPushButton("Clear System Logs")
        btn_log.setStyleSheet("background-color: #004700; color: white;")
        btn_log.setFixedSize(200, 35)
        
        
        log_vbox.addWidget(log_desc)
        log_btn_lay = QHBoxLayout()
        log_btn_lay.addWidget(btn_log)
        log_btn_lay.addStretch(1)
        log_vbox.addLayout(log_btn_lay)
        
        log_h_main.addWidget(log_icon)
        log_h_main.addLayout(log_vbox)
        layout.addWidget(log_group)
        
        btn_log.clicked.connect(lambda: self.start_process("pkexec bash -c 'journalctl --vacuum-time=3d --vacuum-size=50M'", "Log Cleanup"))

        # --- RAM OPTİMİZASYONU ---
        ram_group = QGroupBox("Memory (RAM)")
        ram_h_main = QHBoxLayout(ram_group)
        
        ram_icon = QLabel()
        ram_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "clean-mem.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ram_icon.setFixedWidth(60)
        
        ram_vbox = QVBoxLayout()
        ram_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ram_desc = QLabel("Frees up system memory by clearing the temporary cache. Recommended before heavy tasks.")
        ram_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        btn_ram = QPushButton("Drop RAM Caches")
        btn_ram.setStyleSheet("background-color: #004700; color: white;")
        btn_ram.setFixedSize(200, 35)
        btn_ram.clicked.connect(lambda: self.start_process("pkexec bash -c 'sync && echo 3 > /proc/sys/vm/drop_caches && echo Memory caches cleared.'", "RAM Optimization"))
        
        ram_vbox.addWidget(ram_desc)
        ram_vbox.addWidget(btn_ram)
        ram_h_main.addWidget(ram_icon)
        ram_h_main.addLayout(ram_vbox)
        layout.addWidget(ram_group)
        
        # --- SWAP TEMİZLEME ---
        swap_clear_group = QGroupBox("Clear Swap Area")
        swap_clear_h_main = QHBoxLayout(swap_clear_group)
        
        swap_clear_icon = QLabel()
        swap_clear_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "clear-swap.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        swap_clear_icon.setFixedWidth(60)
        
        swap_clear_vbox = QVBoxLayout()
        swap_clear_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        swap_clear_desc = QLabel("Flushes the swap space by moving data back into RAM. This may take a moment.")
        swap_clear_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        btn_clear_swap = QPushButton("Clear Swap Now")
        btn_clear_swap.setStyleSheet("background-color: #004700; color: white;")
        btn_clear_swap.setFixedSize(200, 35)
        btn_clear_swap.clicked.connect(lambda: self.start_process("pkexec bash -c 'swapoff -a && swapon -a'", "Swap Cleaning"))
        
        swap_clear_vbox.addWidget(swap_clear_desc)
        swap_clear_vbox.addWidget(btn_clear_swap)
        swap_clear_h_main.addWidget(swap_clear_icon)
        swap_clear_h_main.addLayout(swap_clear_vbox)
        layout.addWidget(swap_clear_group)

        # --- SWAP AYARI (Çift Butonlu Yapı) ---
        swap_group = QGroupBox("Swapiness Level")
        swap_h_main = QHBoxLayout(swap_group)
        
        swap_level_icon = QLabel()
        swap_level_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "swappines.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        swap_level_icon.setFixedWidth(60)
        
        swap_vbox = QVBoxLayout()
        swap_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        swap_desc = QLabel("Adjusts how aggressively the system uses swap space. 10 is better for desktops, 60 is default.")
        swap_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        swap_btn_layout = QHBoxLayout()
        swap_btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btn_swap_10 = QPushButton("Set to 10 (Desktop)")
        btn_swap_10.setFixedSize(200, 35)
        btn_swap_10.setStyleSheet("background-color: #004700; color: white;")
        btn_swap_60 = QPushButton("Set to 60 (Default)")
        btn_swap_60.setFixedSize(200, 35)
        btn_swap_60.setStyleSheet("background-color: #004700; color: white;")
        btn_swap_10.clicked.connect(lambda: self.start_process("pkexec bash -c 'sysctl vm.swappiness=10'", "Swap: Desktop"))
        btn_swap_60.clicked.connect(lambda: self.start_process("pkexec bash -c 'sysctl vm.swappiness=60'", "Swap: Default"))
        swap_btn_layout.addWidget(btn_swap_10)
        swap_btn_layout.addWidget(btn_swap_60)
        swap_btn_layout.addStretch(1)
        swap_vbox.addWidget(swap_desc)
        swap_vbox.addLayout(swap_btn_layout)
        swap_h_main.addWidget(swap_level_icon)
        swap_h_main.addLayout(swap_vbox)
        layout.addWidget(swap_group)

        # --- SSD OPTİMİZASYONU ---
        ssd_group = QGroupBox("SSD Maintenance (TRIM)")
        ssd_h_main = QHBoxLayout(ssd_group)
        ssd_icon = QLabel()
        ssd_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "optimize-SSD.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        ssd_icon.setFixedWidth(60)
        
        ssd_vbox = QVBoxLayout()
        ssd_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ssd_desc = QLabel("Sends TRIM commands to all mounted filesystems on SSDs to maintain long-term performance.")
        ssd_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        btn_trim = QPushButton("Run SSD TRIM")
        btn_trim.setStyleSheet("background-color: #004700; color: white;")
        btn_trim.setFixedSize(200, 35)
        btn_trim.clicked.connect(lambda: self.start_process("pkexec bash -c 'fstrim -av'", "SSD Optimization"))
        
        ssd_vbox.addWidget(ssd_desc)
        ssd_vbox.addWidget(btn_trim)
        ssd_h_main.addWidget(ssd_icon)
        ssd_h_main.addLayout(ssd_vbox)
        layout.addWidget(ssd_group)

        # --- HDD OPTİMİZASYONU ---
        hdd_group = QGroupBox("HDD Maintenance (Defrag)")
        hdd_h_main = QHBoxLayout(hdd_group)
        hdd_icon = QLabel()
        hdd_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "fragment-hdd.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        hdd_icon.setFixedWidth(60)
        
        hdd_vbox = QVBoxLayout()
        hdd_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        hdd_desc = QLabel("Defragment files on ext4 formatted Hard Disk Drives to improve access speed.")
        hdd_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        btn_defrag = QPushButton("Run HDD Defrag")
        btn_defrag.setStyleSheet("background-color: #004700; color: white;")
        btn_defrag.setFixedSize(200, 35)
        
        # Parçalanma durumu kontrol butonu
        btn_check_defrag = QPushButton("Check Fragmentation Status")
        btn_check_defrag.setFixedSize(200, 35)
        
        # Düzenleme: Butonları yan yana koymak için yeni bir layout
        hdd_btn_layout = QHBoxLayout()
        hdd_btn_layout.addWidget(btn_check_defrag)
        hdd_btn_layout.addWidget(btn_defrag)
        hdd_btn_layout.addStretch(1)
        
        btn_defrag.clicked.connect(lambda: self.start_process("pkexec e4defrag / -v", "HDD Optimization"))
        btn_check_defrag.clicked.connect(self.show_defrag_check_dialog)
        
        hdd_vbox.addWidget(hdd_desc)
        hdd_vbox.addLayout(hdd_btn_layout)
        hdd_h_main.addWidget(hdd_icon)
        hdd_h_main.addLayout(hdd_vbox)
        layout.addWidget(hdd_group)
        # --- GÜÇ MODLARI (Power Management) ---
        power_group = QGroupBox("Power Management")
        power_h_main = QHBoxLayout(power_group)
        
        power_icon = QLabel()
        power_icon.setPixmap(QPixmap(os.path.join(ICONS_DIR, "performance-powersave.png")).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        power_icon.setFixedWidth(60)
        
        power_vbox = QVBoxLayout()
        power_vbox.setAlignment(Qt.AlignmentFlag.AlignLeft)
        power_desc = QLabel("Switch between Power Save for longer battery life or Performance for maximum speed.")
        power_desc.setStyleSheet("color: #7f8c8d; font-size: 9pt;")
        
        power_btn_layout = QHBoxLayout()
        btn_powersave = QPushButton("Power Save")
        btn_powersave.setFixedSize(180, 35)
        btn_balanced = QPushButton("Balanced (Dynamic)")
        btn_balanced.setFixedSize(180, 35)
        btn_performance = QPushButton("Performance")
        btn_performance.setFixedSize(180, 35)
        btn_powersave.setStyleSheet("background-color: #004700; color: white;")
        btn_balanced.setStyleSheet("background-color: #ac8900; color: white;")
        btn_performance.setStyleSheet("background-color: #600f0f; color: white;")
        # Komut tanımlamaları
        cmd_save = "pkexec bash -c 'for d in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo powersave > \"$d\"; done 2>/dev/null; for e in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference; do echo power > \"$e\"; done 2>/dev/null; echo Power Save mode active.'"
        cmd_perf = "pkexec bash -c 'for d in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > \"$d\"; done 2>/dev/null; for e in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference; do echo performance > \"$e\"; done 2>/dev/null; echo Performance mode active.'"
        cmd_balanced = "pkexec bash -c 'for d in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do (echo schedutil > \"$d\" || echo ondemand > \"$d\"); done 2>/dev/null; for e in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference; do echo balance_performance > \"$e\"; done 2>/dev/null; echo Balanced mode active.'"
        
        btn_powersave.clicked.connect(lambda: self.start_process(cmd_save, "Power Mode: Save"))
        btn_balanced.clicked.connect(lambda: self.start_process(cmd_balanced, "Power Mode: Balanced"))
        btn_performance.clicked.connect(lambda: self.start_process(cmd_perf, "Power Mode: Performance"))
        
        power_btn_layout.addWidget(btn_powersave)
        power_btn_layout.addWidget(btn_balanced)
        power_btn_layout.addWidget(btn_performance)
        power_vbox.addWidget(power_desc)
        power_vbox.addLayout(power_btn_layout)
        btn_check_power = QPushButton("Check Current Power Mode")
        
        btn_check_power.clicked.connect(lambda: self.start_process("echo -n 'Current Governor: ' && cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo 'N/A'", "Current Power Mode"))
        power_vbox.addWidget(btn_check_power)
        btn_check_power.setFixedSize(220, 35)
        power_h_main.addWidget(power_icon)
        power_h_main.addLayout(power_vbox)
        layout.addWidget(power_group)
        layout.addStretch(1)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        return page

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMaid()
    window.show()
    sys.exit(app.exec())
