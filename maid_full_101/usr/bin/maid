#!/usr/bin/env python3

import os
import sys
import subprocess
import glob
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTabWidget, QPushButton, QLabel, 
    QTextEdit, QCheckBox, QGroupBox, QScrollArea, 
    QMessageBox, QDialog, QSizePolicy
)
from PySide6.QtCore import Qt, QProcess, QStandardPaths
from PySide6.QtGui import QIcon, QPixmap 

# Qt platform plugin sorununu çözmek için ortam değişkenlerini ayarla
# Bu iki satır, programın gnome gibi ortamlarda sorunsuzca açılması için gereklidir.
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
os.environ['QT_PLUGIN_PATH'] = ''

# --- Ana Uygulama Sınıfı ---
class LinuxCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Dil ayarları ve metin sözlüğü
        self.texts = self._load_localization()
        self.current_lang = 'en' # Varsayılan dil: İngilizce (en)
        
        self.setGeometry(100, 100, 800, 650) 
        self.output_log = None 
        self.process = None 

        # İkon dosyasını bulmaya çalış
        self.icon_path = self.find_icon_file("maid.png")
        if self.icon_path:
            self.setWindowIcon(QIcon(self.icon_path)) 
            
        self.setup_ui()
        self.update_ui_texts() # Başlangıçta İngilizce metinleri yükle
        
    def _load_localization(self):
        """Uygulamanın İngilizce ve Türkçe metinlerini yükler."""
        return {
            'en': {
                'window_title': "System Maid - Linux Cleaner & Optimizer",
                'header_title': "Clean Your System",
                'log_group': "Operation Log and Results",
                'log_start_info': "Application started. Please select cleaning and optimization options.",
                'log_privilege_info': "Privilege Requirement: APT, Defrag, CPU, and RAM operations will use pkexec (Root Privilege).",
                
                # Tab 1: Garbage & Privacy
                'tab_garbage': "Junk & Privacy Cleanup",
                'secure_group': "Secure Deletion Settings",
                'chk_secure_delete': "Activate Secure Deletion (shred)",
                'secure_delete_label': "This option prevents attackers from recovering deleted data using complex data overwriting (shred).",
                'trash_group': "Trash Cleanup",
                'chk_trash': "Empty Current User's Trash Bin",
                'privacy_group': "Specific History Cleanup",
                'chk_recent_xbel': "Clean Recently Used (.xbel) file",
                'chk_recent_docs': "Clean Recently Used Documents folder content",
                'chk_thumbs_db': "Delete thumbs.db files remaining from Linux/Windows Shares",
                'thumbnail_group': "Thumbnail Cache Cleanup",
                'thumbnail_warning': "Thumbnails are small files showing previews in your file manager. Deleting them is not strictly necessary. Deleting them will cause your system to regenerate them, slowing down loading when opening folders full of images/videos. However, thumbnails can provide clues about your content to physical attackers, so you may want to delete them.",
                'chk_thumbs_large': "Clean Large Thumbnails cache (.cache/thumbnails/large)",
                'chk_thumbs_normal': "Clean Normal Thumbnails cache (.cache/thumbnails/normal)",
                'btn_clean_selected': "Clean Selected",
                
                # Tab 2: APT
                'tab_apt': "APT Package Cleanup",
                'apt_group': "APT Package Management Cleanup (Privilege Required)",
                'chk_autoremove': "Autoremove: Delete unnecessary dependencies",
                'chk_autoclean': "Autoclean: Delete old downloaded package files",
                'btn_apt_clean': "Start APT Cleanup",
                
                # Tab 3: Optimization
                'tab_optimization': "System Optimization",
                'defrag_group': "Disk Optimization (Privilege Required)",
                'defrag_label': "WARNING: Modern Linux filesystems (Ext4, Btrfs) generally do not need defragmentation. It is also not recommended for SSDs. It is highly recommended for HDDs and can provide up to 30% speed increase. This process is slow!",
                'btn_defrag': "Start Disk Defragmentation",
                'cpu_group': "CPU Usage Optimization (Privilege Required)",
                'cpu_label': "This process limits CPU usage to %75, extending battery life if you use a laptop. It also ensures your hardware runs cooler, but system speed will noticeably decrease.",
                'btn_cpupower_apply': "Apply CPU Optimization (%75)",
                'btn_cpupower_restore': "Restore Optimization (%100)",
                'ram_group': "RAM Cache Cleanup (Privilege Required)",
                'ram_label': "This process increases available RAM by freeing up data held in the system cache. It is not true memory release and may cause the system to slow down briefly.",
                'btn_ram_clean': "Clean RAM Caches",
                
                # About Dialog
                'about_title': "About System Maid",
                'about_version': "Version:",
                'about_license': "License:",
                'about_programming': "Programming:",
                'about_description': "This program helps your computer run healthier by performing system cleaning and performance adjustments, while protecting your privacy from attackers.",
                'about_disclaimer': "This program comes with no warranty.",
                'btn_ok': "OK",
            },
            'tr': {
                'window_title': "System Maid - Linux Temizleyici ve Optimizasyon Aracı",
                'header_title': "Sisteminizi Temizleyin",
                'log_group': "İşlem Günlüğü ve Sonuçlar",
                'log_start_info': "Uygulama başlatıldı. Lütfen temizlik ve optimizasyon seçeneklerini seçiniz.",
                'log_privilege_info': "Yetki Gereksinimi: APT, Defrag, CPU ve RAM işlemleri için pkexec (Root Yetkisi) kullanılacaktır.",
                
                # Tab 1: Çöp ve Gizlilik
                'tab_garbage': "Çöp ve Gizlilik Temizliği",
                'secure_group': "Güvenli Silme Ayarları",
                'chk_secure_delete': "Güvenli Silmeyi Aktif Et (shred)",
                'secure_delete_label': "Bu seçenek, başkalarının veri kurtarma yöntemiyle sildiğiniz verileri kurtarmasını ve sizi heklemesini önler. Bu yöntem, dosya silinmeden önce üzerine karmaşık veri yazar (shred).",
                'trash_group': "Çöp Kutusu Temizliği",
                'chk_trash': "Geçerli Kullanıcının Çöp Kutusunu Boşalt",
                'privacy_group': "Özel Geçmiş Temizliği",
                'chk_recent_xbel': "Son Kullanılanlar (.xbel) dosyasını temizle",
                'chk_recent_docs': "Son Kullanılan Belgeler (RecentDocuments) klasör içeriğini temizle",
                'chk_thumbs_db': "Linux/Windows Paylaşımlarından Kalan thumbs.db dosyalarını sil",
                'thumbnail_group': "Küçük Resim Önbelleği Temizliği",
                'thumbnail_warning': "Küçük resimler, resim ve video gibi dosyalarınızın dosya yöneticinizde içeriklerini size küçük resim olarak gösteren küçük dosyalardır. Bu dosyaları silmeniz gerekmez. Onları silmeniz durumunda sisteminiz onları yeniden oluşturacak, bu da içi resim ve/veya video dolu bir klasörü açtığınızda içeriğin yüklenmesini yavaşlatacaktır. Ayrıca küçük resimler, bilgisayarınıza fiziksel erişimi olan saldırganların bilgisayarınızda neler tuttuğunuza dair fikir edinmelerine neden olur. Bu yüzden onları da silmek isteyebilirsiniz.",
                'chk_thumbs_large': "Büyük Boyutlu Küçük Resimler önbelleğini temizle",
                'chk_thumbs_normal': "Normal Boyutlu Küçük Resimler önbelleğini temizle",
                'btn_clean_selected': "Seçilenleri Temizle",
                
                # Tab 2: APT
                'tab_apt': "APT Paket Temizliği",
                'apt_group': "APT Paket Yönetimi Temizliği (Yetki Gereklidir)",
                'chk_autoremove': "Otomatik Kaldır: Gereksiz bağımlılıkları sil",
                'chk_autoclean': "Önbelleği Temizle: İndirilen eski paket dosyalarını sil",
                'btn_apt_clean': "APT Temizliğini Başlat",
                
                # Tab 3: Optimizasyon
                'tab_optimization': "Sistem Optimizasyonu",
                'defrag_group': "Disk Optimizasyonu (Yetki Gereklidir)",
                'defrag_label': "UYARI: Modern Linux dosya sistemleri (Ext4, Btrfs) genellikle birleştirmeye ihtiyaç duymazlar. Ayrıca sisteminiz SSD üzerine kuruluysa da birleştirme yapılması önerilmez. Sisteminiz bir HDD üzerinde çalışıyorsa kesinlikle önerilir ve %30'a kadar hız artışı sağlayabilir. Bu işlem uzun sürer!",
                'btn_defrag': "Disk Birleştirmeyi Başlat",
                'cpu_group': "İşlemci Kullanımı Optimizasyonu (Yetki Gereklidir)",
                'cpu_label': "Bu işlem, işlemci kullanımını %75'e sınırlayarak, eğer bir dizüstü kullanıyorsanız batarya kullanım sürenizi uzatır. Ayrıca donanımınızın daha soğuk çalışmasını sağlar. Ancak sistem hızı belirgin şekilde düşer.",
                'btn_cpupower_apply': "CPU Optimizasyonunu Uygula (%75)",
                'btn_cpupower_restore': "Optimizasyonu Geri Al (%100)",
                'ram_group': "RAM ÖnBelleği Temizliği (Yetki Gereklidir)",
                'ram_label': "Bu işlem, sistemin önbellekte tuttuğu verileri serbest bırakarak kullanılabilir RAM miktarını artırır. Gerçek bellek boşaltımı değildir ve sistemin kısa bir süre için yavaşlamasına neden olabilir.",
                'btn_ram_clean': "RAM ÖnBelleklerini Temizle",
                
                # Hakkında Diyalogu
                'about_title': "System Maid Hakkında",
                'about_version': "Sürüm:",
                'about_license': "Lisans:",
                'about_programming': "Programlama:",
                'about_description': "Bu program, sistem temizliği ve performans ayarları yaparak bilgisayarınızın daha sağlıklı çalışmasına yardımcı olurken, özel hayatınızı saldırganlardan korumanıza yardımcı olur.",
                'about_disclaimer': "Bu program hiçbir garanti getirmez.",
                'btn_ok': "Tamam",
            }
        }
        
    def find_icon_file(self, filename):
        """İkon dosyasını olası konumlarda arar."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(base_dir, filename)
        if os.path.exists(local_path):
            return local_path

        global_path = os.path.join("/usr/share/System Maid", filename)
        if os.path.exists(global_path):
            return global_path
        
        # log_message başlangıçta henüz hazır olmayabilir, bu yüzden sadece None döndürüyoruz
        return None

    def setup_ui(self):
        """Kullanıcı arayüzünü (UI) hazırlar."""
        
        # Ana Konteyner ve Düzen
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # --- Üst Başlık ve Butonlar Alanı ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10) 
        
        # İkon Resim Nesnesi (68x68 olarak ayarlandı)
        self.icon_label = QLabel()
        if self.icon_path:
            icon_pixmap = QPixmap(self.icon_path)
            # BURASI 68x68 olarak ayarlandı
            scaled_pixmap = icon_pixmap.scaled(68, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(self.icon_label)
        
        # Başlık Yazısı
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch(1) # Başlık ve ikonları sola yaslamak için
        
        # Hakkında Butonu
        self.btn_about = QPushButton("Hakkında") # Bu butonu da dil ile güncelleyeceğiz, ancak başlangıçta Türkçe bırakıyorum
        self.btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.btn_about)
        
        # Dil Değiştirme Butonu (Evrensel: "Language")
        self.btn_lang = QPushButton("Language")
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        
        main_layout.addWidget(header_widget)
        
        # Sekmeli Alan (Temizlik Görevleri)
        self.tab_widget = QTabWidget()
        
        # Sekme Widget'larını ve düzenlerini tanımla
        self.tab_garbage_widget = self.create_garbage_privacy_tab()
        self.tab_apt_widget = self.create_apt_tab()
        self.tab_optimization_widget = self.create_system_optimization_tab()
        
        self.tab_widget.addTab(self.tab_garbage_widget, "") # Metinler update_ui_texts'te ayarlanacak
        self.tab_widget.addTab(self.tab_apt_widget, "")
        self.tab_widget.addTab(self.tab_optimization_widget, "")

        main_layout.addWidget(self.tab_widget)

        # Sonuç Günlüğü Alanı
        self.log_group = QGroupBox()
        log_layout = QVBoxLayout(self.log_group)
        
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        log_layout.addWidget(self.output_log)

        main_layout.addWidget(self.log_group)

        self.setCentralWidget(main_widget)
        
    def update_ui_texts(self):
        """Mevcut dile göre tüm UI metinlerini günceller."""
        lang = self.current_lang
        texts = self.texts[lang]
        
        # Ana Pencere ve Başlık
        self.setWindowTitle(texts['window_title'])
        self.title_label.setText(texts['header_title'])
        self.log_group.setTitle(texts['log_group'])
        
        # Sekme Başlıkları
        self.tab_widget.setTabText(0, texts['tab_garbage'])
        self.tab_widget.setTabText(1, texts['tab_apt'])
        self.tab_widget.setTabText(2, texts['tab_optimization'])
        
        # Hakkında Butonu (Evrensel olmadığı için çevrilmeli)
        self.btn_about.setText(texts['about_title'])
        
        # Log mesajları (Sadece bir kez eklenir)
        if self.output_log.toPlainText() == "":
            self.log_message(texts['log_start_info'])
            self.log_message(texts['log_privilege_info'])
        
        # Tab 1
        self.tab_garbage_widget.findChild(QGroupBox, "secure_group").setTitle(texts['secure_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_secure_delete").setText(texts['chk_secure_delete'])
        self.tab_garbage_widget.findChild(QLabel, "secure_delete_label").setText(texts['secure_delete_label'])
        self.tab_garbage_widget.findChild(QGroupBox, "trash_group").setTitle(texts['trash_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").setText(texts['chk_trash'])
        self.tab_garbage_widget.findChild(QGroupBox, "privacy_group").setTitle(texts['privacy_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").setText(texts['chk_recent_xbel'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").setText(texts['chk_recent_docs'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_db").setText(texts['chk_thumbs_db'])
        self.tab_garbage_widget.findChild(QGroupBox, "thumbnail_group").setTitle(texts['thumbnail_group'])
        self.tab_garbage_widget.findChild(QLabel, "thumbnail_warning").setText(texts['thumbnail_warning'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_large").setText(texts['chk_thumbs_large'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_normal").setText(texts['chk_thumbs_normal'])
        self.tab_garbage_widget.findChild(QPushButton, "btn_clean_selected").setText(texts['btn_clean_selected'])
        
        # Tab 2
        self.tab_apt_widget.findChild(QGroupBox, "apt_group").setTitle(texts['apt_group'])
        self.tab_apt_widget.findChild(QCheckBox, "chk_autoremove").setText(texts['chk_autoremove'])
        self.tab_apt_widget.findChild(QCheckBox, "chk_autoclean").setText(texts['chk_autoclean'])
        self.tab_apt_widget.findChild(QPushButton, "btn_apt_clean").setText(texts['btn_apt_clean'])
        
        # Tab 3
        self.tab_optimization_widget.findChild(QGroupBox, "defrag_group").setTitle(texts['defrag_group'])
        self.tab_optimization_widget.findChild(QLabel, "defrag_label").setText(texts['defrag_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_defrag").setText(texts['btn_defrag'])
        self.tab_optimization_widget.findChild(QGroupBox, "cpu_group").setTitle(texts['cpu_group'])
        self.tab_optimization_widget.findChild(QLabel, "cpu_label").setText(texts['cpu_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_apply").setText(texts['btn_cpupower_apply'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_restore").setText(texts['btn_cpupower_restore'])
        self.tab_optimization_widget.findChild(QGroupBox, "ram_group").setTitle(texts['ram_group'])
        self.tab_optimization_widget.findChild(QLabel, "ram_label").setText(texts['ram_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_ram_clean").setText(texts['btn_ram_clean'])

    def toggle_language(self):
        """Dili Türkçe ve İngilizce arasında değiştirir ve arayüzü günceller."""
        self.current_lang = 'tr' if self.current_lang == 'en' else 'en'
        self.update_ui_texts()
        self.log_message(f"Dili '{'Türkçe' if self.current_lang == 'tr' else 'English'}' olarak değiştirdiniz.")


    def log_message(self, message):
        """Günlük alanına mesaj ekler."""
        self.output_log.append(f"[{os.linesep}] {message}")

    def show_alert(self, title, message):
        """Özel bir uyarı kutusu gösterir (alert yerine)."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def show_about_dialog(self):
        """Hakkında penceresini (modal diyalog) gösterir."""
        texts = self.texts[self.current_lang]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(texts['about_title'])
        dialog.setMinimumWidth(400) # Hakkında penceresinin minimum genişliği
        dialog_layout = QVBoxLayout(dialog)
        
        # 1. Logo (68x68)
        logo_label = QLabel()
        if self.icon_path:
            icon_pixmap = QPixmap(self.icon_path)
            scaled_pixmap = icon_pixmap.scaled(68, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(logo_label)
        
        # 2. Başlık
        title_label = QLabel(f"<h1>{texts['about_title']}</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(title_label)
        
        # 3. Bilgiler
        info_text = f"""
        <p><b>{texts['about_version']}</b> 1.0.1</p>
        <p><b>{texts['about_license']}</b> GPLv3</p>
        <p><b>{texts['about_programming']}</b> A. Serhat KILIÇOĞLU</p>
        <p><b>Github:</b> <a href="https://www.github.com/shampuan">www.github.com/shampuan</a></p>
        <hr>
        <p>{texts['about_description']}</p>
        <p style='color: red; font-weight: bold;'>{texts['about_disclaimer']}</p>
        """
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True) # Github linkini açabilmek için
        info_label.setWordWrap(True) # <-- BU ÖNEMLİ: Metnin otomatik alt satıra geçmesini sağlar
        dialog_layout.addWidget(info_label)
        
        # 4. Tamam Butonu
        ok_button = QPushButton(texts['btn_ok'])
        ok_button.clicked.connect(dialog.accept)
        dialog_layout.addWidget(ok_button)
        
        dialog.exec()


    # --- Sekme Oluşturma Fonksiyonları ---

    def create_garbage_privacy_tab(self):
        """Çöp ve Gizlilik Temizliği sekmesini oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        scroll.setWidget(content_widget)
        
        # --- 1. Güvenli Silme Ayarları ---
        secure_group = QGroupBox()
        secure_group.setObjectName("secure_group")
        secure_layout = QVBoxLayout(secure_group)
        
        self.chk_secure_delete = QCheckBox()
        self.chk_secure_delete.setObjectName("chk_secure_delete")
        secure_layout.addWidget(self.chk_secure_delete)
        
        secure_delete_label = QLabel()
        secure_delete_label.setObjectName("secure_delete_label")
        secure_delete_label.setWordWrap(True)
        secure_layout.addWidget(secure_delete_label)
        content_layout.addWidget(secure_group)
        content_layout.addSpacing(15) 

        # --- 2. Çöp Kutusu Grubu (Sadece Geçerli Kullanıcı) ---
        trash_group = QGroupBox()
        trash_group.setObjectName("trash_group")
        trash_layout = QVBoxLayout(trash_group)
        self.chk_trash = QCheckBox()
        self.chk_trash.setObjectName("chk_trash")
        self.chk_trash.setChecked(True)
        trash_layout.addWidget(self.chk_trash)
        content_layout.addWidget(trash_group)
        content_layout.addSpacing(15)

        # --- 3. Özel Geçmiş Temizliği ---
        privacy_group = QGroupBox()
        privacy_group.setObjectName("privacy_group")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.chk_recent_xbel = QCheckBox()
        self.chk_recent_xbel.setObjectName("chk_recent_xbel")
        self.chk_recent_docs = QCheckBox()
        self.chk_recent_docs.setObjectName("chk_recent_docs")
        self.chk_thumbs_db = QCheckBox()
        self.chk_thumbs_db.setObjectName("chk_thumbs_db")
        
        self.chk_recent_xbel.setChecked(True)
        self.chk_recent_docs.setChecked(True)
        
        privacy_layout.addWidget(self.chk_recent_xbel)
        privacy_layout.addWidget(self.chk_recent_docs)
        privacy_layout.addWidget(self.chk_thumbs_db)
        content_layout.addWidget(privacy_group)
        content_layout.addSpacing(15)
        
        # --- 4. Thumbnail (Küçük Resim) Önbellek Temizliği ---
        thumbnail_group = QGroupBox()
        thumbnail_group.setObjectName("thumbnail_group")
        thumbnail_layout = QVBoxLayout(thumbnail_group)

        thumbnail_warning = QLabel()
        thumbnail_warning.setObjectName("thumbnail_warning")
        thumbnail_warning.setWordWrap(True)
        thumbnail_layout.addWidget(thumbnail_warning)

        self.chk_thumbs_large = QCheckBox()
        self.chk_thumbs_large.setObjectName("chk_thumbs_large")
        self.chk_thumbs_normal = QCheckBox()
        self.chk_thumbs_normal.setObjectName("chk_thumbs_normal")
        
        thumbnail_layout.addWidget(self.chk_thumbs_large)
        thumbnail_layout.addWidget(self.chk_thumbs_normal)
        content_layout.addWidget(thumbnail_group)


        # Temizle Butonu
        clean_button = QPushButton()
        clean_button.setObjectName("btn_clean_selected")
        clean_button.clicked.connect(self.run_garbage_privacy_cleanup)
        layout.addWidget(scroll)
        layout.addWidget(clean_button)
        layout.addStretch(1) 

        return tab

    def create_apt_tab(self):
        """APT Temizliği sekmesini oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        apt_group = QGroupBox()
        apt_group.setObjectName("apt_group")
        apt_layout = QVBoxLayout(apt_group)
        
        self.chk_autoremove = QCheckBox()
        self.chk_autoremove.setObjectName("chk_autoremove")
        self.chk_autoclean = QCheckBox()
        self.chk_autoclean.setObjectName("chk_autoclean")
        
        self.chk_autoremove.setChecked(True)
        self.chk_autoclean.setChecked(True)
        
        apt_layout.addWidget(self.chk_autoremove)
        apt_layout.addWidget(self.chk_autoclean)
        layout.addWidget(apt_group)
        
        clean_button = QPushButton()
        clean_button.setObjectName("btn_apt_clean")
        clean_button.clicked.connect(self.run_apt_cleanup)
        layout.addWidget(clean_button)
        layout.addStretch(1)

        return tab

    def create_system_optimization_tab(self):
        """Sistem Optimizasyonu sekmesini oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Disk Birleştirme Grubu
        defrag_group = QGroupBox()
        defrag_group.setObjectName("defrag_group")
        defrag_layout = QVBoxLayout(defrag_group)
        
        defrag_label = QLabel()
        defrag_label.setObjectName("defrag_label")
        defrag_label.setWordWrap(True)
        defrag_layout.addWidget(defrag_label)
        
        btn_defrag = QPushButton()
        btn_defrag.setObjectName("btn_defrag")
        btn_defrag.clicked.connect(self.run_defrag)
        defrag_layout.addWidget(btn_defrag)
        layout.addWidget(defrag_group)
        
        # CPU Kontrol Grubu
        cpu_group = QGroupBox()
        cpu_group.setObjectName("cpu_group")
        cpu_layout = QVBoxLayout(cpu_group)
        
        cpu_label = QLabel()
        cpu_label.setObjectName("cpu_label")
        cpu_label.setWordWrap(True)
        cpu_layout.addWidget(cpu_label)
        
        cpu_button_layout = QHBoxLayout()
        
        btn_cpupower_apply = QPushButton()
        btn_cpupower_apply.setObjectName("btn_cpupower_apply")
        btn_cpupower_apply.clicked.connect(lambda: self.run_cpupower("powersave", "CPU Optimizasyonu (%75)"))
        cpu_button_layout.addWidget(btn_cpupower_apply)
        
        btn_cpupower_restore = QPushButton()
        btn_cpupower_restore.setObjectName("btn_cpupower_restore")
        btn_cpupower_restore.clicked.connect(lambda: self.run_cpupower("performance", "CPU Optimizasyonu Geri Alma (%100)"))
        cpu_button_layout.addWidget(btn_cpupower_restore)
        
        cpu_layout.addLayout(cpu_button_layout)
        layout.addWidget(cpu_group)
        
        # RAM Temizliği Grubu
        ram_group = QGroupBox()
        ram_group.setObjectName("ram_group")
        ram_layout = QVBoxLayout(ram_group)
        
        ram_label = QLabel()
        ram_label.setObjectName("ram_label")
        ram_label.setWordWrap(True)
        ram_layout.addWidget(ram_label)
        
        btn_ram_clean = QPushButton()
        btn_ram_clean.setObjectName("btn_ram_clean")
        btn_ram_clean.clicked.connect(self.run_ram_cleanup)
        ram_layout.addWidget(btn_ram_clean)
        layout.addWidget(ram_group)
        
        layout.addStretch(1)
        return tab

    # --- İşlem Yürütme Fonksiyonları ---
    
    def run_garbage_privacy_cleanup(self):
        """Çöp ve Gizlilik temizleme işlemlerini sırayla yürütür."""
        is_secure = self.chk_secure_delete.isChecked()
        self.log_message(f"\n--- Temizlik Başlatılıyor (Güvenli Silme: {'Aktif' if is_secure else 'Pasif'}) ---")
        
        cleaned_count = 0

        # 1. Çöp Kutusu Temizliği (Sadece Geçerli Kullanıcı)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").isChecked():
            self.log_message("Geçerli kullanıcının çöp kutusu boşaltılıyor...")
            
            try:
                trash_path = os.path.expanduser("~/.local/share/Trash/files")
                if not os.path.exists(trash_path):
                     self.log_message("ℹ️ Çöp kutusu dizini bulunamadı, atlanıyor.")
                else:
                    for item in os.listdir(trash_path):
                        full_path = os.path.join(trash_path, item)
                        
                        if os.path.isdir(full_path) and not os.path.islink(full_path):
                            subprocess.run(["rm", "-rf", full_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif os.path.isfile(full_path) or os.path.islink(full_path):
                            if is_secure:
                                self.secure_delete_file(full_path)
                            else:
                                os.remove(full_path)
                        cleaned_count += 1
                    self.log_message(f"✅ Geçerli kullanıcının çöp kutusu başarıyla temizlendi. ({cleaned_count} öğe)")
            except Exception as e:
                self.log_message(f"❌ Çöp kutusu temizlenirken hata oluştu: {e}")

        # 2. Özel Geçmiş Temizliği
        home = os.path.expanduser("~")
        
        # .xbel
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").isChecked():
            self.log_message("Son kullanılanlar (.xbel) temizleniyor...")
            if is_secure:
                self.secure_delete_file(os.path.join(home, ".local/share/recently-used.xbel"))
            else:
                self.clean_file(os.path.join(home, ".local/share/recently-used.xbel"))

        # RecentDocuments
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").isChecked():
            self.log_message("Son kullanılan belgeler klasör içeriği temizleniyor...")
            self.clean_directory_contents(os.path.join(home, ".local/share/RecentDocuments"), is_secure=is_secure)

        # thumbs.db (Home dizini içi)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_db").isChecked():
            self.log_message("Home dizinindeki thumbs.db dosyaları aranıyor...")
            try:
                deleted_count = 0
                for root, _, files in os.walk(home):
                    for file in files:
                        if file.lower() == "thumbs.db":
                            full_path = os.path.join(root, file)
                            if is_secure:
                                self.secure_delete_file(full_path)
                            else:
                                os.remove(full_path)
                            deleted_count += 1
                            self.log_message(f"Silindi: {full_path}")
                self.log_message(f"✅ thumbs.db temizliği tamamlandı. ({deleted_count} dosya)")
            except Exception as e:
                self.log_message(f"❌ thumbs.db temizlenirken hata oluştu: {e}")

        # 3. Küçük Resim (Thumbnail) Önbelleği
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_large").isChecked():
            self.log_message(".cache/thumbnails/large temizleniyor...")
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/large"), is_secure=is_secure)

        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_normal").isChecked():
            self.log_message(".cache/thumbnails/normal temizleniyor...")
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/normal"), is_secure=is_secure)

        self.log_message("\n--- Temizlik İşlemi Tamamlandı ---")

    def secure_delete_file(self, filepath):
        """Dosyayı shred ile güvenli bir şekilde siler (3 geçiş)."""
        if os.path.exists(filepath):
            try:
                # -f: force, -u: remove after overwriting, -n 3: 3 passes (default)
                subprocess.run(["shred", "-f", "-u", filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message(f"✅ Güvenli Silme başarılı: {filepath}")
            except subprocess.CalledProcessError as e:
                self.log_message(f"❌ Güvenli Silme hatası oluştu ({filepath}): {e}")
            except FileNotFoundError:
                self.log_message(f"❌ Hata: 'shred' aracı bulunamadı. Normal silme yapılıyor. ({filepath})")
                self.clean_file(filepath)
            except Exception as e:
                self.log_message(f"❌ Güvenli Silme sırasında bilinmeyen hata: {e}")
        else:
            self.log_message(f"ℹ️ Güvenli Silme: Dosya bulunamadı: {filepath}")


    def clean_file(self, filepath):
        """Belirtilen dosyayı normal şekilde siler ve günlük kaydı tutar."""
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self.log_message(f"✅ Dosya silindi: {filepath}")
            except Exception as e:
                self.log_message(f"❌ Dosya silinirken hata oluştu ({filepath}): {e}")
        else:
            self.log_message(f"ℹ️ Dosya bulunamadı: {filepath}")

    def clean_directory_contents(self, dirpath, is_secure=False):
        """Belirtilen dizinin içeriğini siler (dizini silmez)."""
        if os.path.isdir(dirpath):
            try:
                count = 0
                for item in os.listdir(dirpath):
                    full_path = os.path.join(dirpath, item)
                    
                    if os.path.isdir(full_path) and not os.path.islink(full_path):
                        subprocess.run(["rm", "-rf", full_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        if is_secure:
                            self.secure_delete_file(full_path)
                        else:
                            os.remove(full_path)
                            
                    count += 1
                self.log_message(f"✅ Dizin içeriği temizlendi: {dirpath} ({count} öğe)")
            except Exception as e:
                self.log_message(f"❌ Dizin içeriği temizlenirken hata oluştu ({dirpath}): {e}")
        else:
            self.log_message(f"ℹ️ Dizin bulunamadı: {dirpath}")
            
    # --- APT Temizliği ---

    def run_apt_cleanup(self):
        """APT temizlik komutlarını QProcess ile pkexec kullanarak yürütür."""
        chk_autoremove = self.tab_apt_widget.findChild(QCheckBox, "chk_autoremove").isChecked()
        chk_autoclean = self.tab_apt_widget.findChild(QCheckBox, "chk_autoclean").isChecked()

        if not (chk_autoremove or chk_autoclean):
            self.show_alert("Seçim Yok", "Lütfen en az bir APT temizlik seçeneği işaretleyiniz.")
            return

        self.log_message("\n--- APT Temizliği Başlatılıyor (pkexec Gerekir) ---")

        if chk_autoremove:
            self.execute_command_with_pkexec("/usr/bin/apt autoremove -y", "APT Autoremove")

        if chk_autoclean:
            self.execute_command_with_pkexec("/usr/bin/apt autoclean", "APT Autoclean")

    # --- Disk Birleştirme (Defrag) ---

    def run_defrag(self):
        """u4defrag komutunu QProcess ile pkexec kullanarak yürütür."""
        self.log_message("\n--- Disk Birleştirme Başlatılıyor (pkexec Gerekir) ---")
        self.execute_command_with_pkexec("/usr/bin/u4defrag -s /", "Disk Birleştirme")

    # --- CPU Optimizasyonu (Apply ve Restore) ---

    def run_cpupower(self, governor, task_name):
        """cpupower komutunu QProcess ile pkexec kullanarak yürütür (powersave veya performance)."""
        if governor == "powersave":
            self.log_message("\n--- CPU Optimizasyonu Uygulanıyor (Powersave - %75) ---")
        elif governor == "performance":
             self.log_message("\n--- CPU Optimizasyonu Geri Alınıyor (Performance - %100) ---")
             
        command = f"/usr/bin/cpupower frequency-set -g {governor}"
        self.execute_command_with_pkexec(command, task_name)


    # --- RAM Temizliği ---

    def run_ram_cleanup(self):
        """RAM önbelleği temizleme komutunu QProcess ile pkexec kullanarak yürütür."""
        command = 'sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"'
        self.log_message("\n--- RAM ÖnBellek Temizliği Başlatılıyor (pkexec Gerekir) ---")
        self.execute_command_with_pkexec(command, "RAM ÖnBellek Temizliği")


    # --- QProcess Ortak Yürütme Fonksiyonu (PKEXEC) ---

    def execute_command_with_pkexec(self, command, task_name):
        """QProcess kullanarak pkexec ile bir komutu yürütür."""
        
        if self.process and self.process.state() == QProcess.Running:
            self.show_alert(self.texts[self.current_lang].get('error_title', "Error"), 
                            self.texts[self.current_lang].get('error_busy', "Please wait for the current process to complete."))
            return

        if " " in command and not command.startswith("sh -c"):
            escaped_command = command.replace('"', '\\"')
            full_command = 'pkexec sh -c "{}"'.format(escaped_command)
        else:
            full_command = f'pkexec {command}'

        self.process = QProcess()
        
        # Sinyal bağlantıları
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(lambda exitCode, exitStatus: self.handle_finished(exitCode, exitStatus, task_name))
        
        self.log_message(f"Başlatılıyor (pkexec): '{full_command}'")
        
        self.process.start("/bin/bash", ["-c", full_command])

    def handle_stdout(self):
        """Komutun standart çıktısını (stdout) okur ve günlüğe yazar."""
        data = self.process.readAllStandardOutput().data().decode().strip()
        if data:
            self.output_log.append(f"Çıktı: {data}")

    def handle_stderr(self):
        """Komutun standart hata çıktısını (stderr) okur ve günlüğe yazar."""
        data = self.process.readAllStandardError().data().decode().strip()
        if data:
            self.output_log.append(f"HATA: {data}")
            
    def handle_finished(self, exitCode, exitStatus, task_name):
        """Komutun tamamlanmasını işler."""
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            self.log_message(f"✅ {task_name} işlemi başarıyla tamamlandı (Çıkış Kodu: {exitCode})")
        else:
            self.log_message(f"❌ {task_name} işlemi HATA ile tamamlandı (Çıkış Kodu: {exitCode}, Durum: {exitStatus}). Lütfen yetkinizi kontrol edin.")

# --- Uygulama Başlatma ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinuxCleanerApp()
    window.show()
    sys.exit(app.exec())

