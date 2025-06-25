__package__

import numpy as np

class Transform2D():
    def __init__(self):
        self.explanationTest = ""
    
    def homogenCoordinates(self,points):
        homogenCoords = []
        
        self.explanationTest += "Primeiro Homogenizamos as coordenadas, adicionando 1 como uma coordenada adicional: \n\n"
        
        for x,y in points:
            homogenCoords.append([x,y,1])
            
        self.explanationTest += f"Novos pontos homogenizados: {homogenCoords}\n"
            
        return homogenCoords
            
    def multiplyMatrix(self,matrix1,matrix2):
        newPosition = []
        
        print(matrix2)
        
        for point in matrix2:
            newPoint = []
            self.explanationTest += "["
            for i in range(len(matrix1)):
                self.explanationTest += "("
                value = 0
                for j in range(len(point)):
                    value += matrix1[i][j] * point[j]
                    self.explanationTest += f" {matrix1[i][j]:.3f} * {point[j]:.3f}"
                    if(j != (len(point)-1)):
                        self.explanationTest += " + "
                
                self.explanationTest += ")"
                
                if(j != (len(matrix1)-1)):
                        self.explanationTest += ","
                
                newPoint.append(value)
            
            self.explanationTest += "]\n"
            
            self.explanationTest += f"= {newPoint}\n\n"
            newPosition.append((round(newPoint[0]), round(newPoint[1])))
            
        return newPosition
                
                
    def transposition(self, points, movedPoints):
        newPosition = points
        
        self.explanationTest += "Transposição: \n\n"
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(newPosition)
        
        self.explanationTest += "Utilizamos da matriz: \n[1, 0, x]\n[0, 1, y]\n[0, 0, 1]\n\n"
        
        #matriz para transposição
        transpositionMatrix = [
            [1, 0, movedPoints[0]],
            [0, 1, movedPoints[1]],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(transpositionMatrix, homogenCoords)
        
        self.explanationTest += f"Por fim temos os novos pontos transladados: {newPosition}\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n"
        
        return newPosition

    def scale(self, points, movedPoints):
        newPosition = points
        
        self.explanationTest += "Escala: \n\n"
        
        transpositionPoints = newPosition[0]
        
        self.explanationTest += "Primeiro Precisamos transladar o ponto para a origem, para evitar erros na hora da operação: \n"
        
        newPosition = self.transposition(newPosition, [transpositionPoints[0]*-1,transpositionPoints[1]*-1])
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(newPosition)
        
        self.explanationTest += "Utilizamos da matriz: \n[x, 0, 0]\n[0, y, 0]\n[0, 0, 1]\n\n"
        
        #matriz para escala
        scaleMatrix = [
            [movedPoints[0], 0, 0],
            [0, movedPoints[1], 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(scaleMatrix, homogenCoords)
        
        self.explanationTest += "Depois trazemos objeto de volta ao ponto anterior com outra Transladação\n"
        
        newPosition = self.transposition(newPosition, transpositionPoints)
        
        return newPosition
    
    def rotation(self, points,angle,x,y):
        newPosition = points
        
        self.explanationTest += "Rotação: \n\n"
        
        reposition = False
        
        if (x != 0) or (y != 0):
            self.explanationTest += "Primeiro Precisamos transladar o ponto para a origem, para evitar erros na hora da operação: \n\n"
            reposition = True
            transpositionPoints = newPosition[0]
        
            newPosition = self.transposition(newPosition, [transpositionPoints[0]*-1,transpositionPoints[1]*-1])
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(newPosition)
            
        theta = np.radians(angle)
        
        self.explanationTest += f"Utilizamos da matriz: \n[cos({theta}), -sen({theta}), 0]\n[sen({theta}), cos({theta}), 0]\n[0, 0, 1]\n\n"
        
        #matriz para Rotação
        rotationMatrix = [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(rotationMatrix, homogenCoords)
        
        if reposition:
            self.explanationTest += "Depois trazemos objeto de volta ao ponto anterior, com outra Transladação\n"
            newPosition = self.transposition(newPosition, transpositionPoints)

        self.explanationTest += f"Por fim temos os novos pontos Rotacionados: {newPosition}\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n"
        
        return newPosition
    
    def reflectionX(self, points):
        newPosition = points
        
        self.explanationTest += "Reflexão em X: \n\n"
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(points)
        
        self.explanationTest += "Utilizamos da matriz: \n[1, 0, 0]\n[0, -1, 0]\n[0, 0, 1]\n\n"
        
        #matriz para Reflexão em X
        reflectioMatrix = [
            [1, 0, 0],
            [0, -1, 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(reflectioMatrix, homogenCoords)
        
        self.explanationTest += f"Por fim temos os novos pontos Refletidos: {newPosition}\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n"
        
        return newPosition
    
    def reflectionY(self, points):
        newPosition = points
        
        self.explanationTest += "Reflexão em Y: \n\n"
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(points)
        
        self.explanationTest += "Utilizamos da matriz: \n[-1, 0, 0]\n[0, 1, 0]\n[0, 0, 1]\n\n"
        
        #matriz para Reflexão em Y
        reflectioMatrix = [
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(reflectioMatrix, homogenCoords)
        
        self.explanationTest += f"Por fim temos os novos pontos Refletidos: {newPosition}\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n"
        
        return newPosition
    
    def schear(self, points, x, y):
        newPosition = points
        
        self.explanationTest += "Cisalhamento: \n\n"
        
        transpositionPoints = newPosition[0]
        
        self.explanationTest += "Primeiro Precisamos transladar o ponto para a origem, para evitar erros na hora da operação: \n\n"
        
        newPosition = self.transposition(newPosition, [transpositionPoints[0]*-1,transpositionPoints[1]*-1])
        
        if x != 0:
            newPosition = self.schearX(newPosition,x)
        if y != 0:
            newPosition = self.schearY(newPosition,y)
            
        self.explanationTest += "Depois trazemos objeto de volta ao ponto anterior, com outra Transladação\n"
            
        newPosition = self.transposition(newPosition, transpositionPoints)
        
        self.explanationTest += f"Por fim temos os novos pontos Cisalhados: {newPosition}\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n\n"
            
        return newPosition
    
    def schearX(self, points, value):
        newPosition = points
        
        self.explanationTest += "Cisalhamento em X: \n\n"
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(points)
        
        self.explanationTest += "Utilizamos da matriz: \n[1, x, 0]\n[0, 1, 0]\n[0, 0, 1]\n\n"
        
        #matriz para Cisalhamento em X
        schearMatrix = [
            [1, value, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(schearMatrix, homogenCoords)
        
        return newPosition
    
    def schearY(self, points, value):
        newPosition = points
        
        self.explanationTest += "Cisalhamento em Y: \n\n"
        
        #transformando em coordenadas homogêneas
        homogenCoords = self.homogenCoordinates(points)
        
        self.explanationTest += "Utilizamos da matriz: \n[1, 0, 0]\n[y, 1, 0]\n[0, 0, 1]\n\n"
        
        #matriz para Cisalhamento em Y
        schearMatrix = [
            [1, 0, 0],
            [value, 1, 0],
            [0, 0, 1]
        ]
        
        self.explanationTest += "Para definir as novas coordenadas, realizando a multiplicação desta matriz por cada ponto do quadrado temos:\n\n"
        
        newPosition = self.multiplyMatrix(schearMatrix, homogenCoords)
        
        return newPosition
    
    def getExplanationText(self):
        return self.explanationTest
    
    def resetExplanationText(self):
        self.explanationTest = ""