import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import Qt

class graphFunctions(FigureCanvas):
    def __init__(self, parent=None):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
       
        self._init_ui()
        self._init_interaction()
        self._init_data()
       
    def _init_ui(self):
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()
        self.setMouseTracking(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self)

        self.ax.grid(True)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')
            
    def _init_interaction(self):
        self._is_panning = False
        self._last_mouse_pos = None        
            
    def _init_data(self):
        self.x_values = []
        self.y_values = []
        

    def plot_graph(self, values, nbr_of_points, i):
        if i == 0:
            self.x_values.clear()
            self.y_values.clear()
        
        self.x_values.append(nbr_of_points)
        self.y_values.append(values)
        
        self.ax.plot(self.x_values, self.y_values, 'ro--')   
        self.draw()
        
    def adjust_to_window(self):
        if not self.x_values or not self.y_values:
            return  # No data to adjust
        
        # Get data bounds
        x_min, x_max = min(self.x_values), max(self.x_values)
        y_min, y_max = min(self.y_values), max(self.y_values)

        # Add a small margin
        x_margin = (x_max - x_min) * 0.05 if x_max != x_min else 1
        y_margin = (y_max - y_min) * 0.1 if y_max != y_min else 1

        self.ax.set_xlim(x_min - x_margin, x_max + x_margin)
        self.ax.set_ylim(y_min - y_margin, y_max + y_margin)

        self.fig.tight_layout()
        self.draw()
        
    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        self.zoom(zoom_in)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = True
            self._last_mouse_pos = event.pos()   
                 
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = False
            self._last_mouse_pos = None   
                 
    def mouseMoveEvent(self, event):
        if self._is_panning and self._last_mouse_pos:
            delta = event.pos() - self._last_mouse_pos
            dx = delta.x()
            dy = delta.y()

            # Get current axes limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Convert pixel movement to data coordinates
            width = self.width()
            height = self.height()

            if width == 0 or height == 0:
                return

            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]

            dx_data = -dx * (x_range / width)
            dy_data = dy * (y_range / height)  # invert Y to match screen movement

            # Update limits
            self.ax.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
            self.ax.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)

            self._last_mouse_pos = event.pos()
            self.draw()
        
    def zoom(self, zoom_in=True, factor=0.9):

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Calculate range
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]

        # Zoom factor
        zoom_factor = factor if zoom_in else 1 / factor

        # Find center
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        # Calculate new limits
        new_xlim = [x_center - x_range * zoom_factor / 2,
                    x_center + x_range * zoom_factor / 2]
        new_ylim = [y_center - y_range * zoom_factor / 2,
                    y_center + y_range * zoom_factor / 2]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.draw()
            
    def clear_graph(self):
        """Clear the graph by resetting the data and redrawing an empty plot."""
        # Clear the data lists
        self.x_values.clear()
        self.y_values.clear()

        # Clear the axes
        self.ax.clear()

        # Redraw the canvas to show an empty plot
        self.ax.grid(True)
        self.draw()
