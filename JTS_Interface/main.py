import sys
from PyQt5.QtWidgets import QApplication,QGraphicsView,QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PyQt5 import uic

from appFunctions import appFunctions
from graphFunctions import graphFunctions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('JTS_Designer.ui', self)
        
        #Create instances of the classes used in the application
        self.graph  = graphFunctions(self)
        self.app_functions = appFunctions(self)
        
        self.graph_widget = self.findChild(QWidget, 'graphWidget')  # 'graphWidget' is the object name from Designer
        
        # Set up the layout of the graph_widget to hold the canvas
        self.graph_widget.setLayout(self.graph.layout)
        
        #Add graph to the layout
        layout = QVBoxLayout()
        layout.addLayout(self.graph.layout)
        
        #Connect functions to the buttons
        self.start_button.clicked.connect(self.app_functions.start_acquisition)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
