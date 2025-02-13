import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PyQt5 import uic
from Graphics_functions import Pyqt_Graph
from App_functions import app_functions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('JTS_Designer.ui', self)

        #Add graph to the layout
        graphicsView = self.findChild(QWidget, 'graphicsView')
        self.plot = pg.PlotWidget()
        layout = QVBoxLayout(graphicsView)
        layout.addWidget(self.plot)
        Pyqt_Graph.plot_graph(self)
        
        #Fetch sequence from table
        self.fetchSequence.clicked.connect(self.fetch_data)  
    
    def fetch_data(self):
        tab = self.findChild(QWidget, 'tabWidget')
        active_tab_index = tab.currentIndex()
        
        if active_tab_index == 0:     
            sequence = self.findChild(QWidget, 'tableWidget')
            sequence_data = app_functions.get_sequence(self, sequence)
            print(sequence_data)
        else:
            sequence = self.findChild(QWidget, 'lineEdit')
            sequence_data = sequence.text()
            print(sequence_data)
        

    def send_sequence_to_arduino(self):
        pass
    
    
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
