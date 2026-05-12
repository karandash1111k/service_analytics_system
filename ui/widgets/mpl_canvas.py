"""Matplotlib canvas embedded into Qt."""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget


class MatplotlibPanel(QWidget):
    """Hosts a single matplotlib Figure inside a QWidget."""

    def __init__(self, figsize=(6.2, 3.8), dpi: int = 100, parent=None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def redraw(self) -> None:
        self.canvas.draw_idle()
