__package__

from Forms.Point import Point
from Forms.Reta import Reta
import numpy as np

class Quadrado():
    def __init__(self, x1 = 100, y1 = 100, x2 = 200, y2 = 200):
        self.pontos = []
        self.A = Point(x1,y1)
        self.B = Point(x2,y1)
        self.C = Point(x2,y2)
        self.D = Point(x1,y2)
        
    def drawPoints(self):
        lighted_pixels = []
        
        drawedPoints = []
        
        drawedPoints.append(Reta.pontoMedioStatic([self.A.X,self.A.Y,self.B.X,self.B.Y]))
        drawedPoints.append(Reta.pontoMedioStatic([self.B.X,self.B.Y,self.C.X,self.C.Y]))
        drawedPoints.append(Reta.pontoMedioStatic([self.C.X,self.C.Y,self.D.X,self.D.Y]))
        drawedPoints.append(Reta.pontoMedioStatic([self.D.X,self.D.Y,self.A.X,self.A.Y]))
        
        for i in drawedPoints:
            for j in i:
                lighted_pixels.append(j)

        return lighted_pixels
    
    def getPoints(self):
        return [self.A.getPointAsArray(),
                self.B.getPointAsArray(),
                self.C.getPointAsArray(),
                self.D.getPointAsArray()]
        
    def setPoints(self, newPoints):
        self.A.setPoints(newPoints[0][0], newPoints[0][1])
        self.B.setPoints(newPoints[1][0], newPoints[1][1])
        self.C.setPoints(newPoints[2][0], newPoints[2][1])
        self.D.setPoints(newPoints[3][0], newPoints[3][1])