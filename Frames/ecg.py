from pyopengltk import OpenGLFrame
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class ECGFrame(OpenGLFrame):
    def __init__(self,master, *args, **kw):
        super().__init__(master,*args, **kw)
        master.after(100, lambda: ECGFrame.loop(self))  # aguarda o contexto OpenGL ficar pronto
    
    def initgl(self):
        glClearColor(0, 0, 0, 1)
        glColor3f(1, 1, 1)
        glLineWidth(1)
        self.ecg_buffer = []
        self.t = 0

    def update(self):
        self.t += 0.02
        y = ECGFrame.heartbeat_wave(self.t % 5)
        self.ecg_buffer.append(y)
        if len(self.ecg_buffer) > 500:
            self.ecg_buffer.pop(0)

    def redraw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_LINE_STRIP)
        for i, y in enumerate(self.ecg_buffer):
            x = i / 500 * 2 - 1
            glVertex2f(x, y)
        glEnd()

        self.tkSwapBuffers()
        
    # Função da curva de batimento cardíaco
    def heartbeat_wave(x):
        return (
            math.exp(-((x - 2)**2) * 10) * 0.8
            - math.exp(-((x - 1.5)**2) * 30) * 0.2
            - math.exp(-((x - 2.5)**2) * 30) * 0.3
            + math.exp(-((x - 3.5)**2) * 10) * 0.15
        )
    
    def loop(frame):
        frame.update()
        frame.redraw()
        frame.after(16, lambda: ECGFrame.loop(frame))  # 60 FPS