from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QDialogButtonBox, QLabel, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QFont

import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bomba Yapılandırması")
        self.setModal(True)
        self.setMinimumWidth(380)

        # Dark tactical theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'JetBrains Mono', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #cdd6f4;
                font-weight: 500;
            }
            QLineEdit, QSpinBox {
                background-color: #181825;
                color: #a6e3a1;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                selection-background-color: #f38ba8;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #89b4fa;
                background-color: #11111b;
            }
            QDialogButtonBox QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 80px;
                font-weight: 600;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #45475a;
                color: #ffffff;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #585b70;
            }
            QDialogButtonBox QPushButton:default {
                background-color: #a6e3a1;
                color: #11111b;
                border: 1px solid #a6e3a1;
            }
            QDialogButtonBox QPushButton:default:hover {
                background-color: #94e2d5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title_label = QLabel("⚙ C4 BOMB PROTOKOL AYARLARI")
        title_label.setStyleSheet("color: #fab387; font-weight: bold; font-size: 14px; letter-spacing: 1px;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 1. Target URL
        self.url_label = QLabel("&Hedef Web Bağlantısı (URL):")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://...")
        self.url_label.setBuddy(self.url_edit)
        form_layout.addRow(self.url_label, self.url_edit)

        # 2. Duration (seconds)
        self.duration_label = QLabel("&Geri Sayım Süresi:")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 300)
        self.duration_spin.setSuffix(" saniye")
        self.duration_label.setBuddy(self.duration_spin)
        form_layout.addRow(self.duration_label, self.duration_spin)

        # 3. 6-Digit Defusal Code
        self.code_label = QLabel("&Çözüm Şifresi (6 Hane):")
        self.code_edit = QLineEdit()
        self.code_edit.setMaxLength(6)
        regex = QRegularExpression("^[0-9]{6}$")
        self.code_edit.setValidator(QRegularExpressionValidator(regex, self))
        self.code_edit.setPlaceholderText("316931")
        self.code_label.setBuddy(self.code_edit)
        form_layout.addRow(self.code_label, self.code_edit)

        layout.addLayout(form_layout)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setText("Kaydet")
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("İptal")
        self.button_box.button(QDialogButtonBox.StandardButton.Save).setDefault(True)

        self.button_box.accepted.connect(self.save_and_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Load initial values
        self.load_current_values()

    def load_current_values(self):
        cfg = config.load_config()
        self.url_edit.setText(cfg.get("url", "https://www.google.com"))
        self.duration_spin.setValue(int(cfg.get("duration", 30)))
        self.code_edit.setText(str(cfg.get("code", "316931")))

    def save_and_accept(self):
        url = self.url_edit.text().strip()
        code = self.code_edit.text().strip()
        duration = self.duration_spin.value()

        if len(code) != 6:
            QMessageBox.warning(self, "Geçersiz Şifre", "Şifre tam olarak 6 haneli rakamdan oluşmalıdır!")
            return

        if not url:
            url = "https://www.google.com"
        elif not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url

        cfg = {
            "url": url,
            "duration": duration,
            "code": code,
            "max_attempts": 3
        }
        config.save_config(cfg)
        self.accept()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = SettingsDialog()
    if dlg.exec():
        print("Settings saved successfully!")