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
        
        # Sürüm numarasını tanımla
        self.VERSION = "1.3.1" # Sürüm Güncellendi

        # Dil ayarları ve metin sözlüğü
        self.texts = self._load_localization()
        self.current_lang = 'en' # Varsayılan dil: İngilizce (en)
        
        self.setGeometry(100, 100, 800, 800) 
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
                'window_title': f"System Maid - Linux Cleaner & Optimizer (v{self.VERSION})",
                'header_title': "System Maid",
                'log_group': "Operation Log and Results",
                'log_start_info': "Application started. Please select cleaning and optimization options.",
                'log_privilege_info': "Privilege Requirement: APT, Defrag, CPU, RAM, and Swap operations will use pkexec (Root Privilege).",
                
                # Tab 1: Garbage & Privacy
                'tab_garbage': "Junk & Privacy Cleanup",
                'secure_group': "Secure Deletion Settings",
                'chk_secure_delete': "Activate Secure Deletion (shred)",
                'secure_delete_label': "This option prevents attackers from recovering deleted data using random data overwriting (shred).",
                'trash_group': "Trash Cleanup",
                'chk_trash': "Empty Current User's Trash Bin",
                'privacy_group': "Specific History Cleanup",
                'chk_recent_xbel': "Clean Recently Used (.xbel) file",
                'chk_recent_docs': "Clean Recently Used Documents folder content",
                'chk_recent_history': "Clean General Recent File History", 
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
                'ram_swap_group': "RAM and Swap Management (Privilege Required)", 
                'ram_label': "This process increases available RAM by freeing up data held in the system cache. It is not true memory release and may cause the system to slow down briefly.",
                'btn_ram_clean': "Clean RAM Caches",
                'swap_label': "This process clears the Swap Area (virtual memory on disk) to prevent sensitive data from remaining after use.", 
                'btn_swap_clean': "Clear Swap Area", 
                'cpu_group': "CPU & Swappiness Control (Privilege Required)",
                'cpu_label': "This process changes the CPU Governor to 'powersave'. This maximizes battery life and reduces heat, but system speed will noticeably decrease. Use this if you need energy saving.",
                'btn_cpupower_apply': "Apply Power Save Mode", 
                'btn_cpupower_restore': "Restore Performance Mode", 
                'swappiness_label': "Sets the kernel's tendency to use swap memory. Low values (e.g., 10) are better for systems with plenty of RAM. (Default is often 60).", 
                'btn_swappiness_apply': "Apply Swappiness (Set to 10)", 
                'btn_swappiness_restore': "Restore Swappiness (Set to 60)",
                
                # About Dialog
                'about_title': "About System Maid",
                'about_version': "Version:",
                'about_license': "License:",
                'about_programming': "Programming:",
                'about_description': "This program helps your computer run healthier by performing system cleaning and performance adjustments, while protecting your privacy from attackers.",
                'about_disclaimer': "This program comes with no warranty.",
                'btn_ok': "OK",
                'error_no_apt_selection': "Please select at least one APT cleaning option.",
                'error_busy': "Please wait for the current process to complete.",
                
                # Language names (NEW)
                'lang_tr_name': 'Turkish',
                'lang_en_name': 'English',

                # LOG MESSAGES (NEW)
                'log_messages': {
                    'cleaning_start': "--- Cleaning Started (Secure Deletion: {secure_status}) ---",
                    'secure_status_active': "Active",
                    'secure_status_inactive': "Inactive",
                    'trash_start': "Emptying current user's trash bin...",
                    'trash_success': "✅ Current user's trash bin successfully emptied. ({count} items)",
                    'trash_not_found': "ℹ️ Trash directory not found, skipping.",
                    'trash_error': "❌ Error occurred while cleaning trash: {error}",
                    'file_deleted': "✅ File deleted: {filepath}",
                    'file_error': "❌ Error occurred while deleting file ({filepath}): {error}",
                    'file_not_found': "ℹ️ File not found: {filepath}",
                    'dir_content_success': "✅ Directory contents cleaned: {dirpath} ({count} items)",
                    'dir_content_error': "❌ Error occurred while cleaning directory contents ({dirpath}): {error}",
                    'recent_xbel': "Cleaning Recently Used (.xbel) file...",
                    'recent_docs': "Cleaning Recently Used Documents folder contents...",
                    'recent_history': "Cleaning General Recent File History (GTK/Zeitgeist)...",
                    'thumbs_db_start': "Searching for thumbs.db files in Home directory...",
                    'thumbs_db_success': "✅ thumbs.db cleanup completed. ({count} files)",
                    'thumbs_db_error': "❌ Error occurred while cleaning thumbs.db: {error}",
                    'thumbs_large': "Cleaning .cache/thumbnails/large...",
                    'thumbs_normal': "Cleaning .cache/thumbnails/normal...",
                    'cleaning_end': "--- Cleaning Process Completed ---",
                    'secure_success': "✅ Secure Deletion successful: {filepath}",
                    'secure_error_shred': "❌ Secure Deletion error occurred ({filepath}): {error}",
                    'secure_not_found': "❌ Error: 'shred' tool not found. Performing normal deletion. ({filepath})",
                    'secure_unknown_error': "❌ Unknown error during Secure Deletion: {error}",
                    'starting_pkexec': "Starting (pkexec): '{command}'",
                    'process_success': "✅ {task_name} process completed successfully (Exit Code: {exitCode})",
                    'process_error': "❌ {task_name} process failed with ERROR (Exit Code: {exitCode}, Status: {exitStatus}). Please check your permissions.",
                    'apt_start': "--- APT Cleanup Started (pkexec Required) ---",
                    'defrag_start': "--- Disk Defragmentation Started (pkexec Required) ---",
                    'ram_start': "--- RAM Cache Cleanup Started (pkexec Required) ---",
                    'swap_start': "--- Swap Area (Swap) Cleanup Started (pkexec Required) ---",
                    'cpu_apply_start': "--- Applying CPU Optimization (powersave) ---",
                    'cpu_restore_start': "--- Restoring CPU Optimization (performance) ---",
                    'swappiness_start': "--- Applying Swappiness Setting (Value: {value}) ---",
                    'language_changed': "Language changed to '{language}'.", # YENİ ŞABLON
                }
            },
            'tr': {
                'window_title': f"System Maid - Linux Temizleyici ve Optimizasyon Aracı (v{self.VERSION})",
                'header_title': "System Maid",
                'log_group': "İşlem Günlüğü ve Sonuçlar",
                'log_start_info': "Uygulama başlatıldı. Lütfen temizlik ve optimizasyon seçeneklerini seçiniz.",
                'log_privilege_info': "Yetki Gereksinimi: APT, Defrag, CPU, RAM ve Takas Alanı işlemleri için pkexec (Root Yetkisi) kullanılacaktır.",
                
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
                'chk_recent_history': "Genel Son Kullanılan Dosya Geçmişini Temizle", 
                'chk_thumbs_db': "Linux/Windows Paylaşımlarından Kalan thumbs.db dosyalarını sil",
                'thumbnail_group': "Küçük Resim Önbelleği Temizliği",
                'thumbnail_warning': "Küçük resimler, resim ve video gibi dosyalarınızın dosya yöneticinizde içeriklerini size küçük resim olarak gösteren küçük dosyalardır. Bu dosyaları silmeniz gerekmez. Onları silmeniz durumunda sisteminiz onları yeniden oluşturacak, bu da içi resim ve/veya video dolu bir klasörü açtığınızda içeriğin yüklenmesini yavaşlatacaktır. Ayrıca küçük resimler, bilgisayarınıza fiziksel erişimi olan saldırganların bilgisayarınızda neler tuttuğuna dair fikir edinmelerine neden olur. Bu yüzden onları da silmek isteyebilirsiniz.",
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
                'ram_swap_group': "RAM ve Takas Alanı Yönetimi (Yetki Gereklidir)", 
                'ram_label': "Bu işlem, sistemin önbellekte tuttuğu verileri serbest bırakarak kullanılabilir RAM miktarını artırır. Gerçek bellek boşaltımı değildir ve sistemin kısa bir süre için yavaşlamasına neden olabilir.",
                'btn_ram_clean': "RAM ÖnBelleklerini Temizle",
                'swap_label': "Bu işlem, hassas verilerin kullanım sonrası bellekte kalmasını engellemek için Takas Alanını (diskteki sanal bellek) temizler ve yeniden etkinleştirir.", 
                'btn_swap_clean': "Takas Alanını Temizle", 
                'cpu_group': "CPU ve Swappiness Kontrolü (Yetki Gereklidir)",
                'cpu_label': "Bu işlem, CPU Yöneticisini 'powersave' moduna geçirir. Bu, pil ömrünü uzatır ve ısınmayı azaltır, ancak sistem hızı belirgin şekilde düşecektir. Enerji tasarrufuna ihtiyacınız varsa kullanın.", 
                'btn_cpupower_apply': "Güç Tasarrufu Modunu Uygula", 
                'btn_cpupower_restore': "Performans Moduna Geri Dön", 
                'swappiness_label': "Kernel'ın takas belleği kullanma eğilimini ayarlar. Düşük değerler (örneğin 10) bol RAM'e sahip sistemler için daha iyidir. (Varsayılan genellikle 60'tır).", 
                'btn_swappiness_apply': "Swappiness Uygula (10 Yap)", 
                'btn_swappiness_restore': "Swappiness Geri Al (60 Yap)", 
                
                # Hakkında Diyalogu
                'about_title': "System Maid Hakkında",
                'about_version': "Sürüm:",
                'about_license': "Lisans:",
                'about_programming': "Programlama:",
                'about_description': "Bu program, sistem temizliği ve performans ayarları yaparak bilgisayarınızın daha sağlıklı çalışmasına yardımcı olurken, özel hayatınızı saldırganlardan korumanıza yardımcı olur.",
                'about_disclaimer': "Bu program hiçbir garanti getirmez.",
                'btn_ok': "Tamam",
                'error_no_apt_selection': "Lütfen en az bir APT temizlik seçeneği işaretleyiniz.",
                'error_busy': "Lütfen mevcut işlemin tamamlanmasını bekleyin.",
                
                # Language names (NEW)
                'lang_tr_name': 'Türkçe',
                'lang_en_name': 'İngilizce',

                # LOG MESSAGES (NEW)
                'log_messages': {
                    'cleaning_start': "--- Temizlik Başlatılıyor (Güvenli Silme: {secure_status}) ---",
                    'secure_status_active': "Aktif",
                    'secure_status_inactive': "Pasif",
                    'trash_start': "Geçerli kullanıcının çöp kutusu boşaltılıyor...",
                    'trash_success': "✅ Geçerli kullanıcının çöp kutusu başarıyla temizlendi. ({count} öğe)",
                    'trash_not_found': "ℹ️ Çöp kutusu dizini bulunamadı, atlanıyor.",
                    'trash_error': "❌ Çöp kutusu temizlenirken hata oluştu: {error}",
                    'file_deleted': "✅ Dosya silindi: {filepath}",
                    'file_error': "❌ Dosya silinirken hata oluştu ({filepath}): {error}",
                    'file_not_found': "ℹ️ Dosya bulunamadı: {filepath}",
                    'dir_content_success': "✅ Dizin içeriği temizlendi: {dirpath} ({count} öğe)",
                    'dir_content_error': "❌ Dizin içeriği temizlenirken hata oluştu ({dirpath}): {error}",
                    'recent_xbel': "Son kullanılanlar (.xbel) temizleniyor...",
                    'recent_docs': "Son kullanılan belgeler klasör içeriği temizleniyor...",
                    'recent_history': "Genel son kullanılan dosya geçmişi (GTK/Zeitgeist) temizleniyor...",
                    'thumbs_db_start': "Home dizinindeki thumbs.db dosyaları aranıyor...",
                    'thumbs_db_success': "✅ thumbs.db temizliği tamamlandı. ({count} dosya)",
                    'thumbs_db_error': "❌ thumbs.db temizlenirken hata oluştu: {error}",
                    'thumbs_large': ".cache/thumbnails/large temizleniyor...",
                    'thumbs_normal': ".cache/thumbnails/normal temizleniyor...",
                    'cleaning_end': "--- Temizlik İşlemi Tamamlandı ---",
                    'secure_success': "✅ Güvenli Silme başarılı: {filepath}",
                    'secure_error_shred': "❌ Güvenli Silme hatası oluştu ({filepath}): {error}",
                    'secure_not_found': "❌ Hata: 'shred' aracı bulunamadı. Normal silme yapılıyor. ({filepath})",
                    'secure_unknown_error': "❌ Güvenli Silme sırasında bilinmeyen hata: {error}",
                    'starting_pkexec': "Başlatılıyor (pkexec): '{command}'",
                    'process_success': "✅ {task_name} işlemi başarıyla tamamlandı (Çıkış Kodu: {exitCode})",
                    'process_error': "❌ {task_name} işlemi HATA ile tamamlandı (Çıkış Kodu: {exitCode}, Durum: {exitStatus}). Lütfen yetkinizi kontrol edin.",
                    'apt_start': "--- APT Temizliği Başlatılıyor (pkexec Gerekir) ---",
                    'defrag_start': "--- Disk Birleştirme Başlatılıyor (pkexec Gerekir) ---",
                    'ram_start': "--- RAM ÖnBellek Temizliği Başlatılıyor (pkexec Gerekir) ---",
                    'swap_start': "--- Takas Alanı (Swap) Temizliği Başlatılıyor (pkexec Gerekir) ---",
                    'cpu_apply_start': "--- CPU Optimizasyonu Uygulanıyor (powersave) ---",
                    'cpu_restore_start': "--- CPU Optimizasyonu Geri Alınıyor (performance) ---",
                    'swappiness_start': "--- Swappiness Ayarı Uygulanıyor (Değer: {value}) ---",
                    'language_changed': "Dil, '{language}' olarak değiştirildi.", # YENİ ŞABLON
                }
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
        
        return None

    def setup_ui(self):
        """Kullanıcı arayüzünü (UI) hazırlar."""
        
        # --- Stil Tanımlamaları (CSS-Benzeri PySide6 Stylesheet) ---

        # 1. Genel Temizleme/Başlatma Butonları (Yeşil)
        self.style_primary_clean = """
            QPushButton {
                background-color: #4CAF50; /* Yeşil */
                color: white;
                border: 2px solid #388E3C;
                border-radius: 8px;
                padding: 8px 20px; 
                font-weight: bold;
                font-size: 10pt; 
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """
        
        # 2. Uygula (Apply) Butonları (Mavi)
        self.style_apply_action = """
            QPushButton {
                background-color: #2196F3; /* Mavi */
                color: white;
                border: 2px solid #1976D2;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """

        # 3. Geri Al (Restore) Butonları (Turuncu)
        self.style_restore_action = """
            QPushButton {
                background-color: #FF9800; /* Turuncu */
                color: white;
                border: 2px solid #FB8C00;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold; 
            }
            QPushButton:hover {
                background-color: #FFB74D;
            }
            QPushButton:pressed {
                background-color: #FB8C00;
            }
        """
        
        # 4. Yardımcı/Hakkında/Dil Butonları (Mavi Gri - Daha sade)
        self.style_utility = """
            QPushButton {
                background-color: #607D8B; /* Mavi Gri */
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #78909C;
            }
        """
        
        # Ana Konteyner ve Düzen
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # --- Üst Başlık ve Butonlar Alanı ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10) 
        
        # İkon Resim Nesnesi
        self.icon_label = QLabel()
        if self.icon_path:
            icon_pixmap = QPixmap(self.icon_path)
            scaled_pixmap = icon_pixmap.scaled(68, 68, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(self.icon_label)
        
        # Başlık Yazısı
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch(1) 
        
        # Hakkında Butonu
        self.btn_about = QPushButton()
        self.btn_about.setStyleSheet(self.style_utility) 
        self.btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.btn_about)
        
        # Dil Değiştirme Butonu (Evrensel: "Language")
        self.btn_lang = QPushButton("Language")
        self.btn_lang.setStyleSheet(self.style_utility) 
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        
        main_layout.addWidget(header_widget)
        
        # Sekmeli Alan (Temizlik Görevleri)
        self.tab_widget = QTabWidget()
        
        # Sekme Widget'larını ve düzenlerini tanımla
        self.tab_garbage_widget = self.create_garbage_privacy_tab()
        self.tab_apt_widget = self.create_apt_tab()
        self.tab_optimization_widget = self.create_system_optimization_tab()
        
        self.tab_widget.addTab(self.tab_garbage_widget, "")
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
        self.btn_about.setText(texts['about_title'])
        
        # Sekme Başlıkları
        self.tab_widget.setTabText(0, texts['tab_garbage'])
        self.tab_widget.setTabText(1, texts['tab_apt'])
        self.tab_widget.setTabText(2, texts['tab_optimization'])
        
        # Log mesajları (Sadece bir kez eklenir)
        if self.output_log.toPlainText() == "":
            self.log_message(texts['log_start_info'])
            self.log_message(texts['log_privilege_info'])
        
        # Tab 1: Çöp ve Gizlilik
        self.tab_garbage_widget.findChild(QGroupBox, "secure_group").setTitle(texts['secure_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_secure_delete").setText(texts['chk_secure_delete'])
        self.tab_garbage_widget.findChild(QLabel, "secure_delete_label").setText(texts['secure_delete_label'])
        
        self.tab_garbage_widget.findChild(QGroupBox, "trash_group").setTitle(texts['trash_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").setText(texts['chk_trash'])
        
        self.tab_garbage_widget.findChild(QGroupBox, "privacy_group").setTitle(texts['privacy_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").setText(texts['chk_recent_xbel'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").setText(texts['chk_recent_docs'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_history").setText(texts['chk_recent_history'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_db").setText(texts['chk_thumbs_db'])

        self.tab_garbage_widget.findChild(QGroupBox, "thumbnail_group").setTitle(texts['thumbnail_group'])
        self.tab_garbage_widget.findChild(QLabel, "thumbnail_warning").setText(texts['thumbnail_warning'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_large").setText(texts['chk_thumbs_large'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_normal").setText(texts['chk_thumbs_normal'])
        self.tab_garbage_widget.findChild(QPushButton, "btn_clean_selected").setText(texts['btn_clean_selected'])
        
        # Tab 2: APT
        self.tab_apt_widget.findChild(QGroupBox, "apt_group").setTitle(texts['apt_group'])
        self.tab_apt_widget.findChild(QCheckBox, "chk_autoremove").setText(texts['chk_autoremove'])
        self.tab_apt_widget.findChild(QCheckBox, "chk_autoclean").setText(texts['chk_autoclean'])
        self.tab_apt_widget.findChild(QPushButton, "btn_apt_clean").setText(texts['btn_apt_clean'])
        
        # Tab 3: Optimizasyon
        self.tab_optimization_widget.findChild(QGroupBox, "defrag_group").setTitle(texts['defrag_group'])
        self.tab_optimization_widget.findChild(QLabel, "defrag_label").setText(texts['defrag_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_defrag").setText(texts['btn_defrag'])
        
        self.tab_optimization_widget.findChild(QGroupBox, "ram_swap_group").setTitle(texts['ram_swap_group'])
        self.tab_optimization_widget.findChild(QLabel, "ram_label").setText(texts['ram_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_ram_clean").setText(texts['btn_ram_clean'])
        self.tab_optimization_widget.findChild(QLabel, "swap_label").setText(texts['swap_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_swap_clean").setText(texts['btn_swap_clean'])
        
        self.tab_optimization_widget.findChild(QGroupBox, "cpu_group").setTitle(texts['cpu_group'])
        self.tab_optimization_widget.findChild(QLabel, "cpu_label").setText(texts['cpu_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_apply").setText(texts['btn_cpupower_apply'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_restore").setText(texts['btn_cpupower_restore'])
        self.tab_optimization_widget.findChild(QLabel, "swappiness_label").setText(texts['swappiness_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_swappiness_apply").setText(texts['btn_swappiness_apply'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_swappiness_restore").setText(texts['btn_swappiness_restore'])

    def toggle_language(self):
        """Dili Türkçe ve İngilizce arasında değiştirir ve arayüzü günceller."""
        
        # 1. Yeni dili belirle
        old_lang = self.current_lang
        self.current_lang = 'tr' if old_lang == 'en' else 'en'
        new_lang = self.current_lang
        
        # 2. UI metinlerini yeni dile güncelle
        self.update_ui_texts() 

        # 3. Yeni dilin metinlerini al
        texts_new = self.texts[new_lang] 
        
        # 4. Aktifleşen dilin adını, aktif dildeki karşılığıyla bul
        reported_lang_key = 'lang_tr_name' if new_lang == 'tr' else 'lang_en_name'
        reported_lang_name = texts_new[reported_lang_key]

        # 5. Yerelleştirilmiş mesajı log'la
        log_message = texts_new['log_messages']['language_changed'].format(language=reported_lang_name)
        self.log_message(log_message)


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
        dialog.setMinimumWidth(400) 
        dialog_layout = QVBoxLayout(dialog)
        
        # 1. Logo
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
        <p><b>{texts['about_version']}</b> {self.VERSION}</p>
        <p><b>{texts['about_license']}</b> GPLv3</p>
        <p><b>{texts['about_programming']}</b> A. Serhat KILIÇOĞLU</p>
        <p><b>Github:</b> <a href="https://www.github.com/shampuan">www.github.com/shampuan</a></p>
        <hr>
        <p>{texts['about_description']}</p>
        <p style='color: red; font-weight: bold;'>{texts['about_disclaimer']}</p>
        """
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True) 
        dialog_layout.addWidget(info_label)
        
        # 4. Tamam Butonu
        ok_button = QPushButton(texts['btn_ok'])
        ok_button.setStyleSheet(self.style_utility)
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
        self.chk_recent_history = QCheckBox()
        self.chk_recent_history.setObjectName("chk_recent_history")
        self.chk_thumbs_db = QCheckBox()
        self.chk_thumbs_db.setObjectName("chk_thumbs_db")
        
        self.chk_recent_xbel.setChecked(True)
        self.chk_recent_docs.setChecked(True)
        self.chk_recent_history.setChecked(True)
        
        privacy_layout.addWidget(self.chk_recent_xbel)
        privacy_layout.addWidget(self.chk_recent_docs)
        privacy_layout.addWidget(self.chk_recent_history)
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
        clean_button.setStyleSheet(self.style_primary_clean)
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
        clean_button.setStyleSheet(self.style_primary_clean)
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
        btn_defrag.setStyleSheet(self.style_primary_clean)
        btn_defrag.clicked.connect(self.run_defrag)
        defrag_layout.addWidget(btn_defrag)
        layout.addWidget(defrag_group)
        
        # RAM ve SWAP Yönetimi Grubu
        ram_swap_group = QGroupBox()
        ram_swap_group.setObjectName("ram_swap_group")
        ram_swap_layout = QVBoxLayout(ram_swap_group)
        
        # RAM Temizliği
        ram_label = QLabel()
        ram_label.setObjectName("ram_label")
        ram_label.setWordWrap(True)
        ram_swap_layout.addWidget(ram_label)
        btn_ram_clean = QPushButton()
        btn_ram_clean.setObjectName("btn_ram_clean")
        btn_ram_clean.setStyleSheet(self.style_primary_clean)
        btn_ram_clean.clicked.connect(self.run_ram_cleanup)
        ram_swap_layout.addWidget(btn_ram_clean)
        
        # SWAP Temizliği
        swap_label = QLabel()
        swap_label.setObjectName("swap_label")
        swap_label.setWordWrap(True)
        ram_swap_layout.addWidget(swap_label)
        btn_swap_clean = QPushButton()
        btn_swap_clean.setObjectName("btn_swap_clean")
        btn_swap_clean.setStyleSheet(self.style_primary_clean)
        btn_swap_clean.clicked.connect(self.run_swap_cleanup) 
        ram_swap_layout.addWidget(btn_swap_clean)
        
        layout.addWidget(ram_swap_group)
        
        # CPU ve Swappiness Kontrol Grubu
        cpu_group = QGroupBox()
        cpu_group.setObjectName("cpu_group")
        cpu_layout = QVBoxLayout(cpu_group)
        
        # CPU Power Kontrolü
        cpu_label = QLabel()
        cpu_label.setObjectName("cpu_label")
        cpu_label.setWordWrap(True)
        cpu_layout.addWidget(cpu_label)
        
        cpu_button_layout = QHBoxLayout()
        btn_cpupower_apply = QPushButton()
        btn_cpupower_apply.setObjectName("btn_cpupower_apply")
        btn_cpupower_apply.setStyleSheet(self.style_apply_action)
        btn_cpupower_apply.clicked.connect(lambda: self.run_cpupower("powersave", self.texts[self.current_lang]['btn_cpupower_apply']))
        cpu_button_layout.addWidget(btn_cpupower_apply)
        btn_cpupower_restore = QPushButton()
        btn_cpupower_restore.setObjectName("btn_cpupower_restore")
        btn_cpupower_restore.setStyleSheet(self.style_restore_action)
        btn_cpupower_restore.clicked.connect(lambda: self.run_cpupower("performance", self.texts[self.current_lang]['btn_cpupower_restore']))
        cpu_button_layout.addWidget(btn_cpupower_restore)
        cpu_layout.addLayout(cpu_button_layout)
        
        # Swappiness Kontrolü
        swappiness_label = QLabel()
        swappiness_label.setObjectName("swappiness_label")
        swappiness_label.setWordWrap(True)
        cpu_layout.addWidget(swappiness_label)
        
        swappiness_button_layout = QHBoxLayout()
        btn_swappiness_apply = QPushButton()
        btn_swappiness_apply.setObjectName("btn_swappiness_apply")
        btn_swappiness_apply.setStyleSheet(self.style_apply_action)
        btn_swappiness_apply.clicked.connect(lambda: self.run_swappiness_control("10", self.texts[self.current_lang]['btn_swappiness_apply']))
        swappiness_button_layout.addWidget(btn_swappiness_apply)
        btn_swappiness_restore = QPushButton()
        btn_swappiness_restore.setObjectName("btn_swappiness_restore")
        btn_swappiness_restore.setStyleSheet(self.style_restore_action)
        btn_swappiness_restore.clicked.connect(lambda: self.run_swappiness_control("60", self.texts[self.current_lang]['btn_swappiness_restore']))
        swappiness_button_layout.addWidget(btn_swappiness_restore)
        cpu_layout.addLayout(swappiness_button_layout)
        
        layout.addWidget(cpu_group)
        layout.addStretch(1)
        return tab

    # --- İşlem Yürütme Fonksiyonları ---
    
    def run_garbage_privacy_cleanup(self):
        """Çöp ve Gizlilik temizleme işlemlerini sırayla yürütür."""
        is_secure = self.chk_secure_delete.isChecked()
        texts_log = self.texts[self.current_lang]['log_messages']
        
        secure_status = texts_log['secure_status_active'] if is_secure else texts_log['secure_status_inactive']
        self.log_message(texts_log['cleaning_start'].format(secure_status=secure_status))
        
        # Kullanıcının Ana Klasör yolu
        home = os.path.expanduser("~")

        # 1. Çöp Kutusu Temizliği (Sadece Geçerli Kullanıcı)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").isChecked():
            self.log_message(texts_log['trash_start'])
            
            try:
                trash_path = os.path.expanduser("~/.local/share/Trash/files")
                if not os.path.exists(trash_path):
                     self.log_message(texts_log['trash_not_found'])
                else:
                    cleaned_count = 0
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
                    self.log_message(texts_log['trash_success'].format(count=cleaned_count))
            except Exception as e:
                self.log_message(texts_log['trash_error'].format(error=e))

        # 2. ÖZEL GİZLİLİK TEMİZLİĞİ

        # Son Kullanılanlar (.xbel)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").isChecked():
            self.log_message(texts_log['recent_xbel'])
            self.clean_file(os.path.join(home, ".local/share/recently-used.xbel"), is_secure=is_secure)

        # RecentDocuments
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").isChecked():
            self.log_message(texts_log['recent_docs'])
            self.clean_directory_contents(os.path.join(home, ".local/share/RecentDocuments"), is_secure=is_secure)

        # Genel Son Kullanılanlar Geçmişi
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_history").isChecked():
            self.log_message(texts_log['recent_history'])
            self.clean_file(os.path.join(home, ".local/share/zeitgeist/activity.sqlite"), is_secure=is_secure)
            self.clean_file(os.path.join(home, ".recently-used.xbel"), is_secure=is_secure) 
        
        # thumbs.db (Home dizini içi)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_db").isChecked():
            self.log_message(texts_log['thumbs_db_start'])
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
                self.log_message(texts_log['thumbs_db_success'].format(count=deleted_count))
            except Exception as e:
                self.log_message(texts_log['thumbs_db_error'].format(error=e))

        # 3. Küçük Resim (Thumbnail) Önbelleği
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_large").isChecked():
            self.log_message(texts_log['thumbs_large'])
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/large"), is_secure=is_secure)

        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_normal").isChecked():
            self.log_message(texts_log['thumbs_normal'])
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/normal"), is_secure=is_secure)

        self.log_message(texts_log['cleaning_end'])

    def secure_delete_file(self, filepath):
        """Dosyayı shred ile güvenli bir şekilde siler (3 geçiş)."""
        texts_log = self.texts[self.current_lang]['log_messages']
        if os.path.exists(filepath):
            try:
                subprocess.run(["shred", "-f", "-u", filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message(texts_log['secure_success'].format(filepath=filepath))
            except subprocess.CalledProcessError as e:
                self.log_message(texts_log['secure_error_shred'].format(filepath=filepath, error=e))
            except FileNotFoundError:
                self.log_message(texts_log['secure_not_found'].format(filepath=filepath))
                self.clean_file(filepath, is_secure=False)
            except Exception as e:
                self.log_message(texts_log['secure_unknown_error'].format(error=e))
        else:
            self.log_message(texts_log['file_not_found'].format(filepath=filepath))


    def clean_file(self, filepath, is_secure=False):
        """Belirtilen dosyayı normal veya güvenli şekilde siler ve günlük kaydı tutar."""
        texts_log = self.texts[self.current_lang]['log_messages']
        if os.path.exists(filepath):
            if is_secure:
                self.secure_delete_file(filepath)
                return
                
            try:
                os.remove(filepath)
                self.log_message(texts_log['file_deleted'].format(filepath=filepath))
            except Exception as e:
                self.log_message(texts_log['file_error'].format(filepath=filepath, error=e))
        else:
            self.log_message(texts_log['file_not_found'].format(filepath=filepath))

    def clean_directory_contents(self, dirpath, is_secure=False):
        """Belirtilen dizinin içeriğini siler (dizini silmez)."""
        texts_log = self.texts[self.current_lang]['log_messages']
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
                self.log_message(texts_log['dir_content_success'].format(dirpath=dirpath, count=count))
            except Exception as e:
                self.log_message(texts_log['dir_content_error'].format(dirpath=dirpath, error=e))
        else:
            self.log_message(texts_log['file_not_found'].format(filepath=dirpath))
            
    # --- APT Temizliği ---

    def run_apt_cleanup(self):
        """APT temizlik komutlarını QProcess ile pkexec kullanarak yürütür."""
        chk_autoremove = self.tab_apt_widget.findChild(QCheckBox, "chk_autoremove").isChecked()
        chk_autoclean = self.tab_apt_widget.findChild(QCheckBox, "chk_autoclean").isChecked()
        texts = self.texts[self.current_lang]

        if not (chk_autoremove or chk_autoclean):
            self.show_alert(texts['about_title'], texts['error_no_apt_selection'])
            return

        self.log_message(texts['log_messages']['apt_start'])

        if chk_autoremove:
            self.execute_command_with_pkexec("/usr/bin/apt autoremove -y", texts['chk_autoremove'])

        if chk_autoclean:
            self.execute_command_with_pkexec("/usr/bin/apt autoclean", texts['chk_autoclean'])

    # --- Disk Birleştirme (Defrag) ---

    def run_defrag(self):
        """u4defrag komutunu QProcess ile pkexec kullanarak yürütür."""
        texts = self.texts[self.current_lang]
        self.log_message(texts['log_messages']['defrag_start'])
        self.execute_command_with_pkexec("/usr/bin/u4defrag -s /", texts['btn_defrag'])

    # --- CPU Optimizasyonu (Apply ve Restore) ---

    def run_cpupower(self, governor, task_name):
        """cpupower komutunu QProcess ile pkexec kullanarak yürütür (powersave veya performance)."""
        texts_log = self.texts[self.current_lang]['log_messages']
        
        if governor == "powersave":
            self.log_message(texts_log['cpu_apply_start'])
        elif governor == "performance":
             self.log_message(texts_log['cpu_restore_start'])
             
        command = f"/usr/bin/cpupower frequency-set -g {governor}"
        self.execute_command_with_pkexec(command, task_name)
        
    # --- Swappiness Kontrolü ---
    
    def run_swappiness_control(self, value, task_name):
        """vm.swappiness ayarını QProcess ile pkexec kullanarak ayarlar."""
        
        texts_log = self.texts[self.current_lang]['log_messages']
        self.log_message(texts_log['swappiness_start'].format(value=value))
        
        # Kalıcı olmayan ayar: sysctl vm.swappiness=<value>
        command = f"sysctl vm.swappiness={value}" 
        self.execute_command_with_pkexec(command, task_name)

    # --- RAM Temizliği ---

    def run_ram_cleanup(self):
        """RAM önbelleği temizleme komutunu QProcess ile pkexec kullanarak yürütür."""
        texts = self.texts[self.current_lang]
        command = 'sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"'
        self.log_message(texts['log_messages']['ram_start'])
        self.execute_command_with_pkexec(command, texts['btn_ram_clean'])

    # --- SWAP Temizliği ---

    def run_swap_cleanup(self):
        """Takas Alanını temizler (Swapoff ve Swapon)."""
        texts = self.texts[self.current_lang]
        command = 'sh -c "swapoff -a && swapon -a"'
        self.log_message(texts['log_messages']['swap_start'])
        self.execute_command_with_pkexec(command, texts['btn_swap_clean'])


    # --- QProcess Ortak Yürütme Fonksiyonu (PKEXEC) ---

    def execute_command_with_pkexec(self, command, task_name):
        """QProcess kullanarak pkexec ile bir komutu yürütür."""
        
        if self.process and self.process.state() == QProcess.Running:
            texts = self.texts[self.current_lang]
            self.show_alert(texts['about_title'], texts['error_busy'])
            return

        if " " in command and not command.startswith("sh -c"):
            escaped_command = command.replace('"', '\\"')
            full_command = 'pkexec sh -c "{}"'.format(escaped_command)
        else:
            full_command = f'pkexec {command}'

        self.process = QProcess()
        
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(lambda exitCode, exitStatus: self.handle_finished(exitCode, exitStatus, task_name))
        
        texts_log = self.texts[self.current_lang]['log_messages']
        self.log_message(texts_log['starting_pkexec'].format(command=full_command))
        
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
        texts_log = self.texts[self.current_lang]['log_messages']
        
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            self.log_message(texts_log['process_success'].format(task_name=task_name, exitCode=exitCode))
        else:
            self.log_message(texts_log['process_error'].format(task_name=task_name, exitCode=exitCode, exitStatus=exitStatus))

# --- Uygulama Başlatma ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinuxCleanerApp()
    window.show()
    sys.exit(app.exec())
