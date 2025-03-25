import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

"""
This script reads data from multiple CSV files created by the oscilloscope "RS-..." in a certain directory and plots the data.
Created: 03/2025 by Christopher
"""


# Function to load and process data from CSV files
def load_and_plot_csv_files(directory_path):
    # Pattern to match all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory_path, '*.csv'))
    
    # Initialize a plot
    plt.figure(figsize=(10, 6))
    
    # Loop through each CSV file and process it
    for csv_file in csv_files:
        try:
            # Read CSV file, skipping the first 26 lines (data starts at line 27)
            data = pd.read_csv(csv_file, header=None, skiprows=26)
            
            # Extract the first column (x_values) and second column (y_values)
            x_values = data[0].astype(float)  # First column (x-axis)
            y_values = data[1].astype(float)  # Second column (y-axis)
            
            # Plot the data, with x_values as x-axis and y_values as y-axis
            plt.plot(x_values, y_values, label=os.path.basename(csv_file))  # Label with filename
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    # Add labels and title to the plot
    plt.xlabel("X Values")
    plt.ylabel("Y Values")
    plt.title("Plot of Data from Multiple CSV Files")
    plt.legend()  # Show legend with file names
    plt.grid(True)
    plt.show()

# Specify the directory containing the CSV files
directory_path = "C:/Users/Christopher/Desktop/Oscillo"  # Change this path to the folder containing your CSV files

# Call the function to load data and plot
load_and_plot_csv_files(directory_path)
