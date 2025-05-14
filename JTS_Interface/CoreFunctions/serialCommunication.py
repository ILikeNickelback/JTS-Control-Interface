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
            
    def close_serial_connection(self):
        if self.ser.is_open:
            self.ser.close()
            self.is_open = False
    
  
class adcCommunication: 
    def __init__(self, main_app):
        self.memhandle = None
        self.main_app = main_app
        self.board_num = 1
        
        self.esp32 = self.main_app.esp32
        if Status.RUNNING:
            self.stop_acquisition()

    def init_adc(self, number_of_points, experiment_type):
        if experiment_type == 'Fluo':
            self.samples_per_trigger = 4
            number_of_channels = 4
        elif experiment_type == 'Spectro':
            self.samples_per_trigger = 8
            number_of_channels = 8
            
        self.num_triggers = number_of_points * 2  # Total triggers you expect
        self.total_points = self.samples_per_trigger * self.num_triggers
            
                        
        self.memhandle = ul.win_buf_alloc_32(self.total_points)
        self.data_array = ctypes.cast(self.memhandle, ctypes.POINTER(ctypes.c_ulong)) #create a pointer to the memory allocated  
        
        ul.set_config(
            info_type = InfoType.BOARDINFO,
            board_num = self.board_num,
            dev_num = 0,
            config_item = BoardInfo.ADTRIGCOUNT,
            config_val = self.samples_per_trigger
            )       

        ul.a_in_scan(
            board_num = self.board_num,
            low_chan = 0,
            high_chan = number_of_channels - 1,
            num_points  = self.total_points,
            rate = 1, #Ignored with EXT_CLOCK & must not be too high with EXTTRIGGER for some reason
            ul_range= ULRange.BIP10VOLTS,
            memhandle=self.memhandle,
            options=  ScanOptions.EXTTRIGGER | ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS |ScanOptions.RETRIGMODE)
        

            
        self.current_trigger_index = 0
        
    def get_status(self):
        status, cur_count, cur_index = ul.get_status(self.board_num, FunctionType.AIFUNCTION)
        return cur_count
         
    def get_triggered_value_from_adc(self):
        #This is the most critical function of the application. It is used to get the value from the ADC when the trigger is activated.
        #The memory allocation and pointer creation is essential to get the data from the ADC for some reason.
        new_curr_count = 0
        while new_curr_count < self.total_points:
            cur_count = self.get_status()
            # if cur_count != new_curr_count:
            #     print(f"Current count: {cur_count}")
            new_curr_count = cur_count
        offset = self.current_trigger_index * self.samples_per_trigger * 2
        eng_units_values = []
        
        for i in range(offset, offset + self.samples_per_trigger * 2):
            raw = self.data_array[i]
            voltage = ul.to_eng_units_32(
                board_num=self.board_num,
                ul_range=1,
                data_value=raw
            )
            eng_units_values.append(voltage)
        
        
        if self.samples_per_trigger == 4:
            first_trig_value = np.mean(eng_units_values[0:3])
            second_trig_value = np.mean(eng_units_values[4:8])
            absorbance  = second_trig_value - first_trig_value
        
        elif self.samples_per_trigger == 8:
            first_trig_value_reference = np.mean(eng_units_values[0:3])
            second_trig_value_reference = np.mean(eng_units_values[8:12])
            reference_value = second_trig_value_reference - first_trig_value_reference
            
            first_trig_value_measurement = np.mean(eng_units_values[4:7])
            second_trig_value_measurement = np.mean(eng_units_values[13:15])
            measurement_value = second_trig_value_measurement - first_trig_value_measurement
                           
            absorbance = reference_value/(measurement_value + reference_value)
              

        
        self.current_trigger_index += 1
        
        return absorbance 
        

    def get_instant_value_from_adc(self):
        self.memhandle = ul.win_buf_alloc_32(8)
        self.data_array = ctypes.cast(self.memhandle, ctypes.POINTER(ctypes.c_ulong)) #create a pointer to the memory allocated             
        eng_units_values = []
        
        ul.a_in_scan(
            board_num = self.board_num,
            low_chan = 0,
            high_chan = 7,
            num_points  = 8,
            rate = 1, #Ignored with EXT_CLOCK & must not be too high with EXTTRIGGER for some reason
            ul_range= ULRange.BIP10VOLTS,
            memhandle=self.memhandle,
            options = ScanOptions.EXTTRIGGER)
        
        for i in range(8):
            raw = self.data_array[i]
            voltage = ul.to_eng_units_32(
                board_num=self.board_num,
                ul_range=ULRange.BIP10VOLTS,
                data_value=raw
            )
            eng_units_values.append(voltage)
        
        reference_value = np.mean(eng_units_values[0:3])
        measurement_value = np.mean(eng_units_values[4:7])
        
             
        ul.win_buf_free(self.memhandle)
        self.data_array = None
        
        return reference_value, measurement_value

    def stop_acquisition(self):
        ul.stop_background(board_num=1, function_type=FunctionType.AIFUNCTION)
        if self.memhandle:
            ul.win_buf_free(self.memhandle)