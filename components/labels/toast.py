from PySide6.QtWidgets import QLabel, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QColor, QPainterPath
from enum import Enum


class ToastType(Enum):
    INFO = "#4CAF50"
    WARNING = "#FFC107"
    ERROR = "#d32f2f"


class Toast(QLabel):
    def __init__(self, parent: QWidget, message: str, duration_ms: int = 3000, type: ToastType = ToastType.INFO):
        super().__init__(parent)  # обычный child-виджет, без window flags
        self.setText(message)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bg_color = QColor(type.value)
        self._radius = 10

        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                background: transparent;
            }
        """)
        self.setContentsMargins(20, 10, 20, 10)

        self.adjustSize()
        self.parent_widget = parent
        self._margin = 20

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

        self._compute_positions()
        self.move(self.start_pos)
        self.raise_()   # поверх остальных детей в родителе
        self.show()

        self._slide_in()
        QTimer.singleShot(duration_ms, self._slide_out)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)

        painter.fillPath(path, self._bg_color)
        painter.end()

        super().paintEvent(event)

    def _compute_positions(self):
        """Координаты теперь ЛОКАЛЬНЫЕ — относительно parent_widget, а не экрана."""
        parent_width = self.parent_widget.width()

        end_x = parent_width - self.width() - self._margin
        end_y = self._margin

        # Не даём toast'у уехать за левый край, если он шире родителя
        end_x = max(end_x, self._margin)

        start_x = parent_width + 20  # чуть правее видимой области родителя
        start_y = end_y

        self.start_pos = QPoint(start_x, start_y)
        self.end_pos = QPoint(end_x, end_y)

    def _slide_in(self):
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(350)
        self.pos_anim.setStartValue(self.start_pos)
        self.pos_anim.setEndValue(self.end_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(350)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)

        self.group_in = QParallelAnimationGroup()
        self.group_in.addAnimation(self.pos_anim)
        self.group_in.addAnimation(self.opacity_anim)
        self.group_in.start()

    def _slide_out(self):
        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(350)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(self.start_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        opacity_anim.setDuration(350)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)

        self.group_out = QParallelAnimationGroup()
        self.group_out.addAnimation(pos_anim)
        self.group_out.addAnimation(opacity_anim)
        self.group_out.finished.connect(self.deleteLater)
        self.group_out.start()