import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

class Operations(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ops_img_a = None
        self.ops_img_b = None
        self.criar_aba_operacoes()

    def criar_aba_operacoes(self):
        # Layout principal da aba
        control_frame = customtkinter.CTkFrame(self)
        control_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        display_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        display_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        display_frame.grid_columnconfigure((0, 1, 2), weight=1)
        display_frame.grid_rowconfigure(1, weight=1)

        # Controles
        customtkinter.CTkButton(control_frame, text="Carregar Imagem A", command=lambda: self.ops_carregar_imagem('a')).pack(side="left", padx=10, pady=10)
        customtkinter.CTkButton(control_frame, text="Carregar Imagem B", command=lambda: self.ops_carregar_imagem('b')).pack(side="left", padx=10, pady=10)

        self.operations = {"Soma": "+", "Subtração": "-", "Multiplicação": "*", "Divisão": "/", "AND": "&", "OR": "|", "XOR": "^"}
        self.ops_op_var = customtkinter.StringVar(value="Soma")
        op_menu = customtkinter.CTkComboBox(control_frame, variable=self.ops_op_var, values=list(self.operations.keys()), state="readonly", width=150)
        op_menu.pack(side="left", padx=10, pady=10)

        customtkinter.CTkButton(control_frame, text="Calcular", command=self.ops_aplicar).pack(side="left", padx=10, pady=10)

        # Displays de Imagem (usando grid para melhor redimensionamento)
        customtkinter.CTkLabel(display_frame, text="Imagem A").grid(row=0, column=0)
        self.ops_label_a = customtkinter.CTkLabel(display_frame, text="", fg_color=("gray85", "gray17"))
        self.ops_label_a.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        customtkinter.CTkLabel(display_frame, text="Imagem B").grid(row=0, column=1)
        self.ops_label_b = customtkinter.CTkLabel(display_frame, text="", fg_color=("gray85", "gray17"))
        self.ops_label_b.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        customtkinter.CTkLabel(display_frame, text="Resultado").grid(row=0, column=2)
        self.ops_label_res = customtkinter.CTkLabel(display_frame, text="", fg_color=("gray85", "gray17"))
        self.ops_label_res.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

    def ops_carregar_imagem(self, target):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.jpg *.png"), ("Todos os arquivos", "*.*")])
        if not path: return
        img = Image.open(path).convert("L")
        if target == 'a':
            self.ops_img_a = img
            self._exibir_imagem(self.ops_img_a, self.ops_label_a)
        else:
            self.ops_img_b = img
            self._exibir_imagem(self.ops_img_b, self.ops_label_b)

    def ops_aplicar(self):
        if not self.ops_img_a or not self.ops_img_b:
            messagebox.showerror("Erro", "Carregue as duas imagens (A e B).")
            return
        
        if self.ops_img_a.size != self.ops_img_b.size:
            self.ops_img_b = self.ops_img_b.resize(self.ops_img_a.size, Image.Resampling.LANCZOS)
            self._exibir_imagem(self.ops_img_b, self.ops_label_b)
            messagebox.showwarning("Aviso", "Imagem B foi redimensionada para corresponder ao tamanho da Imagem A.")

        op_key = self.ops_op_var.get()
        op_symbol = self.operations[op_key]

        arr_a = np.array(self.ops_img_a, dtype=np.float32)
        arr_b = np.array(self.ops_img_b, dtype=np.float32)
        res_arr = None

        if op_symbol in ['+', '-', '*', '/']:
            if op_symbol == '+': res_arr = arr_a + arr_b
            elif op_symbol == '-': res_arr = arr_a - arr_b
            elif op_symbol == '*': res_arr = (arr_a / 255.0) * arr_b
            elif op_symbol == '/': res_arr = (arr_a / (arr_b + 1e-6)) * 255 # Escala para melhor visualização
        elif op_symbol in ['&', '|', '^']:
            arr_a_uint, arr_b_uint = arr_a.astype(np.uint8), arr_b.astype(np.uint8)
            if op_symbol == '&': res_arr = arr_a_uint & arr_b_uint
            elif op_symbol == '|': res_arr = arr_a_uint | arr_b_uint
            elif op_symbol == '^': res_arr = arr_a_uint ^ arr_b_uint

        if res_arr is not None:
            res_arr = np.clip(res_arr, 0, 255)
            res_img = Image.fromarray(res_arr.astype(np.uint8))
            self._exibir_imagem(res_img, self.ops_label_res)

    def _exibir_imagem(self, pil_image, label_widget):
        if pil_image is None: return
        max_w, max_h = 350, 350
        img_copy = pil_image.copy()
        img_copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        ctk_img = customtkinter.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        label_widget.configure(image=ctk_img, text="")