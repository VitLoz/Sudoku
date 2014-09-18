from main import BaseTableGenerator
from main import TableShuffler
from main import HiderCells

class SudokuMaker(object):
    
    def __init__(self, difficult):
        self.difficult = difficult

    def makeSudoku(self):
        baseTable = BaseTableGenerator()
        table = baseTable.getTable()

        shuffler = TableShuffler(table)
        table = shuffler.getTable()

        hider = HiderCells(table, self.difficult)
        self.visibleCells = hider.getVisibleCells()
        self.hiddentCells = hider.getHiddenCells()
        
        return hider.getTable()

    def getHidden(self):
        return self.hiddentCells

    def getVisible(self):
        return self.visibleCells
