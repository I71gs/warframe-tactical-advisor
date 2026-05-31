from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel
)

import sys


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Warframe Tactical Advisor"
        )

        self.setMinimumSize(
            1000,
            700
        )

        label = QLabel(
            "Warframe Tactical Advisor"
        )

        self.setCentralWidget(
            label
        )


app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec()