import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget,QSpinBox, QMessageBox

from Tools.sequenceDecoder import sequenceDecoder
from Tools.manageJson import manageJson

from CoreFunctions.serialCommunication import  adcCommunication
import threading
"""
This class contains the functions associated to the applications widgets.
Created: 03/2025 by Christopher
"""

class appFunctions:
    def __init__(self, main_app):
        self.main_app = main_app

        self.esp32 = self.main_app.esp32
        self.adc = self.main_app.adc
        self.data_management = self.main_app.data_management
        self.json = self.main_app.json
        self.sequence_decoder = self.main_app.sequence_decoder
        
        self.acquisition_worker = None
        self.reference_value = None
        
        self.stop_event = threading.Event()
       
    def start_acquisition(self):
        self.main_app.start_button.setEnabled(False)
        
        self.voltage_values = []
        self.time_values = []
        
        #Get the sequence from the user, decode it and send it to the ESP32
        self.decoded_sequence, self.nbr_of_points = self.sequence_decoder.get_sequence()
        self.time_values = self.sequence_decoder.extract_cumulative_times_from_sequence(self.decoded_sequence)
        
        self.experiment_type = self.sequence_decoder.get_experiment_type_from_user()
        
        
        self.adc.init_adc(self.nbr_of_points, self.experiment_type)
        self.esp32.send_sequence(self.decoded_sequence)
        
        
        for i in range(self.nbr_of_points):
            absorbance  = self.adc.get_triggered_value_from_adc()
            self.voltage_values.append(absorbance)

        self.adc.stop_acquisition()
                 
        #Save data to the data management class for later use          
        self.main_app.data_management.add_data(self.voltage_values, self.time_values)
            
        #Plot points on the graph               
        self.main_app.graph.plot_graph(self.voltage_values, self.time_values) 
        
        self.main_app.start_button.setEnabled(True)       
   
    def start_continues_flashing(self):
        sequence = ['#']
        self.main_app.start_continues_flash.setEnabled(False)
        self.main_app.stop_continues_flash.setEnabled(True)
        self.main_app.start_button.setEnabled(False)
        self.esp32.send_sequence(sequence)
          
    def stop_continues_flashing(self):
        sequence = ['@']
        self.stop_event.set()
        time.sleep(1)
        self.main_app.start_continues_flash.setEnabled(True)
        self.main_app.stop_continues_flash.setEnabled(False)
        self.main_app.start_button.setEnabled(True)
        self.esp32.send_sequence(sequence)
        
    def get_instant_values_from_adc(self):
        self.start_continues_flashing()
        self.stop_event.clear()
        while not self.stop_event.is_set():
            self.instant_reference_value, self.instant_measurement_value =  self.adc.get_instant_value_from_adc()
            self.update_lcd_value()
            if self.main_app.simulation == True:
                time.sleep(1)
            
    def save_sequence(self):
        self.json.convertConfigToJson(self.decoded_sequence)
    
    def load_sequence(self):
        pass
    
    def save_data(self):
        if self.data_management.fetch_data() == []:
            self.display_message("No data to save.")
        else:
            self.data_management.save_data_to_csv()
    
    def update_progress_bar(self):
        point_number = self.adc.get_status()
        number_of_points = self.sequence_decoder.get_total_number_of_points(self.nbr_of_points, self.experiment_type)
        value = int((point_number / number_of_points) * 100)
        self.main_app.progress_bar.setValue(value)
         
    def update_lcd_value(self):
        self.main_app.reference_value.display(self.instant_reference_value)
        self.main_app.measuring_value.display(self.instant_measurement_value)
        
    def stop_acquisition(self):
        #Not working yet    
        if self.acquisition_worker:
            self.acquisition_worker.abort()
            self.adc.stop_acquisition()
            
    def display_message(self, message):
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()