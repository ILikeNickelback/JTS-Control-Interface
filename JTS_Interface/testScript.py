#Script to test data acquisition and plotting on JTS
from sequenceDecoder import sequenceDecoder
import time
import serial
import threading
from serialCommunication import adcCommunication



class testScript:
    def __init__(self):
        pass
    
    def test_sequence_decoder(self, sequence):
        decoded_sequence = sequenceDecoder(sequence)
        formated_sequence = decoded_sequence.formatSequence()
        decoded_sequence = decoded_sequence.decodeSequence(formated_sequence)
        print(decoded_sequence)
        return decoded_sequence

    
    def connect_to_arduino(self, port):
        ser = serial.Serial(port, 115200)
        time.sleep(2)
        return ser
    
    def send_sequence_to_arduino(self, sequence, arduino_serial):
        for item  in sequence:
            arduino_serial.write(item.encode())
        arduino_serial.write('\n'.encode())
        
    def read_from_arduino(self, arduino_serial, stop_event, nbr_of_points):
        i = 0
        while i < nbr_of_points:
            print(adcCommunication.get_triggered_value_from_adc())
            data = arduino_serial.readline().decode('utf-8').strip()
            print(data)
            i += 1
   
    def connect_to_adc(self):
        pass
    
    def test_data_acquisition(self):
        pass
    
    def test_plotting(self):
        pass
    
    


test = testScript()

sequence = "10(500msD)"
port = "COM4"


decoded_sequence = test.test_sequence_decoder(sequence)
arduino_serial = test.connect_to_arduino(port)

nbr_of_points = decoded_sequence.count('D')

stop_event = threading.Event()

serial_thread = threading.Thread(target = test.read_from_arduino, args=(arduino_serial, stop_event, nbr_of_points))
other_thread = threading.Thread(target = test.send_sequence_to_arduino, args=(decoded_sequence, arduino_serial))

serial_thread.start()
other_thread.start() 

serial_thread.join()
other_thread.join()
