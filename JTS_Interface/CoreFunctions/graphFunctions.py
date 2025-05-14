import numpy as np

from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QPen

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

"""
This class contains the functions that are used for plotting the data and manipulating the graph.
Created: 03/2025 by Christopher
"""


class graphFunctions(FigureCanvas):
    def __init__(self, main_app):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        
        self.main_app = main_app
        
        self.appFunctions = self.main_app.app_functions
        self.data_management = self.main_app.data_management
       
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
        self.ax.set_xlabel('Time (ms)')
        self.ax.set_ylabel('Value')
            
    def _init_interaction(self):
        self._is_panning = False
        self._last_mouse_pos = None 
        self._is_selecting = False
        self._selection_start = None
        self._selection_rect = None       
            
    def _init_data(self):
        self.x_values = []
        self.y_values = []
        
    def plot_graph(self, values, time,):
        self.x_values.clear()
        self.y_values.clear()
        
        self.x_values = values
        self.y_values = time
        
        self.ax.plot(self.y_values, self.x_values, 'ro--')   
        self.draw()
        
    def adjust_to_window(self):
        if not self.ax.lines:
            return
        
        all_x = np.concatenate([line.get_xdata() for line in self.ax.lines])
        all_y = np.concatenate([line.get_ydata() for line in self.ax.lines])
        
        if all_x.size == 0 or all_y.size == 0:
            return

        x_min, x_max = np.min(all_x), np.max(all_x)
        y_min, y_max = np.min(all_y), np.max(all_y)

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
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self._is_selecting = True
            self._selection_start = event.pos()
            self._selection_rect = self._selection_start
        elif event.button() == Qt.LeftButton:
            self._is_panning = True
            self._last_mouse_pos = event.pos()
                 
    def mouseReleaseEvent(self, event):
        if self._is_selecting and event.button() == Qt.LeftButton:
            self._is_selecting = False
            self.zoom_to_selection()
            self._selection_start = None
            self._selection_rect = None
            self.update()
        if event.button() == Qt.LeftButton:
            self._is_panning = False
            self._last_mouse_pos = None   
                 
    def mouseMoveEvent(self, event):
        if self._is_selecting and self._selection_start:
            self._selection_rect = event.pos()
            self.update()
            
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
        
    def zoom_to_selection(self):
        if not self._selection_start or not self._selection_rect:
            return

        x0, y0 = self._selection_start.x(), self._selection_start.y()
        x1, y1 = self._selection_rect.x(), self._selection_rect.y()

        if abs(x1 - x0) < 5 or abs(y1 - y0) < 5:  # prevent tiny clicks from triggering zoom
            return
        
        def widget_to_canvas(x, y):
            return x, self.height() - y
    
        x0_c, y0_c = widget_to_canvas(x0, y0)
        x1_c, y1_c = widget_to_canvas(x1, y1)

        # Convert canvas to data coordinates
        x0_data, y0_data = self.ax.transData.inverted().transform((x0_c, y0_c))
        x1_data, y1_data = self.ax.transData.inverted().transform((x1_c, y1_c))

        self.ax.set_xlim(min(x0_data, x1_data), max(x0_data, x1_data))
        self.ax.set_ylim(min(y0_data, y1_data), max(y0_data, y1_data))
        self.draw()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._is_selecting and self._selection_start and self._selection_rect:
            painter = QPainter(self)
            pen = QPen(Qt.red, 1, Qt.DashLine)
            painter.setPen(pen)
            rect = self._make_qrect(self._selection_start, self._selection_rect)
            painter.drawRect(rect)    
    
    def _make_qrect(self, p1, p2):
        return QRect(p1, p2).normalized()
               
    def clear_graph(self):
        self.ax.clear()

        self.ax.grid(True)
        self.ax.set_xlabel('Time (ms)')
        self.ax.set_ylabel('Value')
        
        self.draw()
