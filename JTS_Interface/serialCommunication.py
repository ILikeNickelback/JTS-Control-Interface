import serial
import time
import math
import serial.tools.list_ports
from mcculw import ul
from mcculw.enums import InterfaceType, TrigType, ULRange, ScanOptions, FunctionType
from mcculw.device_info import DaqDeviceInfo
import ctypes as ctypes
from ctypes.wintypes import HGLOBAL
from ctypes.util import find_library

"""
This class is used to communicate with the Arduino board and the ADC.
It is used to send the sequence of actions to the board.
Created: 03/2025 by Christopher
"""


class esp32Communication:
    def __init__(self, app_functions):
        self.app_functions = app_functions
        self.ser = serial.Serial('COM4', 115200, timeout=1) 
        time.sleep(2)
        
    def send_sequence(self, sequence):
        self.ser.write('<'.encode())
        for item in sequence:
            for char in item:
                self.ser.write(char.encode())
                time.sleep(0.001)
        self.ser.write('>'.encode())
        
            
    def senf_start_signal(self):
        self.ser.write('S'.encode())
        
    def read_from_arduino(self):    
        if self.ser.in_waiting > 0: 
            print(self.ser.readline())
                
    def find_arduino_port(self, baud_rate):
        ports = serial.tools.list_ports.comports()
        for port_info in ports:
            port = port_info.device
            desc = port_info.description
            if 'Arduino' in desc:
                try:
                    ser = serial.Serial(port, baud_rate)
                    return ser
                except serial.SerialException as e:
                    print(f"Could not open port {port}: {e}")
                    continue
            
    def close(self):
        if self.is_open:
            self.ser.close()
            self.is_open = False
    
  
class adcCommunication(): 
    def __init__(self):
        self.board_num = 1 #Defined in InstaCal
        ul.set_trigger(1, 14,3,4)
        self.esp32 = esp32Communication()
        
    def get_instant_value_from_adc(self):
        value = ul.a_in_32(board_num = 1, channel = 0, ul_range = 1)
        eng_units_value = ul.to_eng_units_32(board_num = 1, ul_range = 1, data_value = value)
        return eng_units_value
        
    def get_triggered_value_from_adc(self, nbr_of_points):
        eng_units_values = []
        memhandle = ul.win_buf_alloc_32(2)
        data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong))
        i = 0
        ul.a_in_scan(board_num = 1, low_chan = 0, high_chan = 0,
                num_points = 2, rate = 50000, ul_range = 1,
                memhandle = memhandle, options = ScanOptions.EXTTRIGGER)
        i += 1
        eng_units_value_1 = ul.to_eng_units_32(board_num=1, ul_range=1, data_value=data_array[0])
        eng_units_value_2 = ul.to_eng_units_32(board_num=1, ul_range=1, data_value=data_array[1])
        eng_units_values.append((eng_units_value_2 - eng_units_value_1))      
    
        ul.win_buf_free(memhandle)
        data_array = None
        return eng_units_values