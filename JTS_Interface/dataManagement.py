import csv

"""
This class is used to manage the data acquired from the ESP32.
It allows to add, fetch, remove, show, hide and save the data to a CSV file.
Created: 03/2025 by Christopher
"""

#Does not work  yet
class dataManagement():
    def __init__(self, main_app):
        self.acquired_data = []
    
    def add_data(self, time_array, value_array):
        self.acquired_data.append([time_array, value_array])
    
    def fetch_data(self):
        return self.acquired_data
        
    def remove_data(self):
        pass
    
    def show_data(self):
        pass
    
    def hide_data(self):
        pass
    
    def save_data_to_csv(self):
        file_name = 'C:/Users/Christopher/Desktop/Code/acquisition_data.csv'
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Acquisition', 'Time', 'Value'])
            
            for i, dataset in enumerate(self.acquired_data):
                time_array = dataset[0]
                value_array = dataset[1]
                for t, v in zip(value_array, time_array):
                    writer.writerow([i+1, t, v])