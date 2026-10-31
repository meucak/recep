import sys
import os
import math
import fcntl
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QRect, QUrl
from PyQt6.QtGui import (
    QPainter, QImage, QColor, QFont, QFontDatabase,
    QDesktopServices, QLinearGradient, QBrush
)

import config
import sound_fx
from settings_dialog import SettingsDialog

SKIN_PATH = os.path.expanduser("~/.local/share/cs-bomb/c4_skin.jpeg")
FONT_PATH = "/usr/share/fonts/truetype/dseg/DSEG7Classic-Bold.ttf"

_lock_file = None

def acquire_instance_lock():
    global _lock_file
    try:
        _lock_file = open("/tmp/cs_bomb_game.lock", "w")
        fcntl.flock(_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (BlockingIOError, IOError):
        return False

class InvisibleButton(QPushButton):
    def __init__(self, key_name, parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.30);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.38);
            }
        """)

class DigitalTimerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.display_text = "00:30.00"
        self.is_defused = False
        self.is_flashing_red = False
        self.flash_state = True

        # Load DSEG7 font
        if os.path.exists(FONT_PATH):
            QFontDatabase.addApplicationFont(FONT_PATH)
        self.digit_font = QFont("DSEG7 Classic", 16, QFont.Weight.Bold)

    def set_time(self, mins, secs, centisecs, flash_red=False):
        self.display_text = f"{mins:02d}:{secs:02d}.{centisecs:02d}"
        self.is_flashing_red = flash_red
        self.update()

    def set_defused(self):
        self.is_defused = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w = self.width()
        h = self.height()

        # 1. Recessed dark glass background
        painter.fillRect(0, 0, w, h, QColor("#0c0202"))

        # Inner shadow / bezel border
        painter.setPen(QColor("#240505"))
        painter.drawRect(0, 0, w - 1, h - 1)

        painter.setFont(self.digit_font)

        # 2. Ghost unlit background segments (88:88.88)
        painter.setPen(QColor(36, 6, 6, 210))
        painter.drawText(QRect(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "88:88.88")

        # 3. Active lit segments
        if self.is_defused:
            # Brilliant green when defused
            painter.setPen(QColor("#25ff44"))
        elif self.is_flashing_red:
            glow = QColor("#ff1111") if self.flash_state else QColor("#770000")
            painter.setPen(glow)
        else:
            painter.setPen(QColor("#ff2222"))

        painter.drawText(QRect(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self.display_text)

        # 4. Subtle glass glare gradient reflection across top half
        glare = QLinearGradient(0, 0, 0, h // 2)
        glare.setColorAt(0.0, QColor(255, 255, 255, 30))
        glare.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(0, 0, w, h // 2, QBrush(glare))

        painter.end()

class CSBombGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C4 Tactical Bomb Defusal")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # 800 x 446 (Matches 2752x1536 aspect ratio)
        self.win_w = 800
        self.win_h = 446
        self.setFixedSize(self.win_w, self.win_h)

        # Center on primary screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.move((geo.width() - self.win_w) // 2, (geo.height() - self.win_h) // 2)

        # Load background skin image
        self.skin_img = None
        if os.path.exists(SKIN_PATH):
            orig = QImage(SKIN_PATH)
            self.skin_img = orig.scaled(
                self.win_w, self.win_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        # Load config
        self.cfg = config.load_config()
        self.remaining_time = float(self.cfg.get("duration", 30))
        self.entered_code = ""

        # States: "ARMED", "DEFUSED", "EXPLODING"
        self.state = "ARMED"
        self.explosion_frame = 0
        self.last_tick_sec = int(self.remaining_time)

        # Dragging support
        self.drag_position = None

        # Countdown Timer (50 FPS)
        self.game_timer = QTimer(self)
        self.game_timer.setInterval(20)
        self.game_timer.timeout.connect(self.update_game_tick)

        # Explosion Animation Timer
        self.explosion_timer = QTimer(self)
        self.explosion_timer.timeout.connect(self.update_explosion)

        self.setup_ui()
        sound_fx.ensure_sounds()
        self.game_timer.start()

    def setup_ui(self):
        sw = self.win_w
        sh = self.win_h
        scale_x = sw / 2752.0
        scale_y = sh / 1536.0

        # 1. Digital 7-Segment Screen (Perfect alignment over LED panel)
        sx = int(1140 * scale_x)
        sy = int(380 * scale_y)
        scw = int(525 * scale_x)
        sch = int(160 * scale_y)

        self.timer_widget = DigitalTimerWidget(self)
        self.timer_widget.setGeometry(sx, sy, scw, sch)

        # 2. Invisible Buttons (Perfect alignment on physical keypad keys)
        cols = [int(1215 * scale_x), int(1355 * scale_x), int(1495 * scale_x)]
        rows = [int(690 * scale_y), int(815 * scale_y), int(940 * scale_y), int(1065 * scale_y)]
        bw = int(105 * scale_x)
        bh = int(90 * scale_y)

        key_labels = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["CLR", "0", "ENT"]
        ]

        self.buttons = {}
        for r_idx, ry in enumerate(rows):
            for c_idx, cx in enumerate(cols):
                kname = key_labels[r_idx][c_idx]

                btn = InvisibleButton(kname, self)
                btn.setGeometry(cx, ry, bw, bh)

                if kname.isdigit():
                    btn.clicked.connect(lambda checked, d=kname: self.press_digit(d))
                elif kname == "CLR":
                    btn.clicked.connect(self.press_clear)
                elif kname == "ENT":
                    btn.clicked.connect(self.press_enter)

                self.buttons[kname] = btn

        # 3. Corner Buttons: Settings & Close
        self.settings_btn = QPushButton("⚙", self)
        self.settings_btn.setGeometry(sw - 68, 10, 26, 24)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 46, 0.65);
                color: #cdd6f4;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(250, 179, 135, 0.85);
                color: #11111b;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)

        self.close_btn = QPushButton("✕", self)
        self.close_btn.setGeometry(sw - 36, 10, 26, 24)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 46, 0.65);
                color: #f38ba8;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(243, 139, 168, 0.85);
                color: #11111b;
            }
        """)
        self.close_btn.clicked.connect(self.close)

    # --- Mouse Dragging Support ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # --- Keyboard Input Support ---
    def keyPressEvent(self, event):
        text = event.text()
        key = event.key()

        if text.isdigit() and len(text) == 1:
            self.press_digit(text)
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.press_enter()
            return

        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.press_clear()
            return

        if key == Qt.Key.Key_Escape:
            self.close()
            return

        super().keyPressEvent(event)

    # --- Keypad Handlers ---
    def press_digit(self, digit):
        if self.state != "ARMED":
            return
        self.cfg = config.load_config()
        target_code = str(self.cfg.get("code", "316931"))
        code_len = len(target_code) if target_code else 6

        if len(self.entered_code) < code_len:
            self.entered_code += digit
            sound_fx.play("beep")

            # Check immediately upon reaching code length!
            if len(self.entered_code) == code_len:
                self.check_entered_code()

    def press_clear(self):
        if self.state != "ARMED":
            return
        if self.entered_code:
            self.entered_code = ""
            sound_fx.play("beep")

    def press_enter(self):
        if self.state != "ARMED":
            return
        # If user presses enter with any code, check immediately!
        if len(self.entered_code) > 0:
            self.check_entered_code()

    def check_entered_code(self):
        self.cfg = config.load_config()
        target_code = str(self.cfg.get("code", "316931"))

        if self.entered_code == target_code:
            self.defuse_success()
        else:
            # Şifre yanlış girildiği anda direkt patla ve kapan
            self.trigger_explosion()

    # --- Game Logic & States ---
    def update_game_tick(self):
        if self.state != "ARMED":
            return

        self.remaining_time -= 0.02
        if self.remaining_time <= 0.0:
            self.remaining_time = 0.0
            # Süre dolduğunda direkt patla ve kapan
            self.trigger_explosion()
            return

        mins = int(self.remaining_time) // 60
        secs = int(self.remaining_time) % 60
        centisecs = int((self.remaining_time - int(self.remaining_time)) * 100)

        # Flashing under 10 seconds
        flash_red = self.remaining_time < 10.0
        if flash_red:
            period = 0.2 if self.remaining_time < 5.0 else 0.5
            self.timer_widget.flash_state = (self.remaining_time % period) < (period / 2)

        self.timer_widget.set_time(mins, secs, centisecs, flash_red=flash_red)

        curr_sec = int(self.remaining_time)
        if curr_sec != self.last_tick_sec:
            self.last_tick_sec = curr_sec
            sound_fx.play("tick")

    def defuse_success(self):
        if self.state != "ARMED":
            return
        self.state = "DEFUSED"
        self.game_timer.stop()
        sound_fx.play("defuse")

        self.timer_widget.set_defused()

        # Open Target URL
        url_str = self.cfg.get("url", "https://www.google.com")
        QDesktopServices.openUrl(QUrl(url_str))

        # Şifre başarılı girilip website açılınca uygulama kapansın
        QTimer.singleShot(600, self.close_and_quit)

    # --- Explosion Sequence ---
    def trigger_explosion(self):
        if self.state == "EXPLODING":
            return
        self.state = "EXPLODING"
        self.game_timer.stop()

        self.timer_widget.hide()
        for b in self.buttons.values():
            b.hide()
        self.settings_btn.hide()
        self.close_btn.hide()

        sound_fx.play("explode")

        # Kısa 3 karelik patlama efekti (3 x 180ms = ~540ms), ardından uygulama kapansın
        self.explosion_frame = 1
        self.explosion_timer.setInterval(180)
        self.explosion_timer.start()
        self.update()

    def update_explosion(self):
        self.explosion_frame += 1
        if self.explosion_frame > 3:
            self.explosion_timer.stop()
            self.close_and_quit()
        else:
            self.update()

    def close_and_quit(self):
        self.close()
        QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        w = self.width()
        h = self.height()

        if self.state == "EXPLODING":
            self.draw_extended_explosion(painter, w, h)
            painter.end()
            return

        # Draw original Gemini C4 image as background
        if self.skin_img and not self.skin_img.isNull():
            painter.drawImage(0, 0, self.skin_img)
        else:
            painter.fillRect(0, 0, w, h, QColor("#1c221c"))

        # Subtle dark border
        painter.setPen(QColor(0, 0, 0, 160))
        painter.drawRect(0, 0, w - 1, h - 1)
        painter.end()

    def draw_extended_explosion(self, painter, w, h):
        cx, cy = w // 2, h // 2

        if self.explosion_frame == 1:
            painter.fillRect(0, 0, w, h, QColor("#ffffff"))
            painter.setBrush(QColor("#fff5a0"))
            painter.setPen(Qt.PenStyle.NoPen)
            for i in range(16):
                ang = i * (2.0 * math.pi / 16)
                bx = cx + int(math.cos(ang) * 160)
                by = cy + int(math.sin(ang) * 120)
                painter.fillRect(bx - 30, by - 30, 60, 60, QColor("#ffaa00"))

        elif self.explosion_frame == 2:
            painter.fillRect(0, 0, w, h, QColor("#2b0800"))
            cols = [QColor("#ffffff"), QColor("#ffea00"), QColor("#ff8800"), QColor("#ff3300")]
            for x in range(30, w - 30, 24):
                for y in range(25, h - 25, 24):
                    d = math.hypot(x - cx, y - cy)
                    if d < 250:
                        c = cols[int(d / 65) % len(cols)]
                        painter.fillRect(x, y, 22, 22, c)

        elif self.explosion_frame == 3:
            painter.fillRect(0, 0, w, h, QColor("#190300"))
            cols = [QColor("#ffea00"), QColor("#ff5500"), QColor("#cc1100"), QColor("#222222")]
            for x in range(20, w - 20, 26):
                for y in range(20, h - 20, 26):
                    d = math.hypot(x - cx, y - cy)
                    if d < 300 and (x * 3 + y * 7) % 5 != 0:
                        c = cols[int(d / 75) % len(cols)]
                        painter.fillRect(x, y, 24, 24, c)

    def open_settings(self):
        was_running = self.game_timer.isActive()
        self.game_timer.stop()

        dlg = SettingsDialog(self)
        if dlg.exec():
            self.cfg = config.load_config()
            self.remaining_time = float(self.cfg.get("duration", 30))
            self.last_tick_sec = int(self.remaining_time)
            self.entered_code = ""

        if was_running and self.state == "ARMED":
            self.game_timer.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if "--settings" in sys.argv or "-s" in sys.argv:
        dlg = SettingsDialog()
        dlg.exec()
        sys.exit(0)

    if not acquire_instance_lock():
        print("CSBomb is already running.")
        sys.exit(0)

    game = CSBombGame()
    game.show()
    sys.exit(app.exec())
