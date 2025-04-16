
from sequenceDecoder import sequenceDecoder
from serialCommunication import esp32Communication, adcCommunication
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
import time
"""
This class contains the functions associated to the applications widgets.
Created: 03/2025 by Christopher
"""

class appFunctions:
    def __init__(self, main_app):
        self.main_app = main_app
        self.esp32 = esp32Communication(self)
        
    def start_acquisition(self):
        
        #Get the sequence from the user, decode it and send it to the ESP32
        sequence = self.get_sequence_from_user()
        self.decoded_sequence = self.decode_sequence(sequence)
        self.esp32.send_sequence(self.decoded_sequence)
                    
        nbr_of_points = self.decoded_sequence.count('D')
        for i in range(nbr_of_points):
            value, point_time = adcCommunication.get_triggered_value_from_adc(self)
            if i == 0:
                cumulated_point_time = 0
            else:
                cumulated_point_time += point_time
            self.main_app.graph.plot_graph(value, cumulated_point_time, i)
            
    
    def get_triggered_values_from_adc(self):
        value = adcCommunication.get_triggered_value_from_adc(self)     
        return value
    
    def get_instant_values_from_adc(self):
        value = adcCommunication.get_instant_value_from_adc(self)
        return value

    def decode_sequence(self, sequence):
        decoded_sequence = sequenceDecoder(sequence)
        formated_sequence = decoded_sequence.formatSequence()
        decoded_sequence = decoded_sequence.decodeSequence(formated_sequence)
        return decoded_sequence
            
    def get_sequence_from_user(self):
        tab = self.main_app.findChild(QWidget, 'tabWidget')
        active_tab_index = tab.currentIndex()
        if active_tab_index == 0:     
            sequence = self.main_app.findChild(QWidget, 'tableWidget')
        else:
            plain_text_edit = self.main_app.findChild(QWidget, 'plainTextEdit')
            sequence = plain_text_edit.toPlainText()
        return sequence
    
    
    def acquire_point_from_adc(self):
        preactinic_value = adcCommunication.get_value_from_adc()
         
        
    def save_sequence(self):
        pass
    
    def load_sequence(self):
        pass
    
    def fetch_data(self):
        pass


    