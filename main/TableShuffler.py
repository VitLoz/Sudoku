from main import SudokuBase
from random import randint

class TableShuffler(SudokuBase):
    
    def __init__(self, table):
        self.table = table
        self.mixTable()

    def transposition(self):
        self.table= list(map(list, zip(*self.table)))

    def swapLocalRows(self):
        area, firstRow, secondRow = randint(0,2), 0, 0
        while firstRow == secondRow:
            firstRow, secondRow = area * 3 + randint(0,2), area * 3 + randint(0,2)
        self.table[firstRow], self.table[secondRow] = self.table[secondRow], self.table[firstRow]

    def swapTotalRows(self):
        firstArea, secondArea = randint(0,2), randint(0,2)
        while firstArea == secondArea:
            firstArea, secondArea = randint(0,2), randint(0,2)
        for row in range(3):
            self.table[firstArea*3 + row], self.table[secondArea*3 + row] = \
                                   self.table[secondArea*3 + row], self.table[firstArea*3 + row]

    def swapLocalCols(self):
        self.transposition()
        self.swapLocalRows()
        self.transposition()

    def swapTotalCols(self):
        self.transposition()
        self.swapTotalRows()
        self.transposition()

    def mixTable(self):
        mixFunctions = ["self.transposition()","self.swapLocalRows()",
                        "self.swapTotalRows()","self.swapLocalCols()","self.swapTotalCols()"]
       
        for i in range(21):
            rndFunc = randint(0,4)
            eval(mixFunctions[rndFunc])
