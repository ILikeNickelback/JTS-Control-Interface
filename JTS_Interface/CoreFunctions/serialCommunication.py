import serial
import time
import ctypes
import numpy as np

from mcculw import ul
from mcculw.enums import InterfaceType, TrigType, ULRange, ScanOptions, FunctionType
from mcculw.device_info import DaqDeviceInfo


"""
This class is used to communicate with the Arduino board and the ADC.
It is mainly used to send the sequence of actions to the board and get data from the ADC.
Created: 03/2025 by Christopher
"""


class esp32Communication:
    #For the moment I'm using an arduino UNO R4 WiFi, but I will change it to an ESP32 later.
    def __init__(self, app_functions=None,
                 port='COM4',
                 baud_rate=115200,
                 timeout=1):
        self.app_functions = app_functions
        self.ser = None
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.open_serial_connection()

    def open_serial_connection(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2) 
            print(f"Connected to {self.port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Could not open serial port {self.port}: {e}")
            self.ser = None
        
    def send_sequence(self, sequence):
        self.ser.write('<'.encode())
        for item in sequence:
            self.ser.write(item.encode())
            time.sleep(0.001) # Wait for 1ms between each item 
        self.ser.write('>'.encode())
            
    def close(self):
        if self.is_open:
            self.ser.close()
            self.is_open = False
    
  
class adcCommunication: 
    def __init__(self, board_num = 1):
        self.board_num = board_num  #Defined in InstaCal
        ul.set_trigger(1, 14,3,4)   #Set trigger type of trigger (see documentation or go to function definition)
        
    def get_triggered_value_from_adc(self, experiment_type = 'Fluo'):
        #This is the most critical function of the application. It is used to get the value from the ADC when the trigger is activated.
        #The memory allocation and pointer creation is essential to get the data from the ADC for some reason.
        if experiment_type == 'Fluo':
            memhandle = ul.win_buf_alloc_32(8)  #Allocate memory for 8 points (4 channels, 2 points per channel)
            data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong)) #create a pointer to the memory allocated
            eng_units_values = []  
            
            ul.a_in_scan(board_num = 1, 
                        low_chan = 0,                       #First channel to read
                        high_chan = 3,                      #Last channel to read    
                        num_points = 8,                     #Number of points to read (4 channels, 2 points per channel)
                        rate = 50000,                       #Sampling rate (in Hz) ==> 1 point every 20us, one before and one after the trigger
                        ul_range = 1,                       #ADC range (0-10V)
                        memhandle = memhandle,              #Pointer to the memory allocated
                        options = ScanOptions.EXTTRIGGER    #Trigger on the rising edge of the signal
                        )             

            for i in range(8):
                #This is the conversion from the raw data to the engineering units (0-10V)
                eng_units_values.append(ul.to_eng_units_32(board_num=1, ul_range=1, data_value=data_array[i]))
            
            #Get the first 4 values (before the trigger) and the last 4 values (after the trigger)
            value_difference  = (np.mean(eng_units_values[4:8]) - np.mean(eng_units_values[0:3]))      
            
            #Free the memory allocated for the data
            ul.win_buf_free(memhandle)

            return value_difference 
            
        elif experiment_type == 'Spectro':
            memhandle = ul.win_buf_alloc_32(16)
            data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong))
            eng_units_values = []

            start_time  = time.time()
            ul.a_in_scan(board_num = 1,
                        low_chan = 0,
                        high_chan = 7,
                        num_points = 16,
                        rate = 50000,
                        ul_range = 1,
                        memhandle = memhandle,
                        options = ScanOptions.EXTTRIGGER)        
            end_time  = time.time()
            
            converstion_time_1 = time.time() 
            for i in range(16):
                eng_units_values.append(ul.to_eng_units_32(board_num=1, ul_range=1, data_value=data_array[i]))
            
               
            time_difference  = (end_time - start_time)
            
            
            value_difference  = (np.mean(eng_units_values[8:16]) - np.mean(eng_units_values[0:8]))
            
            
            ul.win_buf_free(memhandle)
            
            
            converstion_time_2 = time.time()
            
            print("Acquisition time: ", end_time - start_time)
            print("Conversion time: ", converstion_time_2 - converstion_time_1) 
            
            return value_difference, time_difference 
            