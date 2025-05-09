import sys
from PyQt5.QtWidgets import QApplication, QLCDNumber, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QTabWidget

from PyQt5 import uic
import qdarkstyle

from CoreFunctions.appFunctions import appFunctions
from CoreFunctions.graphFunctions import graphFunctions
from Tools.dataManagement import dataManagement
from CoreFunctions.serialCommunication import esp32Communication, adcCommunication
from CoreFunctions.simulated_serialCommunication import simulated_esp32Communication, simulated_adcCommunication
from CoreFunctions.uiController import uiController

"""
This class is used to start the application.
Created: 03/2025 by Christopher
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.simulation = False  # Set to True for simulation mode, False for real ESP32 communication
        self.init_components()

    def setup_ui(self):
        uic.loadUi('PyQtFiles\JTS_Designer.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def init_components(self):
        if not self.simulation:
            self.esp32 = esp32Communication(self)
            # self.adc = adcCommunication()
        else:
            self.esp32 = simulated_esp32Communication()
            self.adc = simulated_adcCommunication()
            
        self.data_management = dataManagement(self)
        self.app_functions = appFunctions(self)
        self.graph  = graphFunctions(self)
        self.ui_controller = uiController(self)    

        self.graph_widget = self.findChild(QWidget, 'graphWidget')
        layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph)
        
                 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    sys.exit(app.exec_())
