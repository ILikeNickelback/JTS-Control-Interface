from PyQt5.QtCore import QObject, QTimer
from Tools.workerThread import workerThread

class uiController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.app_functions = main_window.app_functions
        self.graph = main_window.graph
        self.esp32 = main_window.esp32

        self.acquisition_worker = None
        self.continues_value_worker = None

        self.connect_buttons()
        self.disable_buttons_if_needed()

    def connect_buttons(self):
        self.main_window.adjust_button.clicked.connect(self.graph.adjust_to_window)
        self.main_window.start_button.clicked.connect(self.start_acquisition_in_thread)
        self.main_window.stop_button.setEnabled(False)
        self.main_window.clear_button.clicked.connect(self.graph.clear_graph)
        self.main_window.save_data_button.clicked.connect(self.app_functions.save_data)
        self.main_window.start_continues_flash.clicked.connect(self.continues_value_thread)
        self.main_window.stop_continues_flash.clicked.connect(self.stop_continues_value_thread)
        self.main_window.stop_continues_flash.setEnabled(False)
        self.main_window.save_sequence.clicked.connect(self.app_functions.save_sequence)
        self.main_window.save_sequence.setEnabled(False)
        self.main_window.load_sequence.setEnabled(False)
        
    def disable_buttons_if_needed(self):
        if self.esp32.ser == None:
            self.main_window.adjust_button.setEnabled(False)
            self.main_window.start_button.setEnabled(False)
            self.main_window.clear_button.setEnabled(False)
            self.main_window.save_data_button.setEnabled(False)
            self.main_window.start_continues_flash.setEnabled(False)
            self.main_window.stop_continues_flash.setEnabled(False)
            

    def start_acquisition_in_thread(self):
        self.acquisition_worker = workerThread(self.app_functions.start_acquisition)
        self.acquisition_worker.abort_signal.connect(self.cleanup_acquisition_thread)
        self.acquisition_worker.start()
        
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.app_functions.update_progress_bar)
        self.progress_timer.start(100)  # update every 100 milliseconds
    

    def continues_value_thread(self):
        self.continues_value_worker = workerThread(self.app_functions.get_instant_values_from_adc)
        self.continues_value_worker.abort_signal.connect(self.cleanup_continues_value_thread)
        self.continues_value_worker.start()
    
    def stop_continues_value_thread(self):    
        self.app_functions.stop_continues_flashing()
             
    def cleanup_continues_value_thread(self):        
        if self.continues_value_worker:
            # self.continues_value_worker.wait()
            self.continues_value_worker.deleteLater()
            self.continues_value_worker = None
            print("Continues thread stopped")

    def cleanup_acquisition_thread(self):
        if self.acquisition_worker:
            # self.acquisition_worker.wait()
            self.acquisition_worker.deleteLater()
            self.acquisition_worker = None
            print("Acqistion thread stopped")
