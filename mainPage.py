from tkinter import *
from tkinter import ttk
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkScrollableFrame, CTkCheckBox, set_default_color_theme, set_appearance_mode
from Frames.Frame2D import GLUTFrame2D
from Frames.Frame3D import GLUTFrame3D
from Frames.ImageFrame import ImageFrame
from Frames.ecg import ECGFrame
from Forms.Reta import Reta
from Forms.Circunferencia import Circunferencia
from Forms.PoligonoRegular import Quadrado
from Transform.Transform2D import Transform2D
from Transform.Transform3D import Transform3D

quadradoBase = [(50,50),
                (150,50),
                (150,150),
                (50,150)]

cuboBase = [
            [0, 0, 0],
            [ 100, 0, 0],
            [ 100,  100, 0],
            [0,  100, 0],
            [0, 0,  100],
            [ 100, 0,  100],
            [ 100,  100,  100],
            [0,  100,  100],
        ]

def LIMPA_CT(array):
    for objeto in array:
        if isinstance(objeto,Text):
            objeto.delete("1.0","end")
        else:
            objeto.delete(0,END)
            
def insertText(widget=Text, text=str):
    widget.insert(END, text)

def limpa_frame(frame:Widget):
    for widget in frame.winfo_children():
        widget.pack_forget()
        widget.place_forget()

def insertDataTreeview(tree=ttk.Treeview, data=[]):
    tree.delete(*tree.get_children())
    
    for x, y in data:
        tree.insert(parent='', index='end', text='', values=(x,y))

def VALIDAR_FLOAT(text):
    if text == '': return True
    try:
        value = float(text)
    except ValueError:
        return False
    return 0<=value

class Main():
    def __init__(self):
        self.reta = Reta()
        self.circunferencia = Circunferencia()
        self.quadrado = Quadrado()
        self.transform2D = Transform2D()
        self.transform3D = Transform3D()

        # Tamanho inicial do GL
        self.window_width = 800
        self.window_height = 680

        self.root = CTk()
        
        # Tamanho da janela TK
        self.tkwindow_width = self.root.winfo_screenwidth()
        self.tkwindow_height = self.root.winfo_screenheight()
        
        self.root.geometry(f"{self.tkwindow_width}x{self.tkwindow_height}")
        self.root.title("Computação Gráfica")
        self.root.after(0, lambda: self.root.wm_state('zoomed'))
        
        set_default_color_theme("./Temas/theme.json")
        set_appearance_mode("dark")
        
        self.auxColor = "#FFFFFF"
        self.mainColor = "#000000"
        self.selectedColor = "#333333"
        
        self.VALIDAÇÃO_FLOAT()
        
        self.generateWidgets()
        
        self.startPage()
        
        self.root.mainloop()
        
    def generateWidgets(self):
        self.processoString = ""
        
        # Widgets Padrão
        self.mainFrame = CTkFrame(self.root,border_width=5)
        self.mainFrame.place(relx=0.330,rely=0.025,relheight=0.95,relwidth=0.65)
        
        self.auxFrame = CTkFrame(self.root,bg_color="gray", corner_radius=10)
        self.auxFrame.place(relx=0.015,rely=0.025,relheight=0.95,relwidth=0.3)
        
        self.labelForma = CTkLabel(self.auxFrame, text="MENU", bg_color=self.mainColor, font=("Segoe UI Black", 40))
        
        self.glFrame = GLUTFrame2D(self.mainFrame,width=(self.mainFrame.winfo_width()*0.98),height=(self.mainFrame.winfo_height()*0.98),forma=self.reta)

        self.backButton = CTkButton(self.auxFrame,text="<",font=("Segoe UI Black", 30),border_width=0,corner_radius=0)

        self.placeHolderlabel = CTkLabel(self.mainFrame,text="COMPUTAÇÃO GRÁFICA 2025.1", bg_color=self.mainColor, font=("Segoe UI Black", 40))
        self.placeHolderlabel.place(relx=0.5,rely=0.5,anchor="c")

        self.imageFrame = ImageFrame(self.mainFrame)

        #Menu Principal
        self.drawButton = CTkButton(self.auxFrame,text="DESENHAR",font=("Segoe UI Black", 35),
                                    command=self.drawPage)
        
        self.ECGButton = CTkButton(self.auxFrame,text="ECG",font=("Segoe UI Black", 35),
                                    command=self.ECGPage)
        
        self.transformButton = CTkButton(self.auxFrame,text="TRANSFORMAR",font=("Segoe UI Black", 35),
                                    command=self.TransformPage)
        
        #Menu Desenho
        self.drawLine = CTkButton(self.auxFrame,text="RETA",font=("Segoe UI Black", 35),
                                  command=self.frameReta)
        
        self.drawCircle = CTkButton(self.auxFrame,text="CIRCUNFERÊNCIA",font=("Segoe UI Black", 35),
                                    command=self.frameCircunferencia)
        
        #Menu Transformações
        self.dimension2 = CTkButton(self.auxFrame,text="2D",font=("Segoe UI Black", 35),
                                    command=self.Transformation2DFrame)
        
        self.dimension3 = CTkButton(self.auxFrame,text="3D",font=("Segoe UI Black", 35),
                                    command=self.Transformation3DFrame)
        
        self.imageButton = CTkButton(self.auxFrame,text="IMAGEM",font=("Segoe UI Black", 35),
                                    command=self.ImageTransfromPage)
        
        #Menu Imagem --TODO
        
        #Criando Menus
        self.menu = Menu(self.root)
        self.root.configure(menu=self.menu)
        
        filemenu = Menu(self.menu)
        self.menu.add_cascade(label='Menu', menu=filemenu)
        filemenu.add_command(label='Guia', command= lambda: [self.changeFrameType(0)])
        filemenu.add_separator()
        filemenu.add_command(label='Sair', command=self.root.quit)
        
        transformacoes2D = Menu(self.menu)
        self.menu.add_cascade(label='OpenGL', menu=transformacoes2D)
        transformacoes2D.add_command(label='Inverter Cores', command=lambda:[self.glFrame.invertColors()])
        transformacoes2D.add_command(label='Eixos ON/OFF', command=lambda:[self.glFrame.turnShowAxis()])
        transformacoes2D.add_command(label='Recorte', command=lambda:[self.glFrame.turnRecorte()])
        transformacoes2D.add_command(label='Cohen-Suterland', command=lambda:[self.glFrame.turnCohensuterland()])
        transformacoes2D.add_command(label='Resetar', command=lambda:[self.glFrame.clearScreen()])
        
        Graphic2D = Menu(self.menu)
        self.menu.add_cascade(label='Temas', menu=Graphic2D)
        Graphic2D.add_command(label="Dark", command=lambda:[set_appearance_mode("dark")])
        Graphic2D.add_command(label='light', command=lambda:[set_appearance_mode("light")])
        
        #Widgets da Reta
        valorX1Reta = IntVar()
        valorY1Reta = IntVar()
        valorX2Reta = IntVar()
        valorY2Reta = IntVar()
        
        self.labelX1Reta = CTkLabel(self.auxFrame,text="X1",  font=("Segoe UI Black", 17))
        self.entryX1Reta = CTkEntry(self.auxFrame,textvariable=valorX1Reta,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelY1Reta = CTkLabel(self.auxFrame,text="Y1",  font=("Segoe UI Black", 17))
        self.entryY1Reta = CTkEntry(self.auxFrame,textvariable=valorY1Reta,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelX2Reta = CTkLabel(self.auxFrame,text="X2",  font=("Segoe UI Black", 17))
        self.entryX2Reta = CTkEntry(self.auxFrame,textvariable=valorX2Reta,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelY2Reta = CTkLabel(self.auxFrame,text="Y2",  font=("Segoe UI Black", 17))
        self.entryY2Reta = CTkEntry(self.auxFrame,textvariable=valorY2Reta,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.setDDAButton = CTkButton(self.auxFrame, text="DDA", font=("Segoe UI Black", 17),border_width=2,
                                      command=lambda: [self.reta.setAlgoritmo(self.reta.DDA), self.focusTable(self.setDDAButton,[self.setPMedioButton])])
        
        self.setPMedioButton = CTkButton(self.auxFrame, text="PONTO\nMEDIO", font=("Segoe UI Black", 17),border_width=2,
                                         command=lambda: [self.reta.setAlgoritmo(self.reta.pontoMedio), self.focusTable(self.setPMedioButton,[self.setDDAButton])])
        
        self.buttonDesenharReta = CTkButton(self.auxFrame, text="Desenhar", font=("Segoe UI Black", 17),
                                         border_width=2, command=lambda:[
            self.glFrame.dadosFornecidos(x1=int(self.entryX1Reta.get()),
                                         y1=int(self.entryY1Reta.get()),
                                         x2=int(self.entryX2Reta.get()),
                                         y2=int(self.entryY2Reta.get())),
            LIMPA_CT([self.entryX1Reta,self.entryY1Reta,self.entryX2Reta,self.entryY2Reta])
        ])
        
        #Widgets da Circunferencia       
        valorX1Circ = IntVar()
        valorY1Circ = IntVar()
        
        valorRaio = IntVar()
        
        self.labelX1Circ = CTkLabel(self.auxFrame,text="X1",  font=("Segoe UI Black", 17))
        self.entryX1Circ = CTkEntry(self.auxFrame,textvariable=valorX1Circ,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelY1Circ = CTkLabel(self.auxFrame,text="Y1",  font=("Segoe UI Black", 17))
        self.entryY1Circ = CTkEntry(self.auxFrame,textvariable=valorY1Circ,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelRaioCirc = CTkLabel(self.auxFrame,text="Raio",  font=("Segoe UI Black", 17))
        self.entryRaioCirc = CTkEntry(self.auxFrame,textvariable=valorRaio,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.seteqExplicita = CTkButton(self.auxFrame, text="EQ.\nEXPLICITA", font=("Segoe UI Black", 17),border_width=2,
                                      command=lambda: [self.reta.setAlgoritmo(self.circunferencia.metodo_equacao_explicita), self.focusTable(self.seteqExplicita,[self.setPMCircle,self.setMetPol,self.setMetTrig])])
        
        self.setPMCircle = CTkButton(self.auxFrame, text="PONTO\nMEDIO", font=("Segoe UI Black", 17),border_width=2,
                                      command=lambda: [self.reta.setAlgoritmo(self.circunferencia.pontoMedio), self.focusTable(self.setPMCircle,[self.seteqExplicita,self.setMetPol,self.setMetTrig])])
        
        self.setMetPol = CTkButton(self.auxFrame, text="MET.\nPOL.", font=("Segoe UI Black", 17),border_width=2,
                                      command=lambda: [self.reta.setAlgoritmo(self.circunferencia.metodo_polinomial), self.focusTable(self.setMetPol,[self.seteqExplicita,self.setPMCircle,self.setMetTrig])])
        
        self.setMetTrig = CTkButton(self.auxFrame, text="MET.\nTRIG.", font=("Segoe UI Black", 17),border_width=2,
                                      command=lambda: [self.reta.setAlgoritmo(self.circunferencia.metodo_trigonometrico), self.focusTable(self.setMetTrig,[self.seteqExplicita,self.setPMCircle,self.setMetPol])])
        
        
        self.buttonDesenharCirc = CTkButton(self.auxFrame, text="Desenhar", font=("Segoe UI Black", 17),
                                         border_width=2, command=lambda:[
            self.glFrame.dadosFornecidos(x1=int(self.entryX1Circ.get()),
                                         y1=int(self.entryY1Circ.get()),
                                         raio=int(self.entryRaioCirc.get())),
            LIMPA_CT([self.entryX1Circ,self.entryY1Circ,self.entryRaioCirc])
        ])
        
        #Página das Transformações 2D
        valorXTrans = IntVar()
        valorYTrans = IntVar()
        valorRotacao = IntVar()
        
        self.labelX1Trans = CTkLabel(self.auxFrame,text="X",  font=("Segoe UI Black", 17))
        self.entryX1Trans = CTkEntry(self.auxFrame,textvariable=valorXTrans,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelY1Trans = CTkLabel(self.auxFrame,text="Y",  font=("Segoe UI Black", 17))
        self.entryY1Trans = CTkEntry(self.auxFrame,textvariable=valorYTrans,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelRotacao = CTkLabel(self.auxFrame,text="Angulo",  font=("Segoe UI Black", 17))
        self.entryRotacao = CTkEntry(self.auxFrame,textvariable=valorRotacao,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        #Página das Transformações 3D
        valorXTrans3D = IntVar()
        valorYTrans3D = IntVar()
        valorZTrans3D = IntVar()
        
        self.labelX1Trans3D = CTkLabel(self.auxFrame,text="X",  font=("Segoe UI Black", 17))
        self.entryX1Trans3D = CTkEntry(self.auxFrame,textvariable=valorXTrans3D,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelY1Trans3D = CTkLabel(self.auxFrame,text="Y",  font=("Segoe UI Black", 17))
        self.entryY1Trans3D = CTkEntry(self.auxFrame,textvariable=valorYTrans3D,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        self.labelZ1Trans3D = CTkLabel(self.auxFrame,text="Z",  font=("Segoe UI Black", 17))
        self.entryZ1Trans3D = CTkEntry(self.auxFrame,textvariable=valorZTrans3D,validate='key', validatecommand=self.vald2, font=("Segoe UI Black", 17))
        
        #Frame Scrollavel
        self.transformSequency = CTkScrollableFrame(self.auxFrame, orientation=HORIZONTAL, border_width=0, label_text="SEQUENCIA")
        
        #Botão de Desenhar o quadrado
        self.buttonDesenharQuadrado = CTkButton(self.auxFrame, text="Desenhar", font=("Segoe UI Black", 17),
                                          command=lambda:[
            self.glFrame.dadosFornecidos(figura=self.quadrado)
        ])
        
        #Botões das transformações 2D
        self.buttonTranslation = CTkButton(self.auxFrame, text="Transladar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(0)])
        
        self.buttonScale = CTkButton(self.auxFrame, text="Escalar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(1)])
        
        self.buttonRotation = CTkButton(self.auxFrame, text="Rotacionar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(2)])
        
        self.buttonReflexX = CTkCheckBox(self.auxFrame, text="em X", font=("Segoe UI Black", 17),
                                        hover_color=self.selectedColor)
                
        self.buttonReflexY = CTkCheckBox(self.auxFrame, text="em Y", font=("Segoe UI Black", 17),
                                         hover_color=self.selectedColor)
        
        self.buttonReflex = CTkButton(self.auxFrame, text="Refletir", font=("Segoe UI Black", 17),
                                         command=self.reflexCheckbox2D)
        
        self.buttonSchear = CTkButton(self.auxFrame, text="Cisalhamento", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(4)])
        
        #Botões das transformações 3d
        self.buttonTranslation3D = CTkButton(self.auxFrame, text="Transladar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector3D(0)])
        
        self.buttonScale3D = CTkButton(self.auxFrame, text="Escalar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector3D(1)])
                
        self.buttonRotation3D = CTkButton(self.auxFrame, text="Rotacionar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector3D(2)])
        
        self.buttonReflexXY = CTkCheckBox(self.auxFrame, text="XY", font=("Segoe UI Black", 17),
                                        hover_color=self.selectedColor)
        
        self.buttonReflexXZ = CTkCheckBox(self.auxFrame, text="XZ", font=("Segoe UI Black", 17),
                                        hover_color=self.selectedColor)
        
        self.buttonReflexYZ = CTkCheckBox(self.auxFrame, text="YZ", font=("Segoe UI Black", 17),
                                        hover_color=self.selectedColor)
        
        self.buttonReflex3D = CTkButton(self.auxFrame, text="Refletir", font=("Segoe UI Black", 17),
                                         command=self.reflexCheckbox3D)
        
        self.buttonSchear3D = CTkButton(self.auxFrame, text="Cisalhar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector3D(4)])
        
        #Botões das transformações 2D
        self.buttonTranslationImage = CTkButton(self.auxFrame, text="Transladar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(0)])
        
        self.buttonScaleImage = CTkButton(self.auxFrame, text="Escalar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(1)])
        
        self.buttonRotationImage = CTkButton(self.auxFrame, text="Rotacionar", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(2)])
        
        self.buttonReflexXImage = CTkCheckBox(self.auxFrame, text="em X", font=("Segoe UI Black", 17),
                                        hover_color=self.selectedColor)
                
        self.buttonReflexYImage = CTkCheckBox(self.auxFrame, text="em Y", font=("Segoe UI Black", 17),
                                         hover_color=self.selectedColor)
        
        self.buttonReflexImage = CTkButton(self.auxFrame, text="Refletir", font=("Segoe UI Black", 17),
                                         command=self.reflexCheckbox2D)
        
        self.buttonSchearImage = CTkButton(self.auxFrame, text="Cisalhamento", font=("Segoe UI Black", 17),
                                         command=lambda:[self.TransformSelector(4)])
        
        #Treeview das coordenadas (Utilizado por todos os widgets acima)
        self.coordinateFrame = Frame(self.auxFrame, bg="red")
        
        self.treeCoordinates = ttk.Treeview(self.coordinateFrame)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", highlightthickness=0, bd=0, font=('Helvetica-Bold', 17), rowheight=25, )
        style.configure("Treeview.Heading", font=('Helvetica-Bold', 17,'bold'))
        
        self.treeCoordinates['columns'] = ("X","Y")
        self.treeCoordinates.column("#0",width=0, stretch = "no")
        self.treeCoordinates.column("X",width=130, minwidth=25, anchor=CENTER)
        self.treeCoordinates.column("Y",width=130, minwidth=25, anchor=CENTER)
        
        self.treeCoordinates.heading("#0",text="")
        self.treeCoordinates.heading("X",text="X")
        self.treeCoordinates.heading("Y",text="Y")
        
        self.treeScroll = Scrollbar(self.treeCoordinates)
        self.treeScroll.pack(side=RIGHT,fill=Y)
        
        self.treeScroll.config(command=self.treeCoordinates.yview)
        
        self.coordMundo = CTkButton(self.auxFrame, text="Mundo", font=("Segoe UI Black", 17),corner_radius=0,border_width=2,
                                 command=lambda: [insertDataTreeview(self.treeCoordinates,self.glFrame.coordenadas_Mundo),
                                                  self.focusTable(self.coordMundo, [self.coordTela, self.coordOpenGL])])
        
        self.coordOpenGL = CTkButton(self.auxFrame, text="OpenGL", font=("Segoe UI Black", 17),corner_radius=0,border_width=2,
                                  command=lambda: [insertDataTreeview(self.treeCoordinates,self.glFrame.coordenadas_OpenGL),
                                                   self.focusTable(self.coordOpenGL, [self.coordMundo, self.coordTela])])
        
        self.coordTela = CTkButton(self.auxFrame, text="Tela", font=("Segoe UI Black", 17),corner_radius=0,border_width=2,
                                command=lambda: [insertDataTreeview(self.treeCoordinates,self.glFrame.coordenadas_Tela), 
                                                 self.focusTable(self.coordTela, [self.coordMundo, self.coordOpenGL])])
        
        #Bidings Adicionais
        self.root.bind("c", lambda _: self.glFrame.clearScreen(), self.shortcut())
        self.root.bind("r", lambda _: self.glFrame.clearScreen())
        self.root.bind("b", lambda _: self.glFrame.resetCamera())
        
    def startPage(self):
        limpa_frame(self.auxFrame)
        self.labelForma.configure(text="MENU")
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(3)
        
        self.drawButton.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        self.ECGButton.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        self.transformButton.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        
    def drawPage(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.startPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        self.labelForma.pack(anchor=CENTER,pady=20)
        self.labelForma.configure(text="DESENHO")
        
        self.changeFrameType(3)
        
        self.drawLine.pack(anchor=CENTER,pady=90,ipady=10,ipadx=10)
        self.drawCircle.pack(anchor=CENTER,pady=90,ipady=10,ipadx=10)
    
    def ECGPage(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.startPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        self.labelForma.pack(anchor=CENTER,pady=20)
        self.labelForma.configure(text="ECG")
        
        self.changeFrameType(2)
    
    def TransformPage(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.startPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        self.labelForma.pack(anchor=CENTER,pady=20)
        self.labelForma.configure(text="TRANSFORMAÇÃO")
        
        self.changeFrameType(3)
        
        self.dimension2.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        self.dimension3.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        self.imageButton.pack(anchor=CENTER,pady=50,ipady=10,ipadx=10)
        
    def ImageTransfromPage(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.TransformPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        
        self.labelForma.configure(text="IMAGEM")
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(4)
        
        self.labelX1Trans.place(relx=0.1,rely=0.15,relheight=0.05,relwidth=0.1)
        self.entryX1Trans.place(relx=0.25,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelY1Trans.place(relx=0.5,rely=0.15,relheight=0.05,relwidth=0.1)
        self.entryY1Trans.place(relx=0.65,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelRotacao.place(relx=0.1,rely=0.4425,relheight=0.05,relwidth=0.3)
        self.entryRotacao.place(relx=0.325,rely=0.4425,relheight=0.05,relwidth=0.2)
        
        self.buttonTranslation.place(relx=0.260,rely=0.225,relheight=0.08,relwidth=0.5)
        self.buttonScale.place(relx=0.260,rely=0.325,relheight=0.08,relwidth=0.5)
        self.buttonRotation.place(relx=0.6,rely=0.425,relheight=0.08,relwidth=0.3)
        self.buttonReflexX.place(relx=0.1,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonReflexY.place(relx=0.35,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonReflex.place(relx=0.6,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonSchear.place(relx=0.260,rely=0.625,relheight=0.08,relwidth=0.5)
        
        self.transformSequency.place(relx=0.05,rely=0.75, relwidth=0.9, relheight=0.125)
        
        self.buttonTranslation.configure(command=lambda:[self.TransformSelectorImage(0)])
        self.buttonScale.configure(command=lambda:[self.TransformSelectorImage(1)])
        self.buttonRotation.configure(command=lambda:[self.TransformSelectorImage(2)])
        self.buttonReflex.configure(command=self.reflexCheckboxImage)
        self.buttonSchear.configure(command=lambda:[self.TransformSelectorImage(4)])
        
    def frameReta(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.drawPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        
        self.labelForma.configure(text="RETA")
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(0)
        self.glFrame.setForma(self.reta)

        self.labelX1Reta.place(relx=0.05,rely=0.1,relheight=0.1,relwidth=0.1)
        self.entryX1Reta.place(relx=0.15,rely=0.125,relheight=0.05,relwidth=0.2)
        
        self.labelY1Reta.place(relx=0.35,rely=0.1,relheight=0.1,relwidth=0.1)
        self.entryY1Reta.place(relx=0.45,rely=0.125,relheight=0.05,relwidth=0.2)
        
        self.labelX2Reta.place(relx=0.05,rely=0.2,relheight=0.1,relwidth=0.1)
        self.entryX2Reta.place(relx=0.15,rely=0.225,relheight=0.05,relwidth=0.2)
        
        self.labelY2Reta.place(relx=0.35,rely=0.2,relheight=0.1,relwidth=0.1)
        self.entryY2Reta.place(relx=0.45,rely=0.225,relheight=0.05,relwidth=0.2)
        
        self.setDDAButton.place(relx=0.70,rely=0.1,relheight=0.07,relwidth=0.25)
        
        self.setPMedioButton.place(relx=0.70,rely=0.2,relheight=0.07,relwidth=0.25)
        
        self.buttonDesenharReta.place(relx=0.260,rely=0.325,relheight=0.08,relwidth=0.5)
        
        self.setTreeViewLoc()
        
    def frameCircunferencia(self):
        limpa_frame(self.auxFrame)
        self.backButton.configure(command=self.drawPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)

        self.labelForma.configure(text="CIRCUNFERENCIA")
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(0)
        self.glFrame.setForma(self.circunferencia)
        
        self.labelX1Circ.place(relx=0.05,rely=0.1,relheight=0.1,relwidth=0.1)
        self.entryX1Circ.place(relx=0.15,rely=0.125,relheight=0.05,relwidth=0.2)
        
        self.labelY1Circ.place(relx=0.35,rely=0.1,relheight=0.1,relwidth=0.1)
        self.entryY1Circ.place(relx=0.45,rely=0.125,relheight=0.05,relwidth=0.2)
        
        self.labelRaioCirc.place(relx=0.15,rely=0.2,relheight=0.1,relwidth=0.2)
        self.entryRaioCirc.place(relx=0.35,rely=0.225,relheight=0.05,relwidth=0.2)
        
        self.seteqExplicita.place(relx=0.70,rely=0.1,relheight=0.07,relwidth=0.25)
        self.setPMCircle.place(relx=0.70,rely=0.18,relheight=0.07,relwidth=0.25)
        self.setMetPol.place(relx=0.70,rely=0.26,relheight=0.07,relwidth=0.25)
        self.setMetTrig.place(relx=0.70,rely=0.34,relheight=0.07,relwidth=0.25)
        
        self.buttonDesenharCirc.place(relx=0.15,rely=0.325,relheight=0.08,relwidth=0.5)
        
        self.setTreeViewLoc()
        
    def Transformation2DFrame(self, typeT=0, txt="TRANSFORMAÇÃO"):
        limpa_frame(self.auxFrame)
        limpa_frame(self.transformSequency)
        self.backButton.configure(command=self.TransformPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        
        self.labelForma.configure(text=txt)
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(0)
        
        self.labelX1Trans.place(relx=0.1,rely=0.15,relheight=0.05,relwidth=0.1)
        self.entryX1Trans.place(relx=0.25,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelY1Trans.place(relx=0.5,rely=0.15,relheight=0.05,relwidth=0.1)
        self.entryY1Trans.place(relx=0.65,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelRotacao.place(relx=0.1,rely=0.4425,relheight=0.05,relwidth=0.3)
        self.entryRotacao.place(relx=0.325,rely=0.4425,relheight=0.05,relwidth=0.2)
        
        self.buttonTranslation.place(relx=0.260,rely=0.225,relheight=0.08,relwidth=0.5)
        self.buttonScale.place(relx=0.260,rely=0.325,relheight=0.08,relwidth=0.5)
        self.buttonRotation.place(relx=0.6,rely=0.425,relheight=0.08,relwidth=0.3)
        self.buttonReflexX.place(relx=0.1,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonReflexY.place(relx=0.35,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonReflex.place(relx=0.6,rely=0.525,relheight=0.08,relwidth=0.3)
        self.buttonSchear.place(relx=0.260,rely=0.625,relheight=0.08,relwidth=0.5)
        
        self.transformSequency.place(relx=0.05,rely=0.75, relwidth=0.9, relheight=0.125)
        
        self.buttonTranslation.configure(command=lambda:[self.TransformSelector(0)])
        self.buttonScale.configure(command=lambda:[self.TransformSelector(1)])
        self.buttonRotation.configure(command=lambda:[self.TransformSelector(2)])
        self.buttonReflex.configure(command=self.reflexCheckbox2D)
        self.buttonSchear.configure(command=lambda:[self.TransformSelector(4)])
        
    def Transformation3DFrame(self, typeT=0, txt="TRANSFORMAÇÃO"):
        limpa_frame(self.auxFrame)
        limpa_frame(self.transformSequency)
        self.backButton.configure(command=self.TransformPage)
        self.backButton.place(relx=0.05,rely=0.03,relwidth=0.05,relheight=0.05)
        
        self.labelForma.configure(text=txt)
        self.labelForma.pack(anchor=CENTER,pady=20)
        
        self.changeFrameType(1)
        
        self.labelX1Trans3D.place(relx=0.05,rely=0.125,relheight=0.1,relwidth=0.1)
        self.entryX1Trans3D.place(relx=0.15,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelY1Trans3D.place(relx=0.35,rely=0.125,relheight=0.1,relwidth=0.1)
        self.entryY1Trans3D.place(relx=0.45,rely=0.15,relheight=0.05,relwidth=0.2)
        
        self.labelZ1Trans3D.place(relx=0.65,rely=0.125,relheight=0.1,relwidth=0.1)
        self.entryZ1Trans3D.place(relx=0.75,rely=0.15,relheight=0.05,relwidth=0.2)

        self.buttonTranslation3D.place(relx=0.260,rely=0.25,relheight=0.08,relwidth=0.5)
        self.buttonScale3D.place(relx=0.260,rely=0.35,relheight=0.08,relwidth=0.5)
        self.buttonRotation3D.place(relx=0.260,rely=0.45,relheight=0.08,relwidth=0.5)
        self.buttonReflexXY.place(relx=0.05,rely=0.55,relheight=0.08,relwidth=0.15)
        self.buttonReflexXZ.place(relx=0.25,rely=0.55,relheight=0.08,relwidth=0.15)
        self.buttonReflexYZ.place(relx=0.45,rely=0.55,relheight=0.08,relwidth=0.15)
        self.buttonReflex3D.place(relx=0.65,rely=0.55,relheight=0.08,relwidth=0.3)
        self.buttonSchear3D.place(relx=0.260,rely=0.65,relheight=0.08,relwidth=0.5)
        
        self.transformSequency.place(relx=0.05,rely=0.75, relwidth=0.9, relheight=0.125)
    
    def TransformSelector(self,type):
        x = float(self.entryX1Trans.get())
        y = float(self.entryY1Trans.get())
        angulo = float(self.entryRotacao.get())
        
        transformation = 0
        
        if(type == 0):
            transformation = self.transform2D.transposition(self.quadrado.getPoints(), [x,y])
            self.addTransform(0,data=(x,y))
        elif(type == 1):
            transformation = self.transform2D.scale(self.quadrado.getPoints(), [x,y])
            self.addTransform(1,data=(x,y))
        elif(type == 2):
            transformation = self.transform2D.rotation(self.quadrado.getPoints(), angulo,x,y)
            self.addTransform(2,data=(angulo,x,y))
        elif(type == 4):
            transformation = self.transform2D.schear(self.quadrado.getPoints(), x,y)
            self.addTransform(4,data=(x,y))
            
        self.quadrado.setPoints(transformation)
        self.glFrame.clearScreen()
        self.glFrame.dadosFornecidos(figura=self.quadrado)
    
    def TransformSelector3D(self,type):
        x = float(self.entryX1Trans3D.get())
        y = float(self.entryY1Trans3D.get())
        z = float(self.entryZ1Trans3D.get())
        
        transformation = 0
        
        if(type == 0):
            transformation = self.transform3D.transposition(self.glFrame.vertices, [x,y,z])
            self.addTransform(0,data=(x,y,z))
        elif(type == 1):
            transformation = self.transform3D.scale(self.glFrame.vertices, [x,y,z])
            self.addTransform(1,data=(x,y,z))
        elif(type == 2):
            transformation = self.transform3D.rotation(self.glFrame.vertices, x,y,z)
            self.addTransform(2,data=(x,y,z))
        elif(type == 4):
            transformation = self.transform3D.schear(self.glFrame.vertices, x,y,z)
            self.addTransform(4,data=(x,y,z))
        
        self.glFrame.setVertices(transformation)
        
        self.glFrame.redraw()
        
    def TransformSelectorImage(self,type):
        x = float(self.entryX1Trans.get())
        y = float(self.entryY1Trans.get())
        angulo = float(self.entryRotacao.get())
        
        if(type == 0):
            self.imageFrame.apply_translation(x,y)
            self.addTransform(0,data=(x,y))
        elif(type == 1):
            self.imageFrame.apply_scale(x,y)
            self.addTransform(1,data=(x,y))
        elif(type == 2):
            self.imageFrame.apply_rotation(angulo)
            self.addTransform(2,data=(angulo,x,y))
        elif(type == 4):
            self.imageFrame.apply_shear(x,y)
            self.addTransform(4,data=(x,y))
    
    def reflexCheckbox2D(self):
        if(self.buttonReflexX.get() == 1):
            self.quadrado.setPoints(self.transform2D.reflectionX(self.quadrado.getPoints()))
            self.addTransform(3,data=("(X)"))
    
        if(self.buttonReflexY.get() == 1):
            self.quadrado.setPoints(self.transform2D.reflectionY(self.quadrado.getPoints()))
            self.addTransform(3,data=("(Y)"))
            
        self.glFrame.clearScreen()
        self.glFrame.dadosFornecidos(figura=self.quadrado)
        
    def reflexCheckbox3D(self):
        if(self.buttonReflexXY.get() == 1):
            self.glFrame.setVertices(self.transform3D.reflectionXY(self.glFrame.vertices))
            self.addTransform(3,data=("(XY)"))
    
        if(self.buttonReflexYZ.get() == 1):
            self.glFrame.setVertices(self.transform3D.reflectionYZ(self.glFrame.vertices))
            self.addTransform(3,data=("(YZ)"))
            
        if(self.buttonReflexXZ.get() == 1):
            self.glFrame.setVertices(self.transform3D.reflectionXZ(self.glFrame.vertices))
            self.addTransform(3,data=("(XZ)"))
            
        self.glFrame.redraw()
        
    def reflexCheckboxImage(self):
        if(self.buttonReflexX.get() == 1):
            self.imageFrame.apply_reflectionX()
            self.addTransform(3,data=("(X)"))
    
        if(self.buttonReflexY.get() == 1):
            self.imageFrame.apply_reflectionY()
            self.addTransform(3,data=("(Y)"))
    
    def setTreeViewLoc(self):
        self.coordinateFrame.place(relx=0.0,rely=0.5,relheight=0.5,relwidth=1)
        
        self.treeCoordinates.place(relx=0.0,rely=0.0,relheight=1,relwidth=1)
        
        self.coordMundo.place(relx=0.0,rely=0.425,relheight=0.08,relwidth=0.34)
        
        self.coordOpenGL.place(relx=0.34,rely=0.425,relheight=0.08,relwidth=0.33)
        
        self.coordTela.place(relx=0.67,rely=0.425,relheight=0.08,relwidth=0.33)
        
    def unbindEvents(self,widget):
        for event in widget.bind():
            widget.unbind(event)

    def focusTable(self, focused=CTkButton, unfocus=CTkButton):
        focused.configure(fg_color="#999999", text_color="black")
        
        for button in unfocus:
            button.configure(fg_color="#000000", text_color="white")

    def VALIDAÇÃO_FLOAT(self):
        self.vald2 = (self.root.register(VALIDAR_FLOAT), '%P')

    def treatReturnTransform(self, points, text):
        if len(points) == 4:
            self.quadrado.setPoints(points)
        else:
            self.glFrame.setVertices(points)
        self.processoString = text

    def changeFrameType(self, opt):
        limpa_frame(self.mainFrame)
        
        if(opt == 0):
            self.glFrame = GLUTFrame2D(self.mainFrame,width=(self.mainFrame.winfo_width()*0.98),height=(self.mainFrame.winfo_height()*0.98),forma=self.circunferencia)
        elif(opt == 1):
            self.glFrame = GLUTFrame3D(self.mainFrame,width=(self.mainFrame.winfo_width()*0.98),height=(self.mainFrame.winfo_height()*0.98),forma=self.reta)
        elif(opt == 2):
            self.glFrame = ECGFrame(self.mainFrame, width=800, height=680)
        elif(opt == 3):
            self.placeHolderlabel.place(relx=0.5,rely=0.5,anchor="c")
            return
        elif(opt == 4):
            self.imageFrame.place(relx=0,rely=0,relwidth=1,relheight=1)
            return
            
        self.glFrame.place(relx=0.01,rely=0.01,relheight=0.98,relwidth=0.98)
        
    def addTransform(self,type,data):
        font = ("Times New Roman", 17)
        fg = "#333333"
        
        if len(self.transformSequency.winfo_children()) != 0:
            CTkLabel(self.transformSequency,text=f" → ",fg_color=fg, font=font).pack(side=LEFT)
        
        if(type == 0):
            CTkLabel(self.transformSequency,text=f"T{data}",fg_color=fg, font=font).pack(side=LEFT)
        elif(type == 1):
            CTkLabel(self.transformSequency,text=f"S{data}",fg_color=fg,font=font).pack(side=LEFT)
        elif(type == 2):
            CTkLabel(self.transformSequency,text=f"R{data[0]}",fg_color=fg,font=font).pack(side=LEFT)
        elif(type == 3):
            CTkLabel(self.transformSequency,text=f"Re{data}",fg_color=fg,font=font).pack(side=LEFT)
        elif(type == 4):
            CTkLabel(self.transformSequency,text=f"Sr{data}",fg_color=fg,font=font).pack(side=LEFT)
        
    def shortcut(self):
        self.quadrado.setPoints(quadradoBase)
        if(isinstance(self.glFrame,GLUTFrame3D)):
            self.glFrame.setVertices(cuboBase)
        self.transform2D.resetExplanationText()
        self.transform3D.resetExplanationText()
        
Main()