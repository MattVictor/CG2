__package__

class Point():
    def __init__(self, x, y):
        self.X = x
        self.Y = y
        
    def getPointAsArray(self):
        return [self.X,self.Y]
    
    def getPointAsTuple(self):
        return (self.X,self.Y)
    
    def setPoints(self, x, y):
        self.X = x
        self.Y = y
    
    