import sys
from PyQt5.QtWidgets import QApplication, QLCDNumber, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QTabWidget

from PyQt5 import uic
import qdarkstyle

from appFunctions import appFunctions
from graphFunctions import graphFunctions
from workerThread import workerThread
from dataManagement import dataManagement

"""
This class is used to create the main window of the application.
I might move the button connection to an other class in the future.
Created: 03/2025 by Christopher
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.init_components()
        self.init_connections()
        
        self.acquisition_worker = None
        self.continues_value_worker  = None
        
    def setup_ui(self):
        uic.loadUi('JTS_Designer.ui', self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
    def init_components(self):    
        #Create instances of the classes used in the application
        self.data_management = dataManagement(self)
        self.graph  = graphFunctions(self)
        self.app_functions = appFunctions(self)

        
        self.graph_widget = self.findChild(QWidget, 'graphWidget')
             
        #Add graph to the layout
        layout = QVBoxLayout(self.graph_widget)
        layout.addWidget(self.graph)
        
    def init_connections(self):
        #Connect UI buttons to their respective functions
        self.adjust_button.clicked.connect(self.graph.adjust_to_window)
        self.start_button.clicked.connect(self.start_acquisition_in_thread)
        self.clear_button.clicked.connect(self.graph.clear_graph)
        self.save_data_button.clicked.connect(self.app_functions.save_data)
        self.start_continues_flash.clicked.connect(self.app_functions.start_continues_flashing)
        self.stop_continues_flash.clicked.connect(self.app_functions.stop_continues_flashing)

    def start_acquisition_in_thread(self):
        self.acquisition_worker = workerThread(self.app_functions.start_acquisition)
        self.acquisition_worker.abort_signal.connect(self.cleanup_acquisition_thread)
        self.acquisition_worker.start()
                
    def continues_value_thread(self):
        self.continues_value_worker = workerThread(self.app_functions.get_instant_values_from_adc)
        self.continues_value_worker.result_signal.connect(self.app_functions.update_lcd_value)
        self.continues_value_worker.start()
    
    def cleanup_acquisition_thread(self):
        print("Acquisition thread stopped and cleaned.")
        if self.acquisition_worker:
            self.acquisition_worker.deleteLater()
            self.acquisition_worker = None        
                 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    sys.exit(app.exec_())
