from PyQt5.QtCore import QThread, pyqtSignal

"""
This class is used to create a worker thread for the acquisition process.
Created: 03/2025 by Christopher
"""

class workerThread(QThread):
    result_signal = pyqtSignal(object)
    abort_signal = pyqtSignal()
        
    def __init__(self, target, *args):
        super().__init__()
        self.target = target
        self.args = args
        self.abort_flag = False
        self.points_acquired = 0 
        
    def run(self):
        while not self.abort_flag:
            result = self.target(*self.args)
            self.result_signal.emit(result)  # Emit the result after the task is done
            self.abort_flag = True
        self.abort_signal.emit()
        
    def abort(self):
        self.abort_flag = True