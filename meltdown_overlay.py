import sys
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush

import sound_fx

class ScreenMeltdownOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        self.setCursor(Qt.CursorShape.BlankCursor)

        screen = QApplication.primaryScreen()
        geo = screen.geometry() if screen else QRectF(0, 0, 1366, 768)
        self.setGeometry(geo.toRect())
        self.sw = geo.width()
        self.sh = geo.height()

        # Phases:
        # 0: Blackout (3.0s)
        # 1: Scanning right -> left
        # 2: Scanning left -> right
        # 3: Done
        self.phase = 0
        self.beam_width = 80
        self.beam_x = float(self.sw)

        self.blackout_timer = QTimer(self)
        self.blackout_timer.setSingleShot(True)
        self.blackout_timer.timeout.connect(self.start_scan)

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)  # ~60 FPS
        self.anim_timer.timeout.connect(self.update_scan)

    def start_meltdown(self):
        self.showFullScreen()
        self.activateWindow()
        self.raise_()
        self.phase = 0
        self.update()
        # Exactly 3.0 seconds of total blackout
        self.blackout_timer.start(3000)

    def start_scan(self):
        self.phase = 1
        self.beam_x = float(self.sw)
        sound_fx.play("scan")
        self.anim_timer.start()

    def update_scan(self):
        speed = 22.0  # pixels per frame (~1300 px/sec)

        if self.phase == 1:
            # Moving Right to Left
            self.beam_x -= speed
            if self.beam_x <= -self.beam_width:
                self.phase = 2
                self.beam_x = -self.beam_width
                sound_fx.play("scan")
        elif self.phase == 2:
            # Moving Left to Right
            self.beam_x += speed
            if self.beam_x >= self.sw + self.beam_width:
                self.phase = 3
                self.anim_timer.stop()
                # Close application cleanly
                QTimer.singleShot(100, self.finish_meltdown)

        self.update()

    def finish_meltdown(self):
        self.close()
        QApplication.quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        if self.phase in (1, 2):
            # Draw glowing white vertical scanning beam
            bx = int(self.beam_x)
            bw = self.beam_width
            grad = QLinearGradient(bx, 0, bx + bw, 0)
            grad.setColorAt(0.0, QColor(255, 255, 255, 0))
            grad.setColorAt(0.25, QColor(220, 240, 255, 140))
            grad.setColorAt(0.5, QColor(255, 255, 255, 255))
            grad.setColorAt(0.75, QColor(220, 240, 255, 140))
            grad.setColorAt(1.0, QColor(255, 255, 255, 0))

            painter.fillRect(bx, 0, bw, self.sh, QBrush(grad))

            # Subtle CRT horizontal scanline overlay
            painter.setPen(QColor(0, 0, 0, 40))
            for y in range(0, self.sh, 4):
                painter.drawLine(bx, y, bx + bw, y)

        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ScreenMeltdownOverlay()
    overlay.start_meltdown()
    sys.exit(app.exec())