from tkinter import *
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkScrollableFrame, CTkCheckBox, set_default_color_theme, set_appearance_mode
from Content.Filtros import Filter
from Content.Histograma import Equalize
from Content.MorfismoDP import Morphing
from Content.Morfologia import Morphology
from Content.Operacoes import Operations

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


def VALIDAR_FLOAT(text):
    if text == '': return True
    try:
        value = float(text)
    except ValueError:
        return False
    return 0<=value

class Main():
    def __init__(self):
        self.root = CTk()
        
        # Tamanho da janela TK
        self.tkwindow_width = self.root.winfo_screenwidth()
        self.tkwindow_height = self.root.winfo_screenheight()
        
        self.root.geometry(f"{self.tkwindow_width}x{self.tkwindow_height}")
        self.root.title("Processamento de Images")
        self.root.after(0, lambda: self.root.wm_state('zoomed'))
        
        set_default_color_theme("./Temas/theme.json")
        set_appearance_mode("dark")
        
        self.auxColor = "#FFFFFF"
        self.mainColor = "#000000"
        self.selectedColor = "#333333"
        
        self.generateWidgets()
        
        self.startPage()
        
        self.root.mainloop()
        
    def generateWidgets(self):
        self.processoString = ""
        
        # Widgets Padrão
        self.mainFrame = CTkFrame(self.root,border_width=5)
        
        self.auxFrame = CTkFrame(self.root,bg_color="gray", corner_radius=10)
        
        self.labelForma = CTkLabel(self.auxFrame, text="MENU", bg_color=self.mainColor, font=("Segoe UI Black", 40))

        self.placeHolderlabel = CTkLabel(self.mainFrame,text="PROCESSAMENTO DE IMAGENS\n2025.1", bg_color=self.mainColor, font=("Segoe UI Black", 40))

        #Menu Principal
        self.drawButton = CTkButton(self.auxFrame,text="FILTROS",font=("Segoe UI Black", 35),
                                    command=self.filterPage)
        
        self.ECGButton = CTkButton(self.auxFrame,text="OPERAÇÕES",font=("Segoe UI Black", 35),
                                    command=self.operationPage)
        
        self.morfismoButton = CTkButton(self.auxFrame,text="MORFISMO",font=("Segoe UI Black", 35),
                                    command=self.morfPage)
        
        self.eq_histogramaButton = CTkButton(self.auxFrame,text="EQUALIZAR\nHISTOGRAMA",font=("Segoe UI Black", 35),
                                    command=self.equalizePage)
        
        self.morfologiaButton = CTkButton(self.auxFrame,text="MORFOLOGIA",font=("Segoe UI Black", 35),
                                    command=self.morphologyPage)
        
        #Criando Menus
        self.menu = Menu(self.root)
        self.root.configure(menu=self.menu)
        
        filemenu = Menu(self.menu)
        self.menu.add_cascade(label='Menu', menu=filemenu)
        filemenu.add_command(label='Voltar', command= self.startPage)
        filemenu.add_separator()
        filemenu.add_command(label='Sair', command=self.root.quit)
        
        Graphic2D = Menu(self.menu)
        self.menu.add_cascade(label='Temas', menu=Graphic2D)
        Graphic2D.add_command(label="Dark", command=lambda:[set_appearance_mode("dark")])
        Graphic2D.add_command(label='light', command=lambda:[set_appearance_mode("light")])
        
    def startPage(self):
        self.labelForma.configure(text="MENU")
        self.labelForma.pack(anchor=CENTER,pady=20)
        limpa_frame(self.mainFrame)

        self.mainFrame.place(relx=0.330,rely=0.025,relheight=0.95,relwidth=0.65)
        self.auxFrame.place(relx=0.015,rely=0.025,relheight=0.95,relwidth=0.3)
        self.placeHolderlabel.place(relx=0.5,rely=0.5,anchor="c")
        
        self.auxFrame.place(relx=0.015,rely=0.025,relheight=0.95,relwidth=0.3)
        self.mainFrame.place(relx=0.330,rely=0.025,relheight=0.95,relwidth=0.65)
        
        self.drawButton.pack(anchor=CENTER,pady=15,ipady=10,ipadx=10)
        self.ECGButton.pack(anchor=CENTER,pady=15,ipady=10,ipadx=10)
        self.morfismoButton.pack(anchor=CENTER,pady=15,ipady=10,ipadx=10)
        self.eq_histogramaButton.pack(anchor=CENTER,pady=15,ipady=10,ipadx=10)
        self.morfologiaButton.pack(anchor=CENTER,pady=15,ipady=10,ipadx=10)
    
    def filterPage(self):
        limpa_frame(self.mainFrame)
        
        Filter(self.mainFrame).place(relx=0,rely=0,relwidth=1,relheight=1)
        
        self.auxFrame.place_forget()
        self.mainFrame.place(relx=0.025,rely=0.025,relwidth=0.95,relheight=0.95)
    
    def operationPage(self):
        limpa_frame(self.mainFrame)
        
        Operations(self.mainFrame).place(relx=0,rely=0,relwidth=1,relheight=1)
        
        self.auxFrame.place_forget()
        self.mainFrame.place(relx=0.025,rely=0.025,relwidth=0.95,relheight=0.95)
    
    def morfPage(self):
        limpa_frame(self.mainFrame)
        
        Morphing(self.mainFrame).place(relx=0,rely=0,relwidth=1,relheight=1)
        
        self.auxFrame.place_forget()
        self.mainFrame.place(relx=0.025,rely=0.025,relwidth=0.95,relheight=0.95)
    
    def equalizePage(self):
        limpa_frame(self.mainFrame)
        
        Equalize(self.mainFrame).place(relx=0,rely=0,relwidth=1,relheight=1)
        
        self.auxFrame.place_forget()
        self.mainFrame.place(relx=0.025,rely=0.025,relwidth=0.95,relheight=0.95)
    
    def morphologyPage(self):
        limpa_frame(self.mainFrame)
        
        Morphology(self.mainFrame).place(relx=0,rely=0,relwidth=1,relheight=1)
        
        self.auxFrame.place_forget()
        self.mainFrame.place(relx=0.025,rely=0.025,relwidth=0.95,relheight=0.95)
        
Main()