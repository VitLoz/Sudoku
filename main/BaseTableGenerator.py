from main import SudokuBase

class BaseTableGenerator(SudokuBase):
    
    def __init__(self):
        self.table= []
        self.tableBaseInit()
    

    def makeRow(self, shift):
        newRowLeft = [i for i in range(shift, self.dimension + 1)]
        newRowRight = [i for i in range(1, shift)]
        return newRowLeft + newRowRight


    def make2DTable(self):
        middle, result = [], []
        for i in range(0, self.dimension ** 2):
            middle.append(self.table[i])
            if len(middle) == 9:
                result.append(middle)
                middle = []
        self.table = result


    def tableBaseInit(self):
        shifts = [1,4,7,2,5,8,3,6,9]
        for shift in shifts:
            self.table += self.makeRow(shift)
        self.make2DTable()
