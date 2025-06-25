__package__

import math

class Circunferencia():
    def __init__(self):
        self.currentFunction = self.pontoMedio
        
    def setAlgoritmo(self,novoAlgoritmo):
        self.currentFunction = novoAlgoritmo

    def drawFunction(self, clicked_points, circle_center=False,circle_radius=False):
        if len(clicked_points) == 4:
            x1, y1 = clicked_points[0], clicked_points[1]
            x2, y2 = clicked_points[2], clicked_points[3]
        
        if not circle_center:
            circle_center = [x1, y1]
            
        if not circle_radius:
            circle_radius = math.sqrt(((x2 - x1)**2) + ((y2-y1)**2))
            circle_radius = round(circle_radius)
        
        return self.currentFunction(circle_center, circle_radius)
    
    def metodo_equacao_explicita(self, circle_center,circle_radius):
        print("USANDO EQUAÇÃO EXPLICITA")

        lighted_pixels = []

        xc, yc = circle_center[0], circle_center[1]
        R = circle_radius
        
        for x in range(-R, R + 1):  # Percorre os valores de x dentro do círculo
            y = math.sqrt(R**2 - x**2)  # Calcula y explicitamente a partir da equação do círculo
            
            lighted_pixels.append((xc + x, yc + round(y)))  # Parte superior
            lighted_pixels.append((xc + x, yc - round(y)))  # Parte inferior

        return lighted_pixels

    def pontoMedio(self, circle_center,circle_radius):
        print("USANDO PONTO MEDIO - CIRC")
        lighted_pixels = []
        
        xc, yc = circle_center[0], circle_center[1]

        R = circle_radius
        
        x = 0
        y = R
        d = 1 - R  # Variável de decisão inicial
        
        def plot_circle_points(x, y):                
            points = [
                (xc + x, yc + y), (xc + y, yc + x),
                (xc + y, yc - x), (xc + x, yc - y),
                (xc - x, yc - y), (xc - y, yc - x),
                (xc - y, yc + x), (xc - x, yc + y)
            ]
            for px, py in points:
                lighted_pixels.append((px, py))
        
        plot_circle_points(x, y)
        
        while x < y:
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
            plot_circle_points(x, y)
        
        return lighted_pixels
    
    def metodo_polinomial(self,circle_center, circle_radius):
        print("USANDO METODO POLINOMIALL")

        lighted_pixels = []

        xc, yc = circle_center[0], circle_center[1]
        R = circle_radius
        n = max(20, int(2 * math.pi * R))  # Aproximação da circunferência com um polígono de n lados
        step = 2 * math.pi / n  # Passo angular
        
        theta = 0
        while theta < 2 * math.pi:
            x = R * math.cos(theta)
            y = R * math.sin(theta)
            
            lighted_pixels.append((round(xc + x), round(yc + y)))
            theta += step
        
        return lighted_pixels
    
    def metodo_trigonometrico(self,circle_center, circle_radius):
        print("USANDO METODO TRIGONOMETRICO")

        lighted_pixels = []

        xc, yc = circle_center[0], circle_center[1]
        R = circle_radius
        
        theta = 0
        step = math.pi / (4 * R)  # Define o passo para varredura
        
        while theta <= math.pi / 4:  # Varre um octante e espelha os pontos
            x = R * math.cos(theta)
            y = R * math.sin(theta)
            
            # Função para converter os pontos em todos os 8 octantes
            def plot_circle_points(x, y):
                points = [
                    (xc + round(x), yc + round(y)), (xc + round(y), yc + round(x)),
                    (xc + round(y), yc - round(x)), (xc + round(x), yc - round(y)),
                    (xc - round(x), yc - round(y)), (xc - round(y), yc - round(x)),
                    (xc - round(y), yc + round(x)), (xc - round(x), yc + round(y))
                ]
                for px, py in points:
                    lighted_pixels.append((px, py))
            
            plot_circle_points(x, y)
            theta += step
        
        return lighted_pixels