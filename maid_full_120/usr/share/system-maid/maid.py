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
        
        # Sürüm numarasını tanımla (HATA DÜZELTMESİ: En üste taşındı)
        self.VERSION = "1.2.0"

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
                
                # Tab 1: Garbage & Privacy (Güncellendi)
                'tab_garbage': "Junk & Privacy Cleanup",
                'secure_group': "Secure Deletion Settings",
                'chk_secure_delete': "Activate Secure Deletion (shred)",
                'secure_delete_label': "This option prevents attackers from recovering deleted data using random data overwriting (shred).",
                
                # Yeni Temizlik Kontrolleri
                'clean_group': "File System Cleanup",
                'chk_broken_links': "Delete Broken Symbolic Links in Home Folder",
                'chk_empty_dirs': "Delete Empty Directories in Home Folder",
                'chk_user_caches': "Clean Snap/Flatpak/User Cache Residue (rm -rf)",
                
                'trash_group': "Trash Cleanup",
                'chk_trash': "Empty Current User's Trash Bin",
                
                # Yeni Gizlilik Kontrolleri
                'privacy_group': "Specific History Cleanup",
                'chk_recent_xbel': "Clean Recently Used (.xbel) file",
                'chk_recent_docs': "Clean Recently Used Documents folder content",
                'chk_recent_history': "Clean General Recent File History", # Yeni
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
                
                # Tab 3: Optimization (Güncellendi)
                'tab_optimization': "System Optimization",
                'defrag_group': "Disk Optimization (Privilege Required)",
                'defrag_label': "WARNING: Modern Linux filesystems (Ext4, Btrfs) generally do not need defragmentation. It is also not recommended for SSDs. It is highly recommended for HDDs and can provide up to 30% speed increase. This process is slow!",
                'btn_defrag': "Start Disk Defragmentation",
                
                # RAM/SWAP Grubu
                'ram_swap_group': "RAM and Swap Management (Privilege Required)", # Yeni Grup
                'ram_label': "This process increases available RAM by freeing up data held in the system cache. It is not true memory release and may cause the system to slow down briefly.",
                'btn_ram_clean': "Clean RAM Caches",
                'swap_label': "This process clears the Swap Area (virtual memory on disk) to prevent sensitive data from remaining after use.", # Yeni
                'btn_swap_clean': "Clear Swap Area", # Yeni
                
                # CPU/Swappiness Grubu
                'cpu_group': "CPU & Swappiness Control (Privilege Required)",
                'cpu_label': "This process changes the CPU Governor to 'powersave'. This maximizes battery life and reduces heat, but system speed will noticeably decrease. Use this if you need energy saving.", # DEĞİŞTİ
                'btn_cpupower_apply': "Apply Power Save Mode", # DEĞİŞTİ
                'btn_cpupower_restore': "Restore Performance Mode", # DEĞİŞTİ
                'swappiness_label': "Sets the kernel's tendency to use swap memory. Low values (e.g., 10) are better for systems with plenty of RAM. (Default is often 60).", # Yeni
                'btn_swappiness_apply': "Apply Swappiness (Set to 10)", # Yeni
                'btn_swappiness_restore': "Restore Swappiness (Set to 60)", # Yeni
                
                # About Dialog
                'about_title': "About System Maid",
                'about_version': "Version:",
                'about_license': "License:",
                'about_programming': "Programming:",
                'about_description': "This program helps your computer run healthier by performing system cleaning and performance adjustments, while protecting your privacy from attackers.",
                'about_disclaimer': "This program comes with no warranty.",
                'btn_ok': "OK",
                
                # Log Mesajları (Eklenenler)
                'log_title_start': "--- Cleaning Initiated (Secure Deletion: {}) ---",
                'log_title_apt_start': "--- APT Cleanup Initiated (pkexec Required) ---",
                'log_title_defrag_start': "--- Disk Defragmentation Initiated (pkexec Required) ---",
                'log_title_cpu_save_start': "--- Applying CPU Optimization (powersave) ---",
                'log_title_cpu_restore_start': "--- Restoring CPU Optimization (performance) ---",
                'log_title_swappiness_start': "--- Applying Swappiness Setting (Value: {}) ---",
                'log_title_ram_start': "--- RAM Cache Cleanup Initiated (pkexec Required) ---",
                'log_title_swap_start': "--- Swap Area Cleanup Initiated (pkexec Required) ---",
                'log_title_end': "--- Cleanup Operation Completed ---",
                
                'log_msg_broken_links_search': "Searching for and deleting broken symbolic links in Home Folder...",
                'log_msg_broken_links_success': "✅ Broken symbolic links cleaned.",
                'log_msg_broken_links_error': "❌ Error cleaning broken symbolic links: {}",
                
                'log_msg_empty_dirs_search': "Searching for and deleting empty directories in Home Folder...",
                'log_msg_empty_dirs_success': "✅ Empty directories cleaned.",
                'log_msg_empty_dirs_error': "❌ Error cleaning empty directories: {}",
                
                'log_msg_user_caches_search': "Cleaning Snap/Flatpak/User Cache residue...",
                'log_msg_user_caches_cleaned': "Cleaned: {}",
                'log_msg_user_caches_error': "❌ Cleanup error ({}): {}",
                'log_msg_user_caches_success': "✅ User cache residue cleanup completed ({} directory/file groups).",
                
                'log_msg_trash_empty': "Emptying current user's trash bin...",
                'log_msg_trash_not_found': "ℹ️ Trash bin directory not found, skipping.",
                'log_msg_trash_success': "✅ Current user's trash bin successfully cleaned. ({} items)",
                'log_msg_trash_error': "❌ Error cleaning trash bin: {}",

                'log_msg_recent_xbel_clean': "Cleaning recently used (.xbel)...",
                'log_msg_recent_docs_clean': "Cleaning recently used documents folder content...",
                'log_msg_recent_history_clean': "Cleaning general recent file history (GTK/Zeitgeist)...",
                
                'log_msg_thumbs_db_search': "Searching for thumbs.db files in Home directory...",
                'log_msg_thumbs_db_deleted': "Deleted: {}",
                'log_msg_thumbs_db_success': "✅ thumbs.db cleanup completed. ({} files)",
                'log_msg_thumbs_db_error': "❌ Error cleaning thumbs.db: {}",
                
                'log_msg_thumbs_large_clean': "Cleaning .cache/thumbnails/large...",
                'log_msg_thumbs_normal_clean': "Cleaning .cache/thumbnails/normal...",
                
                'log_msg_file_deleted': "✅ File deleted: {}",
                'log_msg_file_error': "❌ Error deleting file ({}): {}",
                'log_msg_file_not_found': "ℹ️ File not found: {}",
                
                'log_msg_dir_contents_success': "✅ Directory contents cleaned: {} ({} items)",
                'log_msg_dir_contents_error': "❌ Error cleaning directory contents ({}): {}",
                'log_msg_dir_not_found': "ℹ️ Directory not found: {}",
                
                'log_msg_secure_success': "✅ Secure Deletion successful: {}",
                'log_msg_secure_error': "❌ Secure Deletion error ({}): {}",
                'log_msg_secure_shred_missing': "❌ Error: 'shred' tool not found. Performing normal deletion. ({})",
                'log_msg_secure_unknown_error': "❌ Unknown error during Secure Deletion: {}",
                'log_msg_secure_file_not_found': "ℹ️ Secure Deletion: File not found: {}",
                
                'log_msg_pkexec_start': "Starting (pkexec): '{}'",
                'log_msg_stdout': "Output: {}",
                'log_msg_stderr': "ERROR: {}",
                'log_msg_process_success': "✅ {} operation completed successfully (Exit Code: {})",
                'log_msg_process_error': "❌ {} operation completed with ERROR (Exit Code: {}, Status: {}). Please check your permissions.",
                
                'error_title': "Error",
                'error_busy': "Please wait for the current operation to finish.",
                'error_no_apt_selection': "Please select at least one APT cleanup option.",
            },
            'tr': {
                'window_title': f"System Maid - Linux Temizleyici ve Optimizasyon Aracı (v{self.VERSION})",
                'header_title': "System Maid",
                'log_group': "İşlem Günlüğü ve Sonuçlar",
                'log_start_info': "Uygulama başlatıldı. Lütfen temizlik ve optimizasyon seçeneklerini seçiniz.",
                'log_privilege_info': "Yetki Gereksinimi: APT, Defrag, CPU, RAM ve Takas Alanı işlemleri için pkexec (Root Yetkisi) kullanılacaktır.",
                
                # Tab 1: Çöp ve Gizlilik (Güncellendi)
                'tab_garbage': "Çöp ve Gizlilik Temizliği",
                'secure_group': "Güvenli Silme Ayarları",
                'chk_secure_delete': "Güvenli Silmeyi Aktif Et (shred)",
                'secure_delete_label': "Bu seçenek, başkalarının veri kurtarma yöntemiyle sildiğiniz verileri kurtarmasını ve sizi heklemesini önler. Bu yöntem, dosya silinmeden önce üzerine karmaşık veri yazar (shred).",
                
                # Yeni Temizlik Kontrolleri
                'clean_group': "Dosya Sistemi Temizliği",
                'chk_broken_links': "Ev Klasöründeki Kırık Sembolik Bağlantıları Sil",
                'chk_empty_dirs': "Ev Klasöründeki Boş Dizinleri Temizle",
                'chk_user_caches': "Snap/Flatpak/Kullanıcı Önbellek Kalıntılarını Temizle (rm -rf)",
                
                'trash_group': "Çöp Kutusu Temizliği",
                'chk_trash': "Geçerli Kullanıcının Çöp Kutusunu Boşalt",
                
                # Yeni Gizlilik Kontrolleri
                'privacy_group': "Özel Geçmiş Temizliği",
                'chk_recent_xbel': "Son Kullanılanlar (.xbel) dosyasını temizle",
                'chk_recent_docs': "Son Kullanılan Belgeler (RecentDocuments) klasör içeriğini temizle",
                'chk_recent_history': "Genel Son Kullanılan Dosya Geçmişini Temizle", # Yeni
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
                
                # Tab 3: Optimizasyon (Güncellendi)
                'tab_optimization': "Sistem Optimizasyonu",
                'defrag_group': "Disk Optimizasyonu (Yetki Gereklidir)",
                'defrag_label': "UYARI: Modern Linux dosya sistemleri (Ext4, Btrfs) genellikle birleştirmeye ihtiyaç duymazlar. Ayrıca sisteminiz SSD üzerine kuruluysa da birleştirme yapılması önerilmez. Sisteminiz bir HDD üzerinde çalışıyorsa kesinlikle önerilir ve %30'a kadar hız artışı sağlayabilir. Bu işlem uzun sürer!",
                'btn_defrag': "Disk Birleştirmeyi Başlat",
                
                # RAM/SWAP Grubu
                'ram_swap_group': "RAM ve Takas Alanı Yönetimi (Yetki Gereklidir)", # Yeni Grup
                'ram_label': "Bu işlem, sistemin önbellekte tuttuğu verileri serbest bırakarak kullanılabilir RAM miktarını artırır. Gerçek bellek boşaltımı değildir ve sistemin kısa bir süre için yavaşlamasına neden olabilir.",
                'btn_ram_clean': "RAM ÖnBelleklerini Temizle",
                'swap_label': "Bu işlem, hassas verilerin kullanım sonrası bellekte kalmasını engellemek için Takas Alanını (diskteki sanal bellek) temizler ve yeniden etkinleştirir.", # Yeni
                'btn_swap_clean': "Takas Alanını Temizle", # Yeni
                
                # CPU/Swappiness Grubu
                'cpu_group': "CPU ve Swappiness Kontrolü (Yetki Gereklidir)",
                'cpu_label': "Bu işlem, CPU Yöneticisini 'powersave' moduna geçirir. Bu, pil ömrünü uzatır ve ısınmayı azaltır, ancak sistem hızı belirgin şekilde düşecektir. Enerji tasarrufuna ihtiyacınız varsa kullanın.", # DEĞİŞTİ
                'btn_cpupower_apply': "Güç Tasarrufu Modunu Uygula", # DEĞİŞTİ
                'btn_cpupower_restore': "Performans Moduna Geri Dön", # DEĞİŞTİ
                'swappiness_label': "Kernel'ın takas belleği kullanma eğilimini ayarlar. Düşük değerler (örneğin 10) bol RAM'e sahip sistemler için daha iyidir. (Varsayılan genellikle 60'tır).", # Yeni
                'btn_swappiness_apply': "Swappiness Uygula (10 Yap)", # Yeni
                'btn_swappiness_restore': "Swappiness Geri Al (60 Yap)", # Yeni
                
                # Hakkında Diyalogu
                'about_title': "System Maid Hakkında",
                'about_version': "Sürüm:",
                'about_license': "Lisans:",
                'about_programming': "Programlama:",
                'about_description': "Bu program, sistem temizliği ve performans ayarları yaparak bilgisayarınızın daha sağlıklı çalışmasına yardımcı olurken, özel hayatınızı saldırganlardan korumanıza yardımcı olur.",
                'about_disclaimer': "Bu program hiçbir garanti getirmez.",
                'btn_ok': "Tamam",

                # Log Mesajları (Eklenenler)
                'log_title_start': "--- Temizlik Başlatılıyor (Güvenli Silme: {}) ---",
                'log_title_apt_start': "--- APT Temizliği Başlatılıyor (pkexec Gerekir) ---",
                'log_title_defrag_start': "--- Disk Birleştirme Başlatılıyor (pkexec Gerekir) ---",
                'log_title_cpu_save_start': "--- CPU Optimizasyonu Uygulanıyor (powersave) ---",
                'log_title_cpu_restore_start': "--- CPU Optimizasyonu Geri Alınıyor (performance) ---",
                'log_title_swappiness_start': "--- Swappiness Ayarı Uygulanıyor (Değer: {}) ---",
                'log_title_ram_start': "--- RAM ÖnBellek Temizliği Başlatılıyor (pkexec Gerekir) ---",
                'log_title_swap_start': "--- Takas Alanı (Swap) Temizliği Başlatılıyor (pkexec Gerekir) ---",
                'log_title_end': "--- Temizlik İşlemi Tamamlandı ---",

                'log_msg_broken_links_search': "Ana Klasördeki kırık sembolik bağlantılar aranıyor ve siliniyor...",
                'log_msg_broken_links_success': "✅ Kırık sembolik bağlantılar temizlendi.",
                'log_msg_broken_links_error': "❌ Kırık sembolik bağlantılar temizlenirken hata oluştu: {}",
                
                'log_msg_empty_dirs_search': "Ana Klasördeki boş dizinler aranıyor ve siliniyor...",
                'log_msg_empty_dirs_success': "✅ Boş dizinler temizlendi.",
                'log_msg_empty_dirs_error': "❌ Boş dizinler temizlenirken hata oluştu: {}",
                
                'log_msg_user_caches_search': "Snap/Flatpak/Kullanıcı Önbellek kalıntıları temizleniyor...",
                'log_msg_user_caches_cleaned': "Temizlendi: {}",
                'log_msg_user_caches_error': "❌ Temizlik hatası ({}): {}",
                'log_msg_user_caches_success': "✅ Kullanıcı önbellek kalıntıları temizliği tamamlandı ({} dizin/dosya grubu).",
                
                'log_msg_trash_empty': "Geçerli kullanıcının çöp kutusu boşaltılıyor...",
                'log_msg_trash_not_found': "ℹ️ Çöp kutusu dizini bulunamadı, atlanıyor.",
                'log_msg_trash_success': "✅ Geçerli kullanıcının çöp kutusu başarıyla temizlendi. ({} öğe)",
                'log_msg_trash_error': "❌ Çöp kutusu temizlenirken hata oluştu: {}",

                'log_msg_recent_xbel_clean': "Son kullanılanlar (.xbel) temizleniyor...",
                'log_msg_recent_docs_clean': "Son kullanılan belgeler klasör içeriği temizleniyor...",
                'log_msg_recent_history_clean': "Genel son kullanılan dosya geçmişi (GTK/Zeitgeist) temizleniyor...",
                
                'log_msg_thumbs_db_search': "Home dizinindeki thumbs.db dosyaları aranıyor...",
                'log_msg_thumbs_db_deleted': "Silindi: {}",
                'log_msg_thumbs_db_success': "✅ thumbs.db temizliği tamamlandı. ({} dosya)",
                'log_msg_thumbs_db_error': "❌ thumbs.db temizlenirken hata oluştu: {}",
                
                'log_msg_thumbs_large_clean': "Büyük Boyutlu Küçük Resimler önbelleği temizleniyor...",
                'log_msg_thumbs_normal_clean': "Normal Boyutlu Küçük Resimler önbelleği temizleniyor...",
                
                'log_msg_file_deleted': "✅ Dosya silindi: {}",
                'log_msg_file_error': "❌ Dosya silinirken hata oluştu ({}): {}",
                'log_msg_file_not_found': "ℹ️ Dosya bulunamadı: {}",
                
                'log_msg_dir_contents_success': "✅ Dizin içeriği temizlendi: {} ({} öğe)",
                'log_msg_dir_contents_error': "❌ Dizin içeriği temizlenirken hata oluştu ({}): {}",
                'log_msg_dir_not_found': "ℹ️ Dizin bulunamadı: {}",

                'log_msg_secure_success': "✅ Güvenli Silme başarılı: {}",
                'log_msg_secure_error': "❌ Güvenli Silme hatası oluştu ({}): {}",
                'log_msg_secure_shred_missing': "❌ Hata: 'shred' aracı bulunamadı. Normal silme yapılıyor. ({})",
                'log_msg_secure_unknown_error': "❌ Güvenli Silme sırasında bilinmeyen hata: {}",
                'log_msg_secure_file_not_found': "ℹ️ Güvenli Silme: Dosya bulunamadı: {}",

                'log_msg_pkexec_start': "Başlatılıyor (pkexec): '{}'",
                'log_msg_stdout': "Çıktı: {}",
                'log_msg_stderr': "HATA: {}",
                'log_msg_process_success': "✅ {} işlemi başarıyla tamamlandı (Çıkış Kodu: {})",
                'log_msg_process_error': "❌ {} işlemi HATA ile tamamlandı (Çıkış Kodu: {}, Durum: {}). Lütfen yetkinizi kontrol edin.",

                'error_title': "Hata",
                'error_busy': "Lütfen mevcut işlemin tamamlanmasını bekleyin.",
                'error_no_apt_selection': "Lütfen en az bir APT temizlik seçeneği işaretleyiniz.",
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

        # 1. Genel Temizleme/Başlatma Butonları (Yeşil) - YÜKSEKLİK EŞİTLENDİ
        self.style_primary_clean = """
            QPushButton {
                background-color: #4CAF50; /* Yeşil */
                color: white;
                border: 2px solid #388E3C;
                border-radius: 8px;
                padding: 8px 20px; /* Dikey padding 10px'den 8px'e düşürüldü */
                font-weight: bold;
                font-size: 10pt; /* Font boyutu 11pt'den 10pt'ye düşürüldü */
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """
        
        # 2. Uygula (Apply) Butonları (Mavi) - YAZI KALINLAŞTIRILDI
        self.style_apply_action = """
            QPushButton {
                background-color: #2196F3; /* Mavi */
                color: white;
                border: 2px solid #1976D2;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold; /* Bold yapıldı */
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """

        # 3. Geri Al (Restore) Butonları (Turuncu) - YAZI KALINLAŞTIRILDI
        self.style_restore_action = """
            QPushButton {
                background-color: #FF9800; /* Turuncu */
                color: white;
                border: 2px solid #FB8C00;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold; /* Bold yapıldı */
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
        
        # İkon Resim Nesnesi (68x68 olarak ayarlandı)
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
        
        header_layout.addStretch(1) # Başlık ve ikonları sola yaslamak için
        
        # Hakkında Butonu
        self.btn_about = QPushButton()
        self.btn_about.setStyleSheet(self.style_utility) # Stil Uygulama
        self.btn_about.clicked.connect(self.show_about_dialog)
        header_layout.addWidget(self.btn_about)
        
        # Dil Değiştirme Butonu (Evrensel: "Language")
        self.btn_lang = QPushButton("Language")
        self.btn_lang.setStyleSheet(self.style_utility) # Stil Uygulama
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
            # BU KISIMDA DİL DEĞİŞTİRME ETKİLENMESİN DİYE SADECE BAŞLANGIÇTA EKLENİYOR
            # Ancak yine de doğru dilde görünmesi için güncellenmelidir.
            # update_ui_texts çağrıldığında log'u temizleyip yeniden ekleyelim, 
            # ancak bu, kullanıcının daha önceki log'unu kaybeder.
            # İlk başlangıç kontrolü (tekrar eden log'u engeller)
            
            # Not: Kullanıcı logu kaybetmesin diye: 
            # Sadece dil değiştiğinde ilk iki bilgi mesajı yeniden eklenmeli veya temizlenmeliydi.
            # Şimdilik, sadece ilk açılışta eklemeye devam edelim.
            # Daha önce log yazılmadıysa ilk iki mesajı ekle
            if self.output_log.document().blockCount() <= 1:
                self.output_log.clear() # Önceki boş log'u temizle
                self.log_message(texts['log_start_info'])
                self.log_message(texts['log_privilege_info'])
        
        # Tab 1: Çöp ve Gizlilik
        self.tab_garbage_widget.findChild(QGroupBox, "secure_group").setTitle(texts['secure_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_secure_delete").setText(texts['chk_secure_delete'])
        self.tab_garbage_widget.findChild(QLabel, "secure_delete_label").setText(texts['secure_delete_label'])
        
        self.tab_garbage_widget.findChild(QGroupBox, "clean_group").setTitle(texts['clean_group']) # Yeni Grup
        self.tab_garbage_widget.findChild(QCheckBox, "chk_broken_links").setText(texts['chk_broken_links']) # Yeni Checkbox
        self.tab_garbage_widget.findChild(QCheckBox, "chk_empty_dirs").setText(texts['chk_empty_dirs']) # Yeni Checkbox
        self.tab_garbage_widget.findChild(QCheckBox, "chk_user_caches").setText(texts['chk_user_caches']) # Yeni Checkbox

        self.tab_garbage_widget.findChild(QGroupBox, "trash_group").setTitle(texts['trash_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").setText(texts['chk_trash'])
        
        self.tab_garbage_widget.findChild(QGroupBox, "privacy_group").setTitle(texts['privacy_group'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").setText(texts['chk_recent_xbel'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").setText(texts['chk_recent_docs'])
        self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_history").setText(texts['chk_recent_history']) # Yeni Checkbox
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
        
        self.tab_optimization_widget.findChild(QGroupBox, "ram_swap_group").setTitle(texts['ram_swap_group']) # Yeni Grup
        self.tab_optimization_widget.findChild(QLabel, "ram_label").setText(texts['ram_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_ram_clean").setText(texts['btn_ram_clean'])
        self.tab_optimization_widget.findChild(QLabel, "swap_label").setText(texts['swap_label']) # Yeni Label
        self.tab_optimization_widget.findChild(QPushButton, "btn_swap_clean").setText(texts['btn_swap_clean']) # Yeni Buton
        
        self.tab_optimization_widget.findChild(QGroupBox, "cpu_group").setTitle(texts['cpu_group'])
        self.tab_optimization_widget.findChild(QLabel, "cpu_label").setText(texts['cpu_label'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_apply").setText(texts['btn_cpupower_apply'])
        self.tab_optimization_widget.findChild(QPushButton, "btn_cpupower_restore").setText(texts['btn_cpupower_restore'])
        self.tab_optimization_widget.findChild(QLabel, "swappiness_label").setText(texts['swappiness_label']) # Yeni Label
        self.tab_optimization_widget.findChild(QPushButton, "btn_swappiness_apply").setText(texts['btn_swappiness_apply']) # Yeni Buton
        self.tab_optimization_widget.findChild(QPushButton, "btn_swappiness_restore").setText(texts['btn_swappiness_restore']) # Yeni Buton

    def toggle_language(self):
        """Dili Türkçe ve İngilizce arasında değiştirir ve arayüzü günceller."""
        self.current_lang = 'tr' if self.current_lang == 'en' else 'en'
        self.update_ui_texts()
        # Düzeltme: Dil değişim mesajı aktif dilde olmalı.
        log_msg = self.texts[self.current_lang].get('log_msg_lang_change', "Dili '{language}' olarak değiştirdiniz.")
        lang_name = 'Türkçe' if self.current_lang == 'tr' else 'English'
        self.log_message(log_msg.replace('{language}', lang_name))


    def log_message(self, message):
        """Günlük alanına mesaj ekler."""
        # Düzeltme: Log mesajlarının başına zaman damgası eklemek daha iyidir.
        # Ancak orijinal kodda sadece os.linesep eklenmiş. Orijinal kodu koruyalım.
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
        <p><b>{texts['about_version']}</b> {self.VERSION}</p>
        <p><b>{texts['about_license']}</b> GPLv3</p>
        <p><b>{texts['about_programming']}</b> A. Serhat KILIÇOĞLU</p>
        <p><b>Github:</b> <a href="https://www.github.com/shampuan">www.github.com/shampuan</a></p>
        <hr>
        <p>{texts['about_description']}</p>
        <p style='color: red; font-weight: bold;'>{texts['about_disclaimer']}</p>
        """
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True) # Github linkini açabilmek için
        info_label.setWordWrap(True) # Metnin otomatik alt satıra geçmesini sağlar
        dialog_layout.addWidget(info_label)
        
        # 4. Tamam Butonu
        ok_button = QPushButton(texts['btn_ok'])
        # Hakkında butonu için de sade bir stil uygulaması
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
        
        # --- 2. Dosya Sistemi Temizliği Grubu (Yeni) ---
        clean_group = QGroupBox()
        clean_group.setObjectName("clean_group")
        clean_layout = QVBoxLayout(clean_group)

        self.chk_broken_links = QCheckBox()
        self.chk_broken_links.setObjectName("chk_broken_links")
        #self.chk_broken_links.setChecked(True)
        
        self.chk_empty_dirs = QCheckBox()
        self.chk_empty_dirs.setObjectName("chk_empty_dirs")
        #self.chk_empty_dirs.setChecked(True)
        
        self.chk_user_caches = QCheckBox()
        self.chk_user_caches.setObjectName("chk_user_caches")
        #self.chk_user_caches.setChecked(True)
        
        clean_layout.addWidget(self.chk_broken_links)
        clean_layout.addWidget(self.chk_empty_dirs)
        clean_layout.addWidget(self.chk_user_caches)
        content_layout.addWidget(clean_group)
        content_layout.addSpacing(15)

        # --- 3. Çöp Kutusu Grubu (Sadece Geçerli Kullanıcı) ---
        trash_group = QGroupBox()
        trash_group.setObjectName("trash_group")
        trash_layout = QVBoxLayout(trash_group)
        self.chk_trash = QCheckBox()
        self.chk_trash.setObjectName("chk_trash")
        #self.chk_trash.setChecked(True)
        trash_layout.addWidget(self.chk_trash)
        content_layout.addWidget(trash_group)
        content_layout.addSpacing(15)

        # --- 4. Özel Geçmiş Temizliği ---
        privacy_group = QGroupBox()
        privacy_group.setObjectName("privacy_group")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.chk_recent_xbel = QCheckBox()
        self.chk_recent_xbel.setObjectName("chk_recent_xbel")
        self.chk_recent_docs = QCheckBox()
        self.chk_recent_docs.setObjectName("chk_recent_docs")
        self.chk_recent_history = QCheckBox() # Yeni
        self.chk_recent_history.setObjectName("chk_recent_history")
        self.chk_thumbs_db = QCheckBox()
        self.chk_thumbs_db.setObjectName("chk_thumbs_db")
        
        self.chk_recent_xbel.setChecked(True)
        self.chk_recent_docs.setChecked(True)
        self.chk_recent_history.setChecked(True) # Yeni varsayılan
        
        privacy_layout.addWidget(self.chk_recent_xbel)
        privacy_layout.addWidget(self.chk_recent_docs)
        privacy_layout.addWidget(self.chk_recent_history) # Yeni
        privacy_layout.addWidget(self.chk_thumbs_db)
        content_layout.addWidget(privacy_group)
        content_layout.addSpacing(15)
        
        # --- 5. Thumbnail (Küçük Resim) Önbellek Temizliği ---
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
        
        # RAM ve SWAP Yönetimi Grubu (Yeni)
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
        btn_swap_clean.clicked.connect(self.run_swap_cleanup) # Yeni Bağlantı
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
        btn_cpupower_apply.clicked.connect(lambda: self.run_cpupower("powersave", self.texts[self.current_lang]['btn_cpupower_apply'])) # Düzeltme: Task adı dil bağımsız olmamalıydı
        cpu_button_layout.addWidget(btn_cpupower_apply)
        btn_cpupower_restore = QPushButton()
        btn_cpupower_restore.setObjectName("btn_cpupower_restore")
        btn_cpupower_restore.setStyleSheet(self.style_restore_action)
        btn_cpupower_restore.clicked.connect(lambda: self.run_cpupower("performance", self.texts[self.current_lang]['btn_cpupower_restore'])) # Düzeltme: Task adı dil bağımsız olmamalıydı
        cpu_button_layout.addWidget(btn_cpupower_restore)
        cpu_layout.addLayout(cpu_button_layout)
        
        # Swappiness Kontrolü (Yeni)
        swappiness_label = QLabel()
        swappiness_label.setObjectName("swappiness_label")
        swappiness_label.setWordWrap(True)
        cpu_layout.addWidget(swappiness_label)
        
        swappiness_button_layout = QHBoxLayout()
        btn_swappiness_apply = QPushButton()
        btn_swappiness_apply.setObjectName("btn_swappiness_apply")
        btn_swappiness_apply.setStyleSheet(self.style_apply_action)
        btn_swappiness_apply.clicked.connect(lambda: self.run_swappiness_control("10", self.texts[self.current_lang]['btn_swappiness_apply'])) # Düzeltme: Task adı dil bağımsız olmamalıydı
        swappiness_button_layout.addWidget(btn_swappiness_apply)
        btn_swappiness_restore = QPushButton()
        btn_swappiness_restore.setObjectName("btn_swappiness_restore")
        btn_swappiness_restore.setStyleSheet(self.style_restore_action)
        btn_swappiness_restore.clicked.connect(lambda: self.run_swappiness_control("60", self.texts[self.current_lang]['btn_swappiness_restore'])) # Düzeltme: Task adı dil bağımsız olmamalıydı
        swappiness_button_layout.addWidget(btn_swappiness_restore)
        cpu_layout.addLayout(swappiness_button_layout)
        
        layout.addWidget(cpu_group)
        layout.addStretch(1)
        return tab

    # --- İşlem Yürütme Fonksiyonları ---
    
    def run_garbage_privacy_cleanup(self):
        """Çöp ve Gizlilik temizleme işlemlerini sırayla yürütür."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        is_secure = self.chk_secure_delete.isChecked()
        
        # Düzeltme: Başlık mesajı aktif dilde olmalı
        secure_status = texts['chk_secure_delete'] if is_secure else texts['secure_group'].replace("Ayarları", "Pasif").replace("Settings", "Passive")
        self.log_message(texts['log_title_start'].format(secure_status))
        
        # Kullanıcının Ana Klasör yolu
        home = os.path.expanduser("~")

        # 1. DOSYA SİSTEMİ TEMİZLİĞİ (Yeni)
        
        # Kırık Sembolik Bağlantıları Sil
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_broken_links").isChecked():
            self.log_message(texts['log_msg_broken_links_search']) # Düzeltme: Aktif dil metni
            # Komut: find /home/<user> -xtype l -delete 
            try:
                subprocess.run(["find", home, "-xtype", "l", "-delete"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message(texts['log_msg_broken_links_success']) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_broken_links_error'].format(e)) # Düzeltme: Aktif dil metni

        # Boş Dizinleri Temizle
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_empty_dirs").isChecked():
            self.log_message(texts['log_msg_empty_dirs_search']) # Düzeltme: Aktif dil metni
            # Komut: find /home/<user> -type d -empty -delete
            try:
                # Önce alt dizinlerin silinmesi için 10 kat derinlikte çalıştırılır
                subprocess.run(["find", home, "-depth", "-type", "d", "-empty", "-delete"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message(texts['log_msg_empty_dirs_success']) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_empty_dirs_error'].format(e)) # Düzeltme: Aktif dil metni

        # Kullanıcı Kurulum Önbelleklerini Temizle
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_user_caches").isChecked():
            self.log_message(texts['log_msg_user_caches_search']) # Düzeltme: Aktif dil metni
            
            cache_dirs = [
                os.path.join(home, ".cache/snapd"), 
                os.path.join(home, ".cache/flatpak"),
                os.path.join(home, ".cache/thumbnails"), # Thumbnail temizlenmediyse ekstra koruma
                os.path.join(home, ".local/share/Trash/info"), # Çöp kutusu bilgi dosyaları
                # Diğer genel önbellekler eklenebilir
            ]
            
            deleted_count = 0
            for c_dir in cache_dirs:
                if os.path.exists(c_dir):
                    try:
                        # Dizin içeriğini sil, dizini değil
                        subprocess.run(["rm", "-rf", os.path.join(c_dir, "*")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        self.log_message(texts['log_msg_user_caches_cleaned'].format(c_dir)) # Düzeltme: Aktif dil metni
                        deleted_count += 1
                    except Exception as e:
                        self.log_message(texts['log_msg_user_caches_error'].format(c_dir, e)) # Düzeltme: Aktif dil metni
            
            self.log_message(texts['log_msg_user_caches_success'].format(deleted_count)) # Düzeltme: Aktif dil metni

        # 2. Çöp Kutusu Temizliği (Sadece Geçerli Kullanıcı)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_trash").isChecked():
            self.log_message(texts['log_msg_trash_empty']) # Düzeltme: Aktif dil metni
            
            try:
                trash_path = os.path.expanduser("~/.local/share/Trash/files")
                if not os.path.exists(trash_path):
                     self.log_message(texts['log_msg_trash_not_found']) # Düzeltme: Aktif dil metni
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
                    self.log_message(texts['log_msg_trash_success'].format(cleaned_count)) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_trash_error'].format(e)) # Düzeltme: Aktif dil metni

        # 3. ÖZEL GİZLİLİK TEMİZLİĞİ

        # Son Kullanılanlar (.xbel)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_xbel").isChecked():
            self.log_message(texts['log_msg_recent_xbel_clean']) # Düzeltme: Aktif dil metni
            self.clean_file(os.path.join(home, ".local/share/recently-used.xbel"), is_secure=is_secure)

        # RecentDocuments
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_docs").isChecked():
            self.log_message(texts['log_msg_recent_docs_clean']) # Düzeltme: Aktif dil metni
            self.clean_directory_contents(os.path.join(home, ".local/share/RecentDocuments"), is_secure=is_secure)

        # Genel Son Kullanılanlar Geçmişi (Yeni)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_recent_history").isChecked():
            self.log_message(texts['log_msg_recent_history_clean']) # Düzeltme: Aktif dil metni
            self.clean_file(os.path.join(home, ".local/share/zeitgeist/activity.sqlite"), is_secure=is_secure)
            self.clean_file(os.path.join(home, ".recently-used.xbel"), is_secure=is_secure) # Bazı eski sistemler için
        
        # thumbs.db (Home dizini içi)
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_db").isChecked():
            self.log_message(texts['log_msg_thumbs_db_search']) # Düzeltme: Aktif dil metni
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
                            self.log_message(texts['log_msg_thumbs_db_deleted'].format(full_path)) # Düzeltme: Aktif dil metni
                self.log_message(texts['log_msg_thumbs_db_success'].format(deleted_count)) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_thumbs_db_error'].format(e)) # Düzeltme: Aktif dil metni

        # 4. Küçük Resim (Thumbnail) Önbelleği
        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_large").isChecked():
            self.log_message(texts['log_msg_thumbs_large_clean']) # Düzeltme: Aktif dil metni
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/large"), is_secure=is_secure)

        if self.tab_garbage_widget.findChild(QCheckBox, "chk_thumbs_normal").isChecked():
            self.log_message(texts['log_msg_thumbs_normal_clean']) # Düzeltme: Aktif dil metni
            self.clean_directory_contents(os.path.join(home, ".cache/thumbnails/normal"), is_secure=is_secure)

        self.log_message(texts['log_title_end']) # Düzeltme: Aktif dil metni

    def secure_delete_file(self, filepath):
        """Dosyayı shred ile güvenli bir şekilde siler (3 geçiş)."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        if os.path.exists(filepath):
            try:
                # -f: force, -u: remove after overwriting, -n 3: 3 passes (default)
                subprocess.run(["shred", "-f", "-u", filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message(texts['log_msg_secure_success'].format(filepath)) # Düzeltme: Aktif dil metni
            except subprocess.CalledProcessError as e:
                self.log_message(texts['log_msg_secure_error'].format(filepath, e)) # Düzeltme: Aktif dil metni
            except FileNotFoundError:
                self.log_message(texts['log_msg_secure_shred_missing'].format(filepath)) # Düzeltme: Aktif dil metni
                self.clean_file(filepath, is_secure=False)
            except Exception as e:
                self.log_message(texts['log_msg_secure_unknown_error'].format(e)) # Düzeltme: Aktif dil metni
        else:
            self.log_message(texts['log_msg_secure_file_not_found'].format(filepath)) # Düzeltme: Aktif dil metni


    def clean_file(self, filepath, is_secure=False):
        """Belirtilen dosyayı normal veya güvenli şekilde siler ve günlük kaydı tutar."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        if os.path.exists(filepath):
            if is_secure:
                self.secure_delete_file(filepath)
                return
                
            try:
                os.remove(filepath)
                self.log_message(texts['log_msg_file_deleted'].format(filepath)) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_file_error'].format(filepath, e)) # Düzeltme: Aktif dil metni
        else:
            self.log_message(texts['log_msg_file_not_found'].format(filepath)) # Düzeltme: Aktif dil metni

    def clean_directory_contents(self, dirpath, is_secure=False):
        """Belirtilen dizinin içeriğini siler (dizini silmez)."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        if os.path.isdir(dirpath):
            try:
                count = 0
                for item in os.listdir(dirpath):
                    full_path = os.path.join(dirpath, item)
                    
                    if os.path.isdir(full_path) and not os.path.islink(full_path):
                        # Dizinler için rm -rf kullan, secure'a gerek yok
                        subprocess.run(["rm", "-rf", full_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        # Dosyalar için güvenli silme kullan
                        if is_secure:
                            self.secure_delete_file(full_path)
                        else:
                            os.remove(full_path)
                            
                    count += 1
                self.log_message(texts['log_msg_dir_contents_success'].format(dirpath, count)) # Düzeltme: Aktif dil metni
            except Exception as e:
                self.log_message(texts['log_msg_dir_contents_error'].format(dirpath, e)) # Düzeltme: Aktif dil metni
        else:
            self.log_message(texts['log_msg_dir_not_found'].format(dirpath)) # Düzeltme: Aktif dil metni
            
    # --- APT Temizliği ---

    def run_apt_cleanup(self):
        """APT temizlik komutlarını QProcess ile pkexec kullanarak yürütür."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        chk_autoremove = self.tab_apt_widget.findChild(QCheckBox, "chk_autoremove").isChecked()
        chk_autoclean = self.tab_apt_widget.findChild(QCheckBox, "chk_autoclean").isChecked()

        if not (chk_autoremove or chk_autoclean):
            # Düzeltme: Hata mesajı aktif dilde olmalı
            self.show_alert(texts['about_title'], 
                            texts['error_no_apt_selection'])
            return

        self.log_message(texts['log_title_apt_start']) # Düzeltme: Aktif dil metni

        # Düzeltme: Task adları aktif dilden alınmalı
        if chk_autoremove:
            self.execute_command_with_pkexec("/usr/bin/apt autoremove -y", texts['chk_autoremove'])

        if chk_autoclean:
            self.execute_command_with_pkexec("/usr/bin/apt autoclean", texts['chk_autoclean'])

    # --- Disk Birleştirme (Defrag) ---

    def run_defrag(self):
        """u4defrag komutunu QProcess ile pkexec kullanarak yürütür."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        self.log_message(texts['log_title_defrag_start']) # Düzeltme: Aktif dil metni
        # Düzeltme: Task adı aktif dilden alınmalı
        self.execute_command_with_pkexec("/usr/bin/u4defrag -s /", texts['btn_defrag'])

    # --- CPU Optimizasyonu (Apply ve Restore) ---

    def run_cpupower(self, governor, task_name):
        """cpupower komutunu QProcess ile pkexec kullanarak yürütür (powersave veya performance)."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        
        # Düzeltme: Log başlıkları aktif dilde olmalı
        if governor == "powersave":
            self.log_message(texts['log_title_cpu_save_start'])
        elif governor == "performance":
             self.log_message(texts['log_title_cpu_restore_start'])
             
        command = f"/usr/bin/cpupower frequency-set -g {governor}"
        self.execute_command_with_pkexec(command, task_name)
        
    # --- Swappiness Kontrolü (Yeni) ---
    
    def run_swappiness_control(self, value, task_name):
        """vm.swappiness ayarını QProcess ile pkexec kullanarak ayarlar."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        
        # Düzeltme: Log başlığı aktif dilde olmalı
        self.log_message(texts['log_title_swappiness_start'].format(value))
        # Kalıcı olmayan ayar: sysctl vm.swappiness=<value>
        command = f"sysctl vm.swappiness={value}" 
        self.execute_command_with_pkexec(command, task_name)

    # --- RAM Temizliği ---

    def run_ram_cleanup(self):
        """RAM önbelleği temizleme komutunu QProcess ile pkexec kullanarak yürütür."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        command = 'sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"'
        self.log_message(texts['log_title_ram_start']) # Düzeltme: Aktif dil metni
        self.execute_command_with_pkexec(command, texts['btn_ram_clean']) # Düzeltme: Task adı aktif dilden alınmalı

    # --- SWAP Temizliği (Yeni) ---

    def run_swap_cleanup(self):
        """Takas Alanını temizler (Swapoff ve Swapon)."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        self.log_message(texts['log_title_swap_start']) # Düzeltme: Aktif dil metni
        # Komut: swapoff -a && swapon -a
        # Bu işlem swap alanını kapatır, temizler ve tekrar etkinleştirir.
        command = 'sh -c "swapoff -a && swapon -a"'
        self.execute_command_with_pkexec(command, texts['btn_swap_clean']) # Düzeltme: Task adı aktif dilden alınmalı


    # --- QProcess Ortak Yürütme Fonksiyonu (PKEXEC) ---

    def execute_command_with_pkexec(self, command, task_name):
        """QProcess kullanarak pkexec ile bir komutu yürütür."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        
        if self.process and self.process.state() == QProcess.Running:
            # Düzeltme: Hata mesajı aktif dilde olmalı
            self.show_alert(texts['error_title'], 
                            texts['error_busy'])
            return

        if " " in command and not command.startswith("sh -c"):
            # Komutu pkexec ile düzgün çalıştırmak için tırnak içine al
            escaped_command = command.replace('"', '\\"')
            full_command = 'pkexec sh -c "{}"'.format(escaped_command)
        else:
            full_command = f'pkexec {command}'

        self.process = QProcess()
        
        # Sinyal bağlantıları
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        # Düzeltme: Task adı çeviriyi koruyarak pass-through yapılmalı
        self.process.finished.connect(lambda exitCode, exitStatus: self.handle_finished(exitCode, exitStatus, task_name))
        
        # Düzeltme: Başlatılıyor mesajı aktif dilde olmalı
        self.log_message(texts['log_msg_pkexec_start'].format(full_command))
        
        self.process.start("/bin/bash", ["-c", full_command])

    def handle_stdout(self):
        """Komutun standart çıktısını (stdout) okur ve günlüğe yazar."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        data = self.process.readAllStandardOutput().data().decode().strip()
        if data:
            self.output_log.append(texts['log_msg_stdout'].format(data)) # Düzeltme: Aktif dil metni

    def handle_stderr(self):
        """Komutun standart hata çıktısını (stderr) okur ve günlüğe yazar."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        data = self.process.readAllStandardError().data().decode().strip()
        if data:
            self.output_log.append(texts['log_msg_stderr'].format(data)) # Düzeltme: Aktif dil metni
            
    def handle_finished(self, exitCode, exitStatus, task_name):
        """Komutun tamamlanmasını işler."""
        texts = self.texts[self.current_lang] # Düzeltme: Aktif dil metinlerini al
        
        # Düzeltme: Bitiş mesajları aktif dilde olmalı. task_name zaten çevrilmiş metin olarak geliyor.
        if exitStatus == QProcess.NormalExit and exitCode == 0:
            self.log_message(texts['log_msg_process_success'].format(task_name, exitCode))
        else:
            self.log_message(texts['log_msg_process_error'].format(task_name, exitCode, exitStatus))

# --- Uygulama Başlatma ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LinuxCleanerApp()
    window.show()
    sys.exit(app.exec())
