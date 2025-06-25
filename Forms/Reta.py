__package__

class Reta():    
    def __init__(self):
        self.currentFunction = self.DDA
        
    def setAlgoritmo(self,novoAlgoritmo):
        self.currentFunction = novoAlgoritmo
    
    def drawFunction(self,clicked_points):
        return self.currentFunction(clicked_points)
    
    def DDA(self,clicked_points_line):
        print("USANDO DDA")
        lighted_pixels = []
        
        x1,x2 = clicked_points_line[0], clicked_points_line[2]
        y1,y2 = clicked_points_line[1], clicked_points_line[3]
        
        lenghtInc = max(abs(x2 - x1),abs(y2 - y1))
        
        xinc = (x2 - x1)/lenghtInc
        yinc = (y2 - y1)/lenghtInc
        
        lighted_pixels.append((x1,y1))
        
        if(x1 < x2):
            while(x1 < x2):
                x1 += xinc
                y1 += yinc
                
                lighted_pixels.append((x1,y1))
        elif(x1 > x2):
            while(x1 > x2):
                x1 += xinc
                y1 += yinc
                
                lighted_pixels.append((x1,y1))
        
        return lighted_pixels
    
    def pontoMedio(self, clicked_points_line):
        print("USANDO PONTO MÉDIO")
        lighted_pixels = []
        
        x1,x2 = clicked_points_line[0], clicked_points_line[2]
        y1,y2 = clicked_points_line[1], clicked_points_line[3]
        
        print(f"{x1} {y1}")
        print(f"{x2} {y2}")
        
        dx = abs(abs(x2) - abs(x1))
        dy = abs(abs(y2) - abs(y1))
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        a = dy
        b = -dx
        
        if dx > dy:
            d = 2*a + b
            while x1 != x2:
                lighted_pixels.append((x1, y1))
                if d >= 0:
                    y1 += sy
                    d -= 2 * dx
                x1 += sx
                d += 2 * dy
        else:
            d = a + 2*b
            while y1 != y2:
                lighted_pixels.append((x1, y1))
                if d >= 0:
                    x1 += sx
                    d -= 2 * dy
                y1 += sy
                d += 2 * dx
        
        lighted_pixels.append((x2, y2))

        return lighted_pixels
    
    def pontoMedioStatic(clicked_points_line):
        lighted_pixels = []
        
        x1,x2 = clicked_points_line[0], clicked_points_line[2]
        y1,y2 = clicked_points_line[1], clicked_points_line[3]
        
        print(f"{x1} {y1}")
        print(f"{x2} {y2}")
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        a = dy
        b = -dx
        
        if dx > dy:
            d = 2*a + b
            
            while x1 != x2:
                # print(d)
                lighted_pixels.append((x1, y1))
                if d >= 0:
                    y1 += sy
                    d -= 2 * dx
                x1 += sx
                d += 2 * dy
        else:
            d = a + 2*b
            
            while y1 != y2:
                # print(d)
                lighted_pixels.append((x1, y1))
                if d >= 0:
                    x1 += sx
                    d -= 2 * dy
                y1 += sy
                d += 2 * dx
        
        lighted_pixels.append((x2, y2))

        return lighted_pixels