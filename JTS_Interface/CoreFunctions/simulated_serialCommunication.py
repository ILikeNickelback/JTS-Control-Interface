import serial
import time
import ctypes
import numpy as np
import random

from mcculw import ul
from mcculw.enums import InterfaceType, TrigType, ULRange, ScanOptions, FunctionType
from mcculw.device_info import DaqDeviceInfo


"""
This class is used to communicate with the Arduino board and the ADC.
It is mainly used to send the sequence of actions to the board and get data from the ADC.
Created: 03/2025 by Christopher
"""


class simulated_esp32Communication:
    #For the moment I'm using an arduino UNO R4 WiFi, but I will change it to an ESP32 later.
    def __init__(self):
        self.ser = True
        
    def send_sequence(self, sequence):
        pass
    
    def close(self):
        pass
  
class simulated_adcCommunication: 
    def __init__(self):
        pass
    
    def init_adc(self, number_of_points, experiment_type):
        pass
        
    def get_triggered_value_from_adc(self):
        simulated_referecnce_value = random.randint(-10, 10)  # Simulate a random value for fluorescence
        simulated_measurement_value = random.randint(-10, 10)
        return simulated_referecnce_value, simulated_measurement_value 
    
    def stop_acquisition(self):
        pass
    
    def get_status(self):
        number = 10
        return number