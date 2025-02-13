import pyqtgraph
import numpy as np

class Pyqt_Graph:
    def __init__(self):
        pass
    
    def plot(self):
        self.graph.show()
    
    def plot_graph(self):
        #Random data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        # Plot the data on the graph
        self.plot.plot(x, y, pen='r')  # 'r' stands for red color