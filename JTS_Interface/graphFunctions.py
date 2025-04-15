import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class graphFunctions(QWidget):
    def __init__(self, parent=None):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        
        # Lists to store x and y values
        self.x_values = []
        self.y_values = []
        
    def plot_graph(self, values, nbr_of_points):

        self.x_values.append(nbr_of_points)  # Example x values (0 to 10)
        self.y_values.append(values)
        
       # Plot all points and lines (will automatically connect the points)
        self.ax.plot(self.x_values, self.y_values, 'bo--')  # 'bo--' for blue points with dashed lines
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        
        
        self.canvas.draw()


    def clear_graph(self):
        """Clear the graph by resetting the data and redrawing an empty plot."""
        # Clear the data lists
        self.x_values.clear()
        self.y_values.clear()

        # Clear the axes
        self.ax.clear()

        # Redraw the canvas to show an empty plot
        self.canvas.draw()