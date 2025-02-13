import matplotlib
from PyQt5 import uic

class app_functions:
    def __init__(self):
        quper().__init__()
        uic.loadUi('JTS_Designer.ui', self)
    
    def get_sequence(self, table):
        rows, columns = table.rowCount(), table.columnCount()
        table_data = []

        for row in range(rows):
            row_data = []
            for column in range(columns):
                item = table.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            table_data.append(row_data)

        return table_data
    

        
    def save_sequence(self):
        pass
    
    def load_sequence(self):
        pass
    
    def fetch_data(self):
        pass


    