__package__ = None # Garante a execução como script

import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class FiltrosFrame(customtkinter.CTkFrame):
    """Um frame que encapsula todas as funcionalidades de filtros de imagem."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # --- Variáveis de Instância ---
        self.img_original_pil = None
        self.img_processada_pil = None
        self.img_original_tk = None
        self.img_processada_tk = None

        # --- Configuração do Grid Principal ---
        self.grid_rowconfigure(2, weight=1) # Linha de display (2) expande
        self.grid_columnconfigure(0, weight=1)

        # --- Frame de Controles (Linha 0) ---
        control_frame = customtkinter.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        btn_carregar = customtkinter.CTkButton(control_frame, text="Carregar Imagem", command=self._carregar_imagem)
        btn_carregar.pack(side="left", padx=10, pady=10)

        operations = {
            "Negativo": "negativo", "Gamma": "gamma", "Logarítmica": "log", "Sigmoide": "sigmoide",
            "Ajuste de Faixa Dinâmica": "faixa_dinamica", "Linear": "linear", "Filtro da Média": "media",
            "Filtro da Mediana": "mediana", "Passa-Altas Básico": "laplaciano",
            "Bordas (Sobel)": "sobel", "Bordas (Prewitt)": "prewitt",
            "Bordas (Roberts)": "roberts", "Bordas (Roberts Cruzado)": "roberts_cruzado",
            "Realce (High-Boost)": "high_boost"
        }
        
        self.op_menu = customtkinter.CTkComboBox(control_frame, values=list(operations.keys()), state="readonly", width=200)
        self.op_menu.set("Negativo")
        self.op_menu.pack(side="left", padx=10, pady=10)

        btn_aplicar = customtkinter.CTkButton(control_frame, text="Aplicar", command=lambda: self._aplicar_operacao(operations[self.op_menu.get()]))
        btn_aplicar.pack(side="left", padx=10, pady=10)

        # --- Frame do Inspetor (Linha 1) ---
        inspector_frame = customtkinter.CTkFrame(self)
        inspector_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        customtkinter.CTkLabel(inspector_frame, text="Vizinhança do Pixel (3x3):").pack(side="left", padx=(10,0))
        grid_frame = customtkinter.CTkFrame(inspector_frame, fg_color="transparent")
        grid_frame.pack(side="left", padx=10)
        
        self.pixel_grid_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                lbl = customtkinter.CTkLabel(grid_frame, text="---", width=35, height=35, font=("Consolas", 10))
                lbl.grid(row=i, column=j, padx=1, pady=1)
                row_labels.append(lbl)
            self.pixel_grid_labels.append(row_labels)

        # --- Frame de Display das Imagens (Linha 2) ---
        display_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        display_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure((0, 1), weight=1)
        display_frame.grid_rowconfigure(0, weight=1)

        self.label_orig = customtkinter.CTkLabel(display_frame, text="Imagem Original", fg_color=("gray85", "gray17"))
        self.label_orig.grid(row=0, column=0, sticky="nsew", padx=5)
        
        self.label_proc = customtkinter.CTkLabel(display_frame, text="Imagem Processada", fg_color=("gray85", "gray17"))
        self.label_proc.grid(row=0, column=1, sticky="nsew", padx=5)

        # Vincula eventos do mouse
        self.label_orig.bind("<Motion>", lambda e: self._mostrar_info_pixel(e, 'original'))
        self.label_proc.bind("<Motion>", lambda e: self._mostrar_info_pixel(e, 'processada'))
        self.label_orig.bind("<Leave>", self._limpar_info_pixel)
        self.label_proc.bind("<Leave>", self._limpar_info_pixel)

    # --- Métodos da Lógica Principal ---

    def _carregar_imagem(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.jpg *.png"), ("Todos os arquivos", "*.*")])
        if not path: return
        
        self.img_original_pil = Image.open(path).convert("L")
        self.img_processada_pil = None
        
        self.img_original_tk = self._exibir_imagem(self.img_original_pil, self.label_orig)
        
        self.label_proc.configure(image=None, text="Imagem Processada")
        self.label_proc.image = None
        self._limpar_info_pixel()

    def _get_input_dialog(self, title, text, initial_value, type_cast=float):
        """Auxiliar para caixas de diálogo de input."""
        dialog = customtkinter.CTkInputDialog(title=title, text=text)
        # CTkInputDialog não suporta valor inicial, então pegamos o input
        input_str = dialog.get_input()
        if input_str is None: return None
        try:
            return type_cast(input_str)
        except (ValueError, TypeError):
            messagebox.showerror("Entrada Inválida", f"Por favor, insira um número válido.")
            return None

    def _aplicar_operacao(self, op_value):
        if not self.img_original_pil:
            messagebox.showerror("Erro", "Carregue uma imagem primeiro.")
            return
            
        self.winfo_toplevel().configure(cursor="watch")
        self.update_idletasks()
        
        img_array = np.array(self.img_original_pil, dtype=np.float32)
        proc_array = None
        
        try:
            if op_value == 'negativo': proc_array = 255 - img_array
            elif op_value == 'gamma':
                gamma = self._get_input_dialog("Input", "Gamma (ex: 0.5):", 0.5, float)
                if gamma is not None: proc_array = ((img_array / 255.0) ** gamma) * 255.0
            elif op_value == 'log':
                c = 255 / np.log(1 + np.max(img_array))
                proc_array = c * np.log(1 + img_array)
            elif op_value == 'sigmoide':
                w = self._get_input_dialog("Input", "Centro (w, ex: 128):", 128, float)
                sigma = self._get_input_dialog("Input", "Largura (σ, ex: 25):", 25, float)
                if w is not None and sigma is not None and sigma != 0: proc_array = 255 * (1 / (1 + np.exp(-(img_array - w) / sigma)))
            elif op_value == 'faixa_dinamica':
                f_min, f_max = np.min(img_array), np.max(img_array)
                proc_array = img_array if f_max == f_min else ((img_array - f_min) / (f_max - f_min)) * 255
            elif op_value == 'linear':
                a = self._get_input_dialog("Input", "Contraste (a, ex: 1.5):", 1.5, float)
                b = self._get_input_dialog("Input", "Brilho (b, ex: -20):", 0, int)
                if a is not None and b is not None: proc_array = a * img_array + b
            elif op_value == 'media': proc_array = self._convolve_manual(img_array, np.ones((3, 3)) / 9.0)
            elif op_value == 'mediana': proc_array = self._mediana_manual(img_array)
            elif op_value == 'laplaciano': proc_array = self._convolve_manual(img_array, np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]))
            elif op_value == 'sobel':
                gy = self._convolve_manual(img_array, np.array([[-1,-2,-1],[0,0,0],[1,2,1]]))
                gx = self._convolve_manual(img_array, np.array([[-1,0,1],[-2,0,2],[-1,0,1]]))
                proc_array = np.sqrt(gx**2 + gy**2)
            elif op_value == 'prewitt':
                gy = self._convolve_manual(img_array, np.array([[-1,-1,-1],[0,0,0],[1,1,1]]))
                gx = self._convolve_manual(img_array, np.array([[-1,0,1],[-1,0,1],[-1,0,1]]))
                proc_array = np.abs(gx) + np.abs(gy)
            elif op_value == 'roberts':
                gy = self._convolve_manual(img_array, np.array([[0,0,0],[0,1,0],[0,-1,0]]))
                gx = self._convolve_manual(img_array, np.array([[0,0,0],[0,1,-1],[0,0,0]]))
                proc_array = np.abs(gx) + np.abs(gy)
            elif op_value == 'roberts_cruzado':
                g_d1 = self._convolve_manual(img_array, np.array([[0,0,0],[0,1,0],[0,0,-1]]))
                g_d2 = self._convolve_manual(img_array, np.array([[0,0,0],[0,0,1],[0,-1,0]]))
                proc_array = np.abs(g_d1) + np.abs(g_d2)
            elif op_value == 'high_boost':
                fator_a = self._get_input_dialog("Input", "Fator de Realce A (A > 1):", 1.1, float)
                if fator_a is not None and fator_a > 1.0:
                    passa_baixa = self._convolve_manual(img_array, np.ones((3, 3)) / 9.0)
                    g_mascara = img_array - passa_baixa
                    proc_array = img_array + fator_a * g_mascara

            if proc_array is not None:
                proc_array = np.clip(proc_array, 0, 255)
                self.img_processada_pil = Image.fromarray(proc_array.astype(np.uint8))
                self.img_processada_tk = self._exibir_imagem(self.img_processada_pil, self.label_proc)
        finally:
            self.winfo_toplevel().configure(cursor="")

    def _mostrar_info_pixel(self, event, tipo_imagem):
        imagem_pil, imagem_tk = (self.img_original_pil, self.img_original_tk) if tipo_imagem == 'original' else (self.img_processada_pil, self.img_processada_tk)
        if not all((imagem_pil, imagem_tk)): return

        widget_w, widget_h = event.widget.winfo_width(), event.widget.winfo_height()
        img_w, img_h = imagem_tk.size

        offset_x, offset_y = (widget_w - img_w) / 2, (widget_h - img_h) / 2
        mouse_x, mouse_y = event.x - offset_x, event.y - offset_y

        if not (0 <= mouse_x < img_w and 0 <= mouse_y < img_h):
            self._limpar_info_pixel()
            return

        orig_w, orig_h = imagem_pil.size
        scale_x, scale_y = orig_w / img_w, orig_h / img_h
        real_x, real_y = int(mouse_x * scale_x), int(mouse_y * scale_y)

        for i, row_lbl in enumerate(self.pixel_grid_labels):
            for j, lbl in enumerate(row_lbl):
                nx, ny = real_x -1 + j, real_y -1 + i
                # Cor de fundo para o pixel central
                bg_color = ("#335B85", "#223E5C") if i == 1 and j == 1 else "transparent"
                lbl.configure(fg_color=bg_color)
                if 0 <= nx < orig_w and 0 <= ny < orig_h:
                    lbl.configure(text=str(imagem_pil.getpixel((nx, ny))))
                else:
                    lbl.configure(text="")

    def _limpar_info_pixel(self, event=None):
        for i in range(3):
            for j in range(3): 
                self.pixel_grid_labels[i][j].configure(text="---", fg_color="transparent")

    # --- Métodos de Apoio e Placeholders ---
    
    def _exibir_imagem(self, pil_image, label_widget):
        """Redimensiona, exibe e mantém referência da imagem."""
        if pil_image is None:
            label_widget.configure(image=None)
            return None
        
        max_size = (600, 600) # Tamanho máximo para exibição
        img_copy = pil_image.copy()
        img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        ctk_img = customtkinter.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img # Previne garbage collection
        return ctk_img

    def _convolve_manual(self, image_array, kernel):
        """Placeholder para sua função de convolução."""
        print(f"-> Chamando convolução com kernel:\n{kernel}")
        # Retorna a imagem original como padrão
        return image_array

    def _mediana_manual(self, image_array):
        """Placeholder para sua função de filtro da mediana."""
        print("-> Chamando filtro da mediana.")
        # Retorna a imagem original como padrão
        return image_array


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    app = customtkinter.CTk()
    app.title("Processador de Imagens - CustomTkinter")
    app.geometry("1280x800")

    # Cria uma aba para conter nosso frame de filtros
    tabview = customtkinter.CTkTabview(app)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)
    tabview.add("Filtros")

    # Instancia nosso frame dentro da aba
    frame_filtros = FiltrosFrame(master=tabview.tab("Filtros"))
    frame_filtros.pack(fill="both", expand=True)

    app.mainloop()