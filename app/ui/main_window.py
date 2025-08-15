from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QSplitter
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BFB — BITS Form Builder")
        self.resize(1000, 700)

        central = QWidget()
        layout = QVBoxLayout(central)

        toolbar = QWidget()
        tb_layout = QVBoxLayout(toolbar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(6)
        tb_layout.addWidget(QPushButton("New"))
        tb_layout.addWidget(QPushButton("Open"))
        tb_layout.addWidget(QPushButton("Save"))
        tb_layout.addWidget(QPushButton("Publish"))

        splitter = QSplitter(Qt.Horizontal)
        left = QListWidget()
        left.addItem("Page 1")
        center = QListWidget()
        center.addItem("Single Line Text — " )
        right = QLabel("Field editor (select a field to edit)")
        right.setWordWrap(True)

        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(toolbar)
        layout.addWidget(splitter)

        self.setCentralWidget(central)
