import sys
from PyQt5.QtWidgets import QApplication, QLCDNumber, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QTabWidget

from PyQt5 import uic
import qdarkstyle

from CoreFunctions.appFunctions import appFunctions
from CoreFunctions.graphFunctions import graphFunctions
from Tools.dataManagement import dataManagement
from Tools.manageJson import manageJson
from CoreFunctions.serialCommunication import esp32Communication, adcCommunication
from CoreFunctions.simulated_serialCommunication import simulated_esp32Communication, simulated_adcCommunication
from CoreFunctions.uiController import uiController
from Tools.sequenceDecoder import sequenceDecoder
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
            self.adc = adcCommunication(self)
        else:
            self.esp32 = simulated_esp32Communication()
            self.adc = simulated_adcCommunication()
         
        self.json = manageJson()    
        self.sequence_decoder = sequenceDecoder(self)    
        self.data_management = dataManagement()
        self.app_functions = appFunctions(self)
        self.graph  = graphFunctions(self)
        self.ui_controller = uiController(self)
       
        
        
        self.graph_widget = self.findChild(QWidget, 'graphWidget')
        layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph)
    
    def closeEvent(self, event):
        # Close the serial connection when the application is closed
        if not self.simulation:
            self.esp32.close_serial_connection()
            self.adc.stop_acquisition()
        event.accept()    
                 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
