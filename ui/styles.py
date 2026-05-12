"""Qt stylesheet tokens — lightweight enterprise skin."""

APP_STYLESHEET = """
/* Светлая область контента: явный цвет текста, иначе при системной тёмной теме Windows
   Qt даёт светлый WindowText на светлом фоне — заголовки и ячейки таблиц не видны. */
QStackedWidget#contentStack {
    background-color: #f4f6f8;
}
QStackedWidget#contentStack QLabel {
    color: #111827;
}
QStackedWidget#contentStack QLineEdit {
    color: #111827;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
}
QStackedWidget#contentStack QLineEdit:focus {
    border: 1px solid #2563eb;
}
QStackedWidget#contentStack QComboBox {
    color: #111827;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
}
QStackedWidget#contentStack QAbstractSpinBox {
    color: #111827;
    background-color: #ffffff;
}
QTableWidget {
    gridline-color: #e5e7eb;
    background-color: #ffffff;
    color: #111827;
}
QTableWidget::item {
    color: #111827;
}
QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #111827;
}
QHeaderView::section {
    background-color: #374151;
    color: #f9fafb;
    padding: 8px;
    border: none;
}
QMainWindow {
    background-color: #f4f6f8;
}
QFrame#sidebar {
    background-color: #1f2937;
    border: none;
}
QPushButton.nav {
    color: #e5e7eb;
    background-color: transparent;
    border: none;
    padding: 12px 18px;
    text-align: left;
    font-size: 14px;
}
QPushButton.nav:hover {
    background-color: #374151;
}
QPushButton.nav:checked {
    background-color: #111827;
    border-left: 4px solid #38bdf8;
}
QPushButton.action {
    background-color: #2563eb;
    color: white;
    padding: 8px 14px;
    border-radius: 6px;
}
QPushButton.action:disabled {
    background-color: #93c5fd;
}
QTableWidget {
    gridline-color: #e5e7eb;
    background-color: white;
}
QLabel.title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
}
"""
