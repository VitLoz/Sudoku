from main import SudokuBase
from random import randint
from copy import deepcopy
from main import solver
from random import shuffle

class HiderCells(SudokuBase):

    def __init__(self, table, difficult):
        
        self.table = table
        self.difficult = difficult
        
        self.calcHiddenCellsAmount()
        self.hideCells()


    def calcHiddenCellsAmount(self):
        if self.difficult == 1: #Easy level
            self.hiddenCells = self.dimension ** 2 - randint(36,49)
        elif self.difficult == 2: #Normal level
            self.hiddenCells = self.dimension ** 2 - randint(32,35)
        elif self.difficult == 3: #Hard level
            self.hiddenCells = self.dimension ** 2 - randint(28,31)
        else: #Evil level
            self.hiddenCells = self.dimension ** 2 - randint(22,27)


    def hideCells(self):
        newTable = deepcopy(self.table)
        indexes = [[i,j] for i in range(9) for j in range(9)]
        shuffle(indexes)
        index, amount, memory = 0, 0, 0

        
        while amount != self.hiddenCells:
                        
            row, col = indexes[index]
            memory = self.table[row][col]
            self.table[row][col] = 0
            newTable[row][col] = 0
            
            solutions = 0
            for solution in solver.solve_sudoku((3, 3), self.table):
                solutions += 1
                
            if solutions != 1:
                newTable[row][col] = memory
                amount -= 1
                
            amount += 1
            index += 1
            if index > len(indexes)-1:
                index= 0
            self.table = deepcopy(newTable)



    def getHiddenCells(self):
        return self.hiddenCells

    def getVisibleCells(self):
        return self.dimension ** 2 - self.hiddenCells

