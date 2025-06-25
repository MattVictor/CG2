__package__

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import numpy as np
import math


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Imagens - Transformações Manuais")
        self.root.geometry("1100x700")

        self.original_pil_image = None
        self.processed_pil_image = None

        # --- Interface Gráfica (Frames e Widgets) ---
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        image_frame = tk.Frame(root, padx=10, pady=10)
        image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.btn_open = tk.Button(control_frame, text="Selecionar Imagem", command=self.select_image)
        self.btn_open.grid(row=0, column=0, padx=10, pady=5)
        self.lbl_path = tk.Label(control_frame, text="Nenhuma imagem selecionada")
        self.lbl_path.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # --- Dicionário de Operações ---
        self.operations = {
            # Novas transformações de intensidade manuais
            "a) Negativo da Imagem": "negativo_manual",
            "b) Transformação Gamma": "gamma_manual",
            "c) Transformação Logarítmica": "log_manual",
            "d) Transformação Sigmoide": "sigmoide_manual",
            "e) Ajuste de Faixa Dinâmica": "faixa_dinamica_manual",
            "f) Transformação Linear (Brilho/Contraste)": "linear_manual",
        }
        self.operation_var = tk.StringVar(value="a) Negativo da Imagem")
        self.operation_menu = ttk.Combobox(control_frame, textvariable=self.operation_var,
                                           values=list(self.operations.keys()), state="readonly", width=40)
        self.operation_menu.grid(row=1, column=0, padx=10, pady=5)

        self.btn_apply = tk.Button(control_frame, text="Aplicar Operação", command=self.apply_operation)
        self.btn_apply.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.btn_save = tk.Button(control_frame, text="Salvar Imagem", command=self.save_image, state=tk.DISABLED)
        self.btn_save.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.original_label = tk.Label(image_frame, text="Imagem Original", relief="solid", bd=1)
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.processed_label = tk.Label(image_frame, text="Imagem Processada", relief="solid", bd=1)
        self.processed_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    # --- Funções de Processamento Manuais ---
    def transformacao_negativo_manual(self, image_array):
        # Fórmula: S = 255 - r
        return 255 - image_array

    def transformacao_gamma_manual(self, image_array, gamma):
        # Fórmula: S = c * r^γ, com c=1
        array_normalizado = image_array / 255.0
        array_gamma = np.power(array_normalizado, gamma)
        return array_gamma * 255

    def transformacao_log_manual(self, image_array):
        # Fórmula: S = a * log(r + 1)
        # 'a' é a constante de escala para mapear para [0, 255]
        a = 255 / np.log(1 + np.max(image_array))
        return a * np.log(1 + image_array)

    def transformacao_sigmoide_manual(self, image_array, w_centro, sigma_largura):
        # Fórmula: S(r) = 255 * (1 / (1 + exp(-(r - w) / σ)))
        return 255 * (1 / (1 + np.exp(-(image_array - w_centro) / sigma_largura)))

    def transformacao_faixa_dinamica_manual(self, image_array):
        # Fórmula: f' = (f - f_min) / (f_max - f_min) * 255
        f_min, f_max = np.min(image_array), np.max(image_array)
        if f_max == f_min:
            return image_array  # Retorna a imagem original se for de cor sólida
        return ((image_array - f_min) / (f_max - f_min)) * 255

    def transformacao_linear_manual(self, image_array, a_contraste, b_brilho):
        # Fórmula: y = ax + b
        return a_contraste * image_array + b_brilho

    # --- Lógica Principal da Aplicação ---
    def apply_operation(self):
        if not self.original_pil_image:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return

        operation_key = self.operation_var.get()
        operation_value = self.operations[operation_key]

        self.root.config(cursor="watch");
        self.root.update()

        img_gray = self.original_pil_image.convert("L")
        img_array = np.array(img_gray, dtype=np.float32)
        processed_array = None

        # --- Mapeamento das operações para as funções manuais ---
        if operation_value == 'negativo_manual':
            processed_array = self.transformacao_negativo_manual(img_array)

        elif operation_value == 'gamma_manual':
            gamma = simpledialog.askfloat("Input", "Digite o valor de Gamma (ex: 0.5):", parent=self.root, minvalue=0.0)
            if gamma is not None:
                processed_array = self.transformacao_gamma_manual(img_array, gamma)

        elif operation_value == 'log_manual':
            processed_array = self.transformacao_log_manual(img_array)

        elif operation_value == 'sigmoide_manual':
            w = simpledialog.askfloat("Input", "Digite o centro (w, ex: 128):", parent=self.root)
            sigma = simpledialog.askfloat("Input", "Digite a largura (σ, ex: 25):", parent=self.root)
            if w is not None and sigma is not None and sigma != 0:
                processed_array = self.transformacao_sigmoide_manual(img_array, w, sigma)

        elif operation_value == 'faixa_dinamica_manual':
            processed_array = self.transformacao_faixa_dinamica_manual(img_array)

        elif operation_value == 'linear_manual':
            a = simpledialog.askfloat("Input", "Digite o fator de contraste (a, ex: 1.5):", parent=self.root)
            b = simpledialog.askinteger("Input", "Digite o ajuste de brilho (b, ex: -20):", parent=self.root)
            if a is not None and b is not None:
                processed_array = self.transformacao_linear_manual(img_array, a, b)

        elif operation_value == 'mediana_manual':
            processed_array = self.aplicar_filtro_mediana_manual(img_array, window_size=3)

        # Lógica para outros filtros...

        # --- Finalização e Exibição ---
        if processed_array is not None:
            processed_array = np.clip(processed_array, 0, 255)  # Garante que os valores fiquem em [0, 255]
            self.processed_pil_image = Image.fromarray(processed_array.astype(np.uint8))

        if self.processed_pil_image:
            self.display_image(self.processed_pil_image, self.processed_label)
            self.btn_save.config(state=tk.NORMAL)

        self.root.config(cursor="")

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png *.bmp *.gif *.pgm")])
        if not path: return
        self.original_pil_image = Image.open(path)
        self.lbl_path.config(text=path)
        self.display_image(self.original_pil_image, self.original_label)
        self.processed_label.config(image='', text="Imagem Processada")
        self.processed_pil_image = None;
        self.btn_save.config(state=tk.DISABLED)

    def display_image(self, pil_image, label):
        max_size = (500, 500)
        display_image = pil_image.copy()
        display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(display_image)
        label.config(image=tk_image, text="");
        label.image = tk_image

    def save_image(self):
        if not self.processed_pil_image:
            messagebox.showerror("Erro", "Não há imagem processada para salvar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if not filepath: return
        try:
            self.processed_pil_image.save(filepath)
            messagebox.showinfo("Sucesso", f"Imagem salva com sucesso em:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()