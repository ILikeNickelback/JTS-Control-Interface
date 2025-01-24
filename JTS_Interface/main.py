import sys
from mcculw import ul
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

Form, Window = uic.loadUiType("JTS_Designer.ui")

class MainWindow(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
