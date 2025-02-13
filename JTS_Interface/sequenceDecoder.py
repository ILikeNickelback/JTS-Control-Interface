
import re # Regular expression library
import numpy as np


class sequenceDecoder:
    
    def __init__(self, sequence, mc = None, NbAcqu = 1, TimeBetweenAcqu = 0):
        self.sequence = ' ' + sequence
        self.mc = mc
        self.NbAcqu = NbAcqu
        self.TimeBetweenAcqu = TimeBetweenAcqu
        
    def readSequence(self):
        pattern = r'(\d+)\(([^)]+)\)' # Matches a number followed by a sequence in parentheses
        
        def replace_match(self):
            repetitions = int(self.group(1))
            sequence = self.group(2)
            return sequence * repetitions

        expanded_sequence = re.sub(pattern, replace_match, self.sequence)

        if expanded_sequence.find('(') != -1 or expanded_sequence.find(')') != -1:
            print("Invalid sequence: missing brackets or no instructions outside of brackets")
            
        print(expanded_sequence)
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
                if strChar:
                    listChar.append(strChar)
                    strChar = ""
            else:
                listChar.append(strChar)
                strChar = char

        # Filter empty strings and convert integers to actual int
        listInt = [int(i) for i in filter(None, listInt)]
        listChar = list(filter(None, listChar))

        # Define time multipliers based on first character of listChar
        time_multipliers = {'m': 1, 'M': 1, 'u': 1e-03, 'µ': 1e-03, 'U': 1e-03, 'n': 1e-03, 'N': 1e-03}
        listTime = [time_multipliers.get(c[0], 1) for c in listChar]

        # Compute expected points and prepare final result
        listExpPtsFloat = [float(i * t) for i, t in zip(listInt, listTime)]
        listChar = [c[1:] for c in listChar]

        # Prepare final output
        listFin = [str(self.NbAcqu), '|', str(self.TimeBetweenAcqu), '|']
        for exp_pts, char in zip(listExpPtsFloat, listChar):
            listFin.extend(['&', str(exp_pts), '^', char])

        print(listFin)

    
    def sendSequence(self):
        for j in range(len(listFin)):
            mc.write(listFin[j].encode())
        mc.write('\n'.encode())
    
sequence = "20msA3(500µsD)"
decoder = sequenceDecoder(sequence)
sequence = decoder.readSequence()
decoder.decodeSequence(sequence)
