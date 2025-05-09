import serial
import time
import ctypes
import numpy as np
import random

from mcculw import ul
from mcculw.enums import InterfaceType, TrigType, ULRange, ScanOptions, FunctionType, InfoType, BoardInfo, Status
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
    def __init__(self):
        ul.stop_background(board_num=1, function_type=FunctionType.AIFUNCTION)
        self.init_adc()

    def init_adc(self):
        self.board_num = 1 #Defined in Instacal
        self.samples_per_trigger = 8
        self.num_triggers = 10  # Total triggers you expect
        self.total_points = self.samples_per_trigger * self.num_triggers

        ul.set_config(
            info_type = InfoType.BOARDINFO,
            board_num = self.board_num,
            dev_num = 0,
            config_item = BoardInfo.ADTRIGCOUNT,
            config_val = 0)

        ul.set_trigger(
            board_num = self.board_num,
            trig_type = TrigType.TRIG_RISING,
            low_threshold = 0,
            high_threshold = 3
            )
        
        self.memhandle = ul.win_buf_alloc_32(self.total_points)
        self.data_array = ctypes.cast(self.memhandle, ctypes.POINTER(ctypes.c_ulong)) #create a pointer to the memory allocated  
            
        ul.a_in_scan(
            board_num = self.board_num,
            low_chan = 0,
            high_chan = 3,
            num_points  = 8,
            rate= 20000, 
            ul_range= ULRange.BIP10VOLTS,
            memhandle=self.memhandle,
            options= ScanOptions.RETRIGMODE | ScanOptions.CONTINUOUS |ScanOptions.BACKGROUND)

        self.current_trigger_index = 0
        
    def get_triggered_value_from_adc(self, experiment_type = 'Fluo' ):
        #This is the most critical function of the application. It is used to get the value from the ADC when the trigger is activated.
        #The memory allocation and pointer creation is essential to get the data from the ADC for some reason.
        if experiment_type == 'Fluo':
            status = Status.RUNNING
            while status == Status.RUNNING:
                status, cur_count, cur_index = ul.get_status(self.board_num, FunctionType.AIFUNCTION)
                print(f"Current count: {cur_count}, Current index: {cur_index}")
            

            offset = self.current_trigger_index * self.samples_per_trigger
            eng_units_values = []
            
            for i in range(offset, offset + self.samples_per_trigger):
                raw = self.data_array[i]
                voltage = ul.to_eng_units_32(
                    board_num=self.board_num,
                    ul_range=1,
                    data_value=raw
                )
                eng_units_values.append(voltage)
            print("Eng units values: ", eng_units_values)

            value_difference  = (np.mean(eng_units_values[4:8]) - np.mean(eng_units_values[0:3]))     
            print(value_difference) 


            self.current_trigger_index += 1
            
            return value_difference 

    def stop_acquisition(self):
        ul.stop_background(board_num=1, function_type=FunctionType.AIFUNCTION)
        ul.win_buf_free(self.memhandle)