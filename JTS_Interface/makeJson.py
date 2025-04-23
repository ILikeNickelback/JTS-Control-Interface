import json

"""
This class is used to create a JSON file from a decoded sequence.
Not used yet, but it is a good idea to have it in case we need to save the configuration of the experiment.
Created: 03/2025 by Christopher
"""


class makeJson:
    def __init__(self, decodedSequence):
        remove = ['|', '^', '&']
        self.decodedSequence = [i for i in decodedSequence if i not in remove][2:]
        print(self.decodedSequence)
    
    def getConfig(self):
        experiment_header = {
            "Experiment title": "Fluo test with Pierre",
            "Experiment type": "Fluo",
            "Experiment date": "12/02/2025",
            "Total number of steps": int(len(self.decodedSequence)/2),
            "Averaging": 1,
            "Total time of experiment": str(self.calculateTotalTime()) + "ms",
        }
        
        sequence = []
        for i in range(0, len(self.decodedSequence), 2):
            step = {
                "Step number": (i // 2) + 1,
                "Dark time": self.decodedSequence[i] + "ms",
                "Action": self.decodedSequence[i + 1],
            }
            sequence.append(step)

        configuration = {
            "Experiment details": experiment_header,
            "Sequence": sequence
        }
    
        print(json.dumps(configuration, indent=4))
        self.saveConfigToJson(configuration)
        
    def saveConfigToJson(self, configuration):
        file_name = "experiment_configuration.json"
        with open(file_name, 'w') as json_file:
            json.dump(configuration, json_file, indent=4)
    
    def calculateTotalTime(self):
        dark_time = 0
        for i in range(0, len(self.decodedSequence), 2):
            dark_time += float(self.decodedSequence[i])
        return dark_time

# Test
a = makeJson(['1', '|', '0', '|', '&', '20.0', '^', 'A', '&', '500000.0', '^', 'D', '&', '0.5', '^', 'D', '&', '20.0', '^', 'A', '&', '500000.0', '^', 'D', '&', '0.5', '^', 'D'])
a.getConfig()
