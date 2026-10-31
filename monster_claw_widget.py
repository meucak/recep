import sys
import math
import subprocess
import fcntl
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient
)

import sound_fx

_widget_lock = None

def acquire_widget_lock():
    global _widget_lock
    try:
        _widget_lock = open("/tmp/monster_claw_widget.lock", "w")
        fcntl.flock(_widget_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (BlockingIOError, IOError):
        return False

class MonsterEyesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toshi Monster Eyes")

        # Frameless, transparent, tool (hidden from taskbar, sits above desktop)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.widget_w = 120
        self.widget_h = 90

        # Position at top-right of primary screen
        screen = QApplication.primaryScreen()
        sw = screen.geometry().width() if screen else 1366
        self.setGeometry(sw - self.widget_w, 0, self.widget_w, self.widget_h)

        # Subtle Breathing / Pulsing Glow Animation
        self.pulse_phase = 0.0
        self.is_hovered = False

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(90)  # ~11 FPS (battery friendly)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start()

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def update_animation(self):
        self.pulse_phase += 0.12
        if self.pulse_phase > 2.0 * math.pi:
            self.pulse_phase -= 2.0 * math.pi
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            sound_fx.play("beep")
            subprocess.Popen(["/home/toshi/.local/bin/cs-bomb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        # Ignore double-click to prevent launching duplicate instances
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()

        # Pure transparent background - ONLY the 2 glowing eyes are drawn!
        pulse = (math.sin(self.pulse_phase) + 1.0) * 0.5  # 0.0 to 1.0
        base_alpha = 1.0 if self.is_hovered else (0.35 + 0.55 * pulse)

        # Eye 1 (Left eye) and Eye 2 (Right eye) in top-right area
        eye1_x, eye1_y = w - 75, 45
        eye2_x, eye2_y = w - 35, 38

        glow_intensity = 255 if self.is_hovered else int(220 * base_alpha)

        for ex, ey in [(eye1_x, eye1_y), (eye2_x, eye2_y)]:
            # 1. Soft Outer Crimson Glow
            rad_grad = QRadialGradient(ex, ey, 22)
            rad_grad.setColorAt(0.0, QColor(255, 45, 30, glow_intensity))
            rad_grad.setColorAt(0.45, QColor(255, 100, 10, int(glow_intensity * 0.55)))
            rad_grad.setColorAt(1.0, QColor(180, 0, 0, 0))
            painter.setBrush(QBrush(rad_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(ex - 22), int(ey - 22), 44, 44)

            # 2. Slanted Sharp Reptilian Eye Sclera / Iris
            painter.setBrush(QColor(255, 175, 40, glow_intensity))
            painter.drawEllipse(int(ex - 10), int(ey - 5), 20, 11)

            # 3. Vertical Black Slit Pupil
            pupil_w = 3 if self.is_hovered else 2
            painter.setBrush(QColor(8, 0, 4, 255))
            painter.drawEllipse(int(ex - pupil_w // 2), int(ey - 5), pupil_w, 11)

            # 4. White Specular Glint
            painter.setBrush(QColor(255, 255, 255, glow_intensity))
            painter.drawEllipse(int(ex - 4), int(ey - 3), 3, 3)

        painter.end()

if __name__ == "__main__":
    if not acquire_widget_lock():
        sys.exit(0)
    app = QApplication(sys.argv)
    widget = MonsterEyesWidget()
    widget.show()
    sys.exit(app.exec())
