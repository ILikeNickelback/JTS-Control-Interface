
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget,QSpinBox, QMessageBox
"""
This class is used to decode the sequence of actions given by the use so that it can be sent to the ESP32.
Created: 03/2025 by Christopher
"""

class sequenceDecoder:
    
    def __init__(self, main_app, mc = None, NbAcqu = 1, TimeBetweenAcqu = 0):
        self.main_app = main_app
        
        self.mc = mc
        self.NbAcqu = NbAcqu
        self.TimeBetweenAcqu = TimeBetweenAcqu
        
    def get_total_number_of_points(self, nbr_of_points, experiment_type):
        if experiment_type == 'Fluo':
            NbAcqu = 8
        elif experiment_type == 'Spectro':
            NbAcqu = 16
            
        total_number_of_points = nbr_of_points * NbAcqu
        return total_number_of_points

    
    def formatSequence(self, sequence):
        self.sequence = ' ' + sequence
        
        pattern = r'(\d+)\(([^)]+)\)' # Matches a number followed by a sequence in parentheses
        
        def replace_match(self):
            repetitions = int(self.group(1))
            sequence = self.group(2)
            return sequence * repetitions

        expanded_sequence = re.sub(pattern, replace_match, self.sequence)

        if expanded_sequence.find('(') != -1 or expanded_sequence.find(')') != -1:
            print("Invalid sequence: missing brackets or no instructions outside of brackets")
            

        return  expanded_sequence
    
    def decodeSequence(self, sequence):
        sequence = sequence.replace(" ", "")
        new_sequence = []

        # Removing 's' based on preceding characters
        for i in range(1, len(sequence)):
            if sequence[i] == 's':
                if sequence[i - 1] in ('m', 'M', 'u', 'µ', 'U'):
                    new_sequence.append(sequence[:i] + sequence[i + 1:])
                else:
                    new_sequence.append(sequence[:i] + "S" + sequence[i + 1:])

        # Finalize the sequence
        sequence = sequence.replace("s", "") + '1'

        # Classify positions as integers or characters
        posInt, posChar = [], []
        for i, char in enumerate(sequence):
            (posInt if char.isdigit() else posChar).append(i)

        # Group integers and characters into lists
        listInt, listChar = [], []
        strInt, strChar = "", ""
        for char in sequence:
            if char.isdigit():
                strInt += char
            else:
                listInt.append(strInt)
                listChar.append(strChar)
                strChar = char
                strInt = ""
        listChar.append(strChar)
  
        # Filter empty strings and convert integers to actual int
        listInt = [int(i) for i in filter(None, listInt)]
        listChar = list(filter(None, listChar))

        # Define time multipliers
        time_multipliers = {'m': 1, 'M': 1, 'u': 1e-03, 'µ': 1e-03, 'U': 1e-03, 'n': 1e-06, 'N': 1e-06}
        listTime = []
        for i  in range(len(listChar)):
            if listChar[i] in time_multipliers:
                listTime.append(time_multipliers[listChar[i]])

        # Compute expected points and prepare final result
        listExpPtsFloat = [float(i * t) for i, t in zip(listInt, listTime)]
        
        #Does not work
        listChar = [''.join([char for char in c if char.isupper()]) for c in listChar]
        # Remove empty strings
        listChar = [c for c in listChar if c]
        
        # Prepare final output
        listFin = [str(self.NbAcqu), '|', str(self.TimeBetweenAcqu), '|']
        for exp_pts, char in zip(listExpPtsFloat, listChar):
            listFin.extend(['&', str(exp_pts), '^', char])
        
        return listFin
    
    def get_experiment_type_from_user(self):
        spectro_button = self.main_app.findChild(QWidget, 'spectro_button')
        fluo_button = self.main_app.findChild(QWidget, 'fluo_button')
        if spectro_button.isChecked():
            return "Spectro"
        elif fluo_button.isChecked():
            return "Fluo"
      
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
        formated_sequence = self.formatSequence(sequence)
        decoded_sequence = self.decodeSequence(formated_sequence)
        nbr_of_points = decoded_sequence.count('D')
        return decoded_sequence, nbr_of_points 
      
    def decode_frequency(self):
        #Decode and send the frequency acquisition to the ESP32
        frequency_widget = self.main_app.findChild(QSpinBox, 'text_frequency')
        nbr_of_points_widget = self.main_app.findChild(QSpinBox, 'text_nbr_of_points')
        frequency = int(frequency_widget.value())
        nbr_of_points = int(nbr_of_points_widget.value())
        sequence = ['F','T', str(frequency),'^', 'N', str(nbr_of_points), '^']
        return sequence, nbr_of_points
      
    def extract_cumulative_times_from_sequence(self, sequence):
        if sequence[0] == 'F':
            time_values = (float(1/int(sequence[2])) * 1000)
            cumulative_times = [0]
            for i in range(1, int(sequence[5])):
                cumulative_times.append(cumulative_times[i-1] + time_values)
                            

        else:        
            def is_float(s):
                try:
                    float(s)
                    return True
                except ValueError:
                    return False
                
            time_values =  [float(item) for item in sequence if is_float(item)]
            
            cumulative_times = []
            for i in range(2,len(time_values)):
                cumulative_times.append(sum(time_values[2:i]))
                       
        return cumulative_times
    
    def get_sequence(self):
        acquisition_type = self.get_acquisition_type_from_user()
        if acquisition_type == 'Sequence':
            decoded_sequence, nbr_of_points = self.decode_sequence()
            return decoded_sequence, nbr_of_points 
        
        if acquisition_type == 'Frequency':
            frequency, nbr_of_points = self.decode_frequency()
            return frequency, nbr_of_points