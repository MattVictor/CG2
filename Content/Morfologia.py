import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

class Morphology(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Variáveis de estado
        self.morf_img_array = None
        self.morf_img_original_pil = None
        
        # Configuração do grid principal deste frame
        self.pack_propagate(False)
        
        # --- Chama o método que constrói a interface ---
        self.criar_interface_morfologia()

    def criar_interface_morfologia(self):
        """Cria todos os widgets para a interface de morfologia."""
        # Layout
        control_frame = customtkinter.CTkFrame(self)
        control_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        display_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        display_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_columnconfigure(1, weight=1)
        display_frame.grid_rowconfigure(0, weight=1)

        # --- Widgets de Controle ---
        customtkinter.CTkButton(control_frame, text="Carregar Imagem", command=self.morf_carregar_imagem).pack(side="left", padx=60, pady=10)

        # Seletor de Modo (Binário / Nível de Cinza)
        self.morf_mode_var = customtkinter.StringVar(value="cinza")
        customtkinter.CTkLabel(control_frame, text="Modo:").pack(side="left", padx=(50, 5), pady=10)
        customtkinter.CTkRadioButton(control_frame, text="Nível de Cinza", variable=self.morf_mode_var, value="cinza", command=self.morf_processar_e_exibir_original).pack(side="left", pady=10)
        customtkinter.CTkRadioButton(control_frame, text="Binário", variable=self.morf_mode_var, value="binario", command=self.morf_processar_e_exibir_original).pack(side="left", padx=5, pady=10)

        # Seletor de Operador Morfológico
        operations = ["Dilatação", "Erosão", "Abertura", "Fechamento", "Gradiente Morfológico", "Extração de Fronteira", "Borda Interna",
                      "Borda Externa", "Top-Hat", "Bottom-Hat"]
        self.morf_op_var = customtkinter.StringVar(value="Dilatação")
        op_menu = customtkinter.CTkComboBox(control_frame, variable=self.morf_op_var, values=operations, state="readonly", width=200)
        op_menu.pack(side="left", padx=50, pady=10)

        # Seletor de Elemento Estruturante
        elementos_estruturantes = ["Quadrado 3x3", "Cruz 3x3", "X 3x3"]
        self.morf_ee_var = customtkinter.StringVar(value="Quadrado 3x3")
        ee_menu = customtkinter.CTkComboBox(control_frame, variable=self.morf_ee_var, values=elementos_estruturantes, state="readonly", width=150)
        ee_menu.pack(side="left", padx=50, pady=10)

        customtkinter.CTkButton(control_frame, text="Aplicar", command=self.morf_aplicar_operacao).pack(side="left", padx=50, pady=10)

        # Displays de Imagem
        self.morf_label_orig = customtkinter.CTkLabel(display_frame, text="Imagem Original", fg_color=("gray85", "gray17"))
        self.morf_label_orig.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.morf_label_proc = customtkinter.CTkLabel(display_frame, text="Imagem Processada", fg_color=("gray85", "gray17"))
        self.morf_label_proc.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    def morf_carregar_imagem(self):
        """Carrega uma imagem, processa de acordo com o modo e exibe."""
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.jpg *.png *.bmp"), ("Todos os arquivos", "*.*")])
        if not path: return
        self.morf_img_original_pil = Image.open(path).convert("L")
        self.morf_processar_e_exibir_original()

    def morf_processar_e_exibir_original(self):
        """Converte a imagem para binária ou cinza e a exibe no painel original."""
        if not self.morf_img_original_pil: return

        if self.morf_mode_var.get() == "binario":
            img_array_temp = np.array(self.morf_img_original_pil)
            self.morf_img_array = ((img_array_temp > 127) * 255).astype('uint8')
        else:
            self.morf_img_array = np.array(self.morf_img_original_pil)

        self._exibir_imagem(Image.fromarray(self.morf_img_array), self.morf_label_orig)
        self.morf_label_proc.configure(image=None, text="Imagem Processada")

    def morf_aplicar_operacao(self):
        if self.morf_img_array is None: messagebox.showerror("Erro",
                                                             "Carregue uma imagem na aba 'Morfologia'."); return

        op = self.morf_op_var.get()
        ee = self._get_elemento_estruturante(self.morf_ee_var.get())
        is_binary = (self.morf_mode_var.get() == "binario")
        resultado_array = None
        try:
            if op == "Erosão":
                resultado_array = self._dilatacao(self.morf_img_array, ee, is_binary)
           
            elif op == "Dilatação":
                resultado_array = self._erosao(self.morf_img_array, ee, is_binary)
            
            elif op == "Abertura":
                erodido = self._erosao(self.morf_img_array, ee, is_binary)
                resultado_array = self._dilatacao(erodido, ee, is_binary)
            
            elif op == "Fechamento":
                dilatado = self._dilatacao(self.morf_img_array, ee, is_binary)
                resultado_array = self._erosao(dilatado, ee, is_binary)
            
            elif op == "Gradiente Morfológico":
                dilatado = self._dilatacao(self.morf_img_array, ee, is_binary).astype(np.float32)
                erodido = self._erosao(self.morf_img_array, ee, is_binary).astype(np.float32)
                resultado_array = np.subtract(dilatado,erodido)

            elif op == "Borda Interna":
                # Fórmula: Original - Erosão
                erodido = self._erosao(self.morf_img_array, ee, is_binary).astype(np.float32)
                resultado_array = self.morf_img_array.astype(np.float32) - erodido

            elif op == "Borda Externa":
                dilatado = self._dilatacao(self.morf_img_array, ee, is_binary).astype(np.float32)
                resultado_array = dilatado - self.morf_img_array.astype(np.float32)

            elif op == "Top-Hat":
                # Fórmula: Original - Abertura
                erodido = self._erosao(self.morf_img_array, ee, is_binary)
                abertura = self._dilatacao(erodido, ee, is_binary).astype(np.float32)
                resultado_array = self.morf_img_array.astype(np.float32) - abertura

            elif op == "Bottom-Hat":
                # Fórmula: Fechamento - Original
                dilatado = self._dilatacao(self.morf_img_array, ee, is_binary)
                fechamento = self._erosao(dilatado, ee, is_binary).astype(np.float32)
                resultado_array = fechamento - self.morf_img_array.astype(np.float32)

            if resultado_array is not None:
                resultado_final = np.clip(resultado_array, 0, 255).astype(np.uint8)
                self._exibir_imagem(Image.fromarray(resultado_final), self.morf_label_proc)
        except:
            messagebox.showerror("ERRO", "Ocorreu um erro durante a operação")

    def _exibir_imagem(self, pil_image, label_widget):
        """Redimensiona e exibe uma imagem da PIL em um CTkLabel."""
        if pil_image is None: 
            label_widget.configure(image=None, text="") # Limpa a imagem se for None
            return
        
        # Redimensiona a imagem para caber na tela sem perder a proporção
        max_size = (500, 500)
        img_copy = pil_image.copy()
        img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        ctk_img = customtkinter.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        
        label_widget.configure(image=ctk_img, text="")

        # --- CORREÇÃO OBRIGATÓRIA ---
        # Guarda uma referência da imagem no próprio widget para evitar
        # que ela seja apagada da memória.
        label_widget.image = ctk_img

    def _get_elemento_estruturante(self, nome_ee):
        """Retorna a matriz NumPy para um dado Elemento Estruturante."""
        if nome_ee == "Quadrado 3x3":
            return np.ones((3, 3), dtype=np.uint8)
        elif nome_ee == "Cruz 3x3":
            return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        elif nome_ee == "X 3x3":
            return np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]], dtype=np.uint8)
        return np.ones((3, 3), dtype=np.uint8)

    # --- FUNÇÕES DE MORFOLOGIA MANUAL (GENERALIZADAS) ---
    def _apply_morphological_op(self, image_array, ee, mode, func_binary, func_grayscale):
        """Função genérica para aplicar uma operação morfológica."""
        h, w = image_array.shape
        ee_h, ee_w = ee.shape
        pad_h, pad_w = ee_h // 2, ee_w // 2

        output_array = np.zeros_like(image_array)
        img_pad = np.pad(image_array, pad_width=((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        
        ee_mask = (ee == 1)

        for y in range(h):
            for x in range(w):
                vizinhanca = img_pad[y:y + ee_h, x:x + ee_w]
                vizinhanca_sob_ee = vizinhanca[ee_mask]
                
                if mode == "binario":
                    output_array[y, x] = func_binary(vizinhanca_sob_ee)
                else: # "cinza"
                    output_array[y, x] = func_grayscale(vizinhanca_sob_ee)
        return output_array

    def _dilatacao(self, image_array, ee, is_binary):
        """Aplica a DILATAÇÃO manual, para binário ou nível de cinza."""
        mode = "binario" if is_binary else "cinza"
        # DILATAÇÃO: Pega o valor MÁXIMO na vizinhança.
        # No modo binário, se QUALQUER pixel for 255, o resultado é 255.
        func_b = lambda v: 255 if np.any(v == 255) else 0
        func_g = lambda v: np.max(v)
        return self._apply_morphological_op(image_array, ee, mode, func_b, func_g)

    def _erosao(self, image_array, ee, is_binary):
        """Aplica a EROSÃO manual, para binário ou nível de cinza."""
        mode = "binario" if is_binary else "cinza"
        # EROSÃO: Pega o valor MÍNIMO na vizinhança.
        # No modo binário, se TODOS os pixels forem 255, o resultado é 255.
        func_b = lambda v: 255 if np.all(v == 255) else 0
        func_g = lambda v: np.min(v)
        return self._apply_morphological_op(image_array, ee, mode, func_b, func_g)