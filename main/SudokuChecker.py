class SudokuChecker(object):

    def __init__(self, table):
        self.table = table
        self.result = [45]
        
        self.checkRows()
        self.checkCols()
        self.checkArea(0, 0)
        self.checkArea(0, 3)
        self.checkArea(0, 6)
        self.checkArea(3, 0)
        self.checkArea(3, 3)
        self.checkArea(3, 6)
        self.checkArea(6, 0)
        self.checkArea(6, 3)
        self.checkArea(6, 6)

    def checkRows(self):
        for row in self.table:
            if sum(row) not in self.result:
                self.result.append(sum(row))

    def transposition(self):
        self.table= list(map(list, zip(*self.table))) 

    def checkCols(self):
        self.transposition()
        self.checkRows()
        self.transposition()

    def checkArea(self, x, y):
        totalSum = 0
        baseY = y
        for i in range(3):
            for j in range(3):
                totalSum += self.table[x][y]
                y += 1
            x += 1
            y = baseY
        
        if totalSum not in self.result:
            self.result.append(totalSum)

    def checkTable(self):
        return len(self.result) == 1
