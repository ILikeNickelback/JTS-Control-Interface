import sys
from PyQt5.QtWidgets import QApplication, QLCDNumber, QGraphicsView,QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PyQt5 import uic

from appFunctions import appFunctions
from graphFunctions import graphFunctions
from workerThread import workerThread

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
        
        self.reference_value = self.findChild(QLCDNumber,'reference_value')
        
        #Add graph to the layout
        layout = QVBoxLayout()
        layout.addLayout(self.graph.layout)
        
        #Connect functions to the buttons
        self.send_button.clicked.connect(self.send_sequence)
        self.start_button.clicked.connect(self.start_acquisition_in_thread)
        self.clear_button.clicked.connect(self.clear_graph_in_thread)
        self.stop_button.clicked.connect(self.abort_thread)
        #self.continues_value_thread()


        # Initialize worker variables to store references
        self.acquisition_worker = None
        self.clear_worker = None
        
    def send_sequence(self):
        self.app_functions.send_sequence()
    
    def start_acquisition_in_thread(self):
        self.acquisition_worker = workerThread(self.app_functions.start_acquisition)
        self.acquisition_worker.abort_signal.connect(self.cleanup_thread)
        self.acquisition_worker.start()
                
                 
    def clear_graph_in_thread(self):
        self.clear_worker = workerThread(self.graph.clear_graph)
        self.clear_worker.start()
        
    
    def continues_value_thread(self):
        self.continues_value_worker = workerThread(self.app_functions.get_instant_values_from_adc)
        self.continues_value_worker.result_signal.connect(self.update_lcd_value)
        self.continues_value_worker.start()
   
    def update_lcd_value(self, value):
        self.reference_value.display(value) 


    def cleanup_thread(self):
        workers_to_check = [self.acquisition_worker, self.clear_worker]
        for worker in workers_to_check:
            if worker:
                if worker.isRunning():
                    worker.quit()  # Request the thread to quit
                    worker.wait()  # Wait for the thread to finish
                worker.deleteLater()  # Clean up the worker

        self.worker = None
        self.clear_worker = None

    def abort_thread(self):
        if self.acquisition_worker and self.acquisition_worker.isRunning():
            self.acquisition_worker.quit()  # Call the abort method on the worker
            self.acquisition_worker.wait()
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
