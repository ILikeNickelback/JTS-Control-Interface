import time
import numpy as np  

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget,QSpinBox

from sequenceDecoder import sequenceDecoder
from serialCommunication import esp32Communication, adcCommunication
from dataManagement import dataManagement



"""
This class contains the functions associated to the applications widgets.
Created: 03/2025 by Christopher
"""

class appFunctions:
    def __init__(self, main_app):
        self.main_app = main_app
        self.esp32 = esp32Communication(self)
        
        self.acquisition_worker = None
        self.reference_value = None
       
    def start_acquisition(self):
        self.x_values = []
        self.y_values = []
        self.time_between_points = [] 
        cumulated_time_difference = 0 
        
        #Get the sequence from the user, decode it and send it to the ESP32
        self.decoded_sequence, nbr_of_points, acquisition_type = self.get_sequence()
        
        #Sequence acquisition
        if acquisition_type == 'Sequence':
            for i in range(nbr_of_points):
                start_time  = time.time()
                value  = adcCommunication.get_triggered_value_from_adc(self)
                end_time  = time.time()

                time_difference = end_time - start_time
                
                if i != 0:
                    cumulated_time_difference += time_difference
                    
                self.x_values.append(value)
                self.y_values.append(cumulated_time_difference)
                
                print(i)
                
            #Save data to the data management class for later use (Not working yet)           
            self.main_app.data_management.add_data(self.x_values, self.y_values)
                
            #Plot points on the graph               
            self.main_app.graph.plot_graph(self.x_values, self.y_values, i) 
            


        #Frequency acquisition (Not working yet)
        if acquisition_type == 'Frequency':
            for i in range(nbr_of_points):
                start_time  = time.time()
                value  = adcCommunication.get_triggered_value_from_adc(self)
                end_time  = time.time()
                self.x_values.append(value)
   
    def start_continues_flashing(self):
        sequence = ['#']
        self.esp32.send_sequence(sequence)      
          
    def stop_continues_flashing(self):
        sequence = ['@']
        self.esp32.send_sequence(sequence)
        
    def get_instant_values_from_adc(self):
        self.instant_value =  adcCommunication.get_instant_value_from_adc(self)

    def get_sequence(self):
        acquisition_type = self.get_acquisition_type_from_user()
        if acquisition_type == 'Sequence':
            decoded_sequence, nbr_of_points = self.decode_sequence()
            return decoded_sequence, nbr_of_points, acquisition_type 
        
        if acquisition_type == 'Frequency':
            frequency, nbr_of_points = self.decode_frequency()
            return frequency, nbr_of_points, acquisition_type
       
    def get_acquisition_type_from_user(self):
        tab = self.main_app.findChild(QWidget, 'tabWidget')
        active_tab_index = tab.currentIndex()
        
        if active_tab_index == 0:
            return "Sequence"
        else:
            return "Frequency"
  
    def decode_sequence(self):
        #Decode and send the sequence acquistion to the ESP32  
        sequence_widget = self.main_app.findChild(QWidget, 'text_sequence')
        sequence = sequence_widget.toPlainText()
        decoder  = sequenceDecoder(sequence)
        formated_sequence = decoder.formatSequence()
        decoded_sequence = decoder.decodeSequence(formated_sequence)
        nbr_of_points = decoded_sequence.count('D')
        self.esp32.send_sequence(decoded_sequence)
        return decoded_sequence, nbr_of_points 
      
    def decode_frequency(self):
        #Decode and send the frequency acquisition to the ESP32
        frequency_widget = self.main_app.findChild(QSpinBox, 'text_frequency')
        nbr_of_points_widget = self.main_app.findChild(QSpinBox, 'text_nbr_of_points')
        frequency = int(frequency_widget.value())
        nbr_of_points = int(nbr_of_points_widget.value())
        sequence = ['F','&', str(frequency), '&', str(nbr_of_points)]
        self.esp32.send_sequence(sequence)
        return frequency, nbr_of_points

    def save_sequence(self):
        pass
    
    def load_sequence(self):
        pass
    
    def save_data(self):
        self.dataManagement.save_data_to_csv()
      
    def update_lcd_value(self):
        #Not working yet 
        self.reference_value.display(self.instant_value) 

    def stop_acquisition(self):
        #Not working yet    
        if self.acquisition_worker:
            self.acquisition_worker.abort()