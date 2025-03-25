import sys
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
        self.parent = parent

    def plot_graph(self, values):
        self.ax.clear()
        x = np.linspace(0, 10, 10)
        y = values
        self.ax.plot(x, y, 'bo--')
        self.canvas.draw()
