import csv
from PyQt5.QtWidgets import QFileDialog, QWidget

"""
This class is used to manage the data acquired from the ESP32.
It allows to add, fetch, remove, show, hide and save the data to a CSV file.
Created: 03/2025 by Christopher
"""

#Does not work  yet
class dataManagement():
    def __init__(self):
        self.acquired_data = []
    
    def add_data(self, value_array, time_array):
        for t, v in zip(time_array, value_array):
            self.acquired_data.append((t, v))  # Store each pair as a tuple
    
    def fetch_data(self):
        return self.acquired_data
        
    def remove_data(self):
        pass
    
    def show_data(self):
        pass
    
    def hide_data(self):
        pass
    
    def save_data_to_csv(self):
        parent = QWidget()
        parent.hide()

        # Open a Save File dialog
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save CSV",
            "",
            "CSV files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        if not file_path.endswith('.csv'):
            file_path += '.csv'

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Value'])  # Header row
            for time, value in self.acquired_data:
                if time == 0:
                    writer.writerow(["New experiment", ''])
                    writer.writerow([time, value])
                else:
                    writer.writerow([time, value])