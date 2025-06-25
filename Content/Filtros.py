__package__

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageFilter
import numpy as np


# A biblioteca SciPy não é mais necessária

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Processador de Imagens - Convolução Manual")
        self.root.geometry("1100x700")

        # Variáveis para armazenar os caminhos e objetos de imagem
        self.original_image_path = None
        self.original_pil_image = None
        self.processed_pil_image = None

        # --- Estrutura da Interface (Frames) ---
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        image_frame = tk.Frame(root, padx=10, pady=10)
        image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- Controles ---
        self.btn_open = tk.Button(control_frame, text="Selecionar Imagem", command=self.select_image)
        self.btn_open.grid(row=0, column=0, padx=10, pady=5)

        self.lbl_path = tk.Label(control_frame, text="Nenhuma imagem selecionada")
        self.lbl_path.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.operations = {
            "Filtro da Média (Manual)": "media_kernel",
            "Filtro da Mediana (Estatístico)": "mediana",
            "Aguçamento (Laplaciano Manual)": "agucamento_laplaciano",
            "Bordas (Prewitt Manual)": "bordas_prewitt",
            "Bordas (Sobel Manual)": "bordas_sobel",
            "Equalização de Histograma": "equalizacao_histograma"
        }
        self.operation_var = tk.StringVar(value="Bordas (Sobel Manual)")
        self.operation_menu = ttk.Combobox(control_frame, textvariable=self.operation_var,
                                           values=list(self.operations.keys()), state="readonly", width=30)
        self.operation_menu.grid(row=1, column=0, padx=10, pady=5)

        self.btn_apply = tk.Button(control_frame, text="Aplicar Operação", command=self.apply_operation)
        self.btn_apply.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.btn_save = tk.Button(control_frame, text="Salvar Imagem", command=self.save_image, state=tk.DISABLED)
        self.btn_save.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.original_label = tk.Label(image_frame, text="Imagem Original", relief="solid", bd=1)
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.processed_label = tk.Label(image_frame, text="Imagem Processada", relief="solid", bd=1)
        self.processed_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def aplicar_filtro_manual(self, image_array, kernel):
        """
        Aplica um filtro de convolução manualmente, pixel a pixel.
        Esta função demonstra o algoritmo g(x,y) = T[f(x,y)].
        """
        # Dimensões da imagem e do kernel
        img_h, img_w = image_array.shape
        ker_h, ker_w = kernel.shape

        # Calcula o preenchimento (padding) para centralizar o kernel
        pad_h = ker_h // 2
        pad_w = ker_w // 2

        # Cria uma matriz de saída vazia (preenchida com zeros)
        output_array = np.zeros_like(image_array)

        # Laço principal: percorre cada pixel da imagem
        for y in range(img_h):
            for x in range(img_w):
                soma = 0.0
                # Laço secundário: percorre a vizinhança definida pelo kernel
                for ky in range(ker_h):
                    for kx in range(ker_w):
                        # Encontra a coordenada correspondente na imagem
                        img_y = y - pad_h + ky
                        img_x = x - pad_w + kx

                        # Tratamento de bordas: replica a borda mais próxima
                        img_y = max(0, min(img_y, img_h - 1))
                        img_x = max(0, min(img_x, img_w - 1))

                        # Operação de convolução: multiplica o pixel pelo valor do kernel
                        soma += image_array[img_y, img_x] * kernel[ky, kx]

                # Atribui o valor calculado ao pixel correspondente na imagem de saída
                output_array[y, x] = soma

        return output_array

    def aplicar_filtro_mediana_manual(self, image_array, window_size=3):
        """Aplica o filtro da mediana manualmente, pixel a pixel."""
        img_h, img_w = image_array.shape
        pad = window_size // 2
        output_array = np.zeros_like(image_array)

        for y in range(img_h):
            for x in range(img_w):
                vizinhanca = []
                for wy in range(window_size):
                    for wx in range(window_size):
                        img_y = max(0, min(y - pad + wy, img_h - 1))
                        img_x = max(0, min(x - pad + wx, img_w - 1))
                        vizinhanca.append(image_array[img_y, img_x])

                vizinhanca.sort()
                mediana = vizinhanca[len(vizinhanca) // 2]
                output_array[y, x] = mediana

        return output_array

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Arquivos de Imagem", "*.jpg *.jpeg *.png *.bmp *.gif *.pgm")])
        if not path: return
        self.original_image_path = path
        self.lbl_path.config(text=self.original_image_path)
        self.original_pil_image = Image.open(path)
        self.display_image(self.original_pil_image, self.original_label)
        self.processed_label.config(image='', text="Imagem Processada")
        self.processed_pil_image = None
        self.btn_save.config(state=tk.DISABLED)

    def apply_operation(self):
        if not self.original_pil_image:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return

        operation_key = self.operation_var.get()
        operation_value = self.operations[operation_key]

        self.root.config(cursor="watch")  # Mudar o cursor para "espera"
        self.root.update()

        img_gray = self.original_pil_image.convert("L")
        img_array = np.array(img_gray, dtype=np.float32)
        processed_array = None

        if operation_value == 'media_kernel':
            kernel = np.ones((3, 3)) / 9.0
            processed_array = self.aplicar_filtro_manual(img_array, kernel)

        elif operation_value == 'agucamento_laplaciano':
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            processed_array = self.aplicar_filtro_manual(img_array, kernel)

        elif operation_value == 'bordas_prewitt':
            kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
            kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            grad_y = self.aplicar_filtro_manual(img_array, kernel_y)
            grad_x = self.aplicar_filtro_manual(img_array, kernel_x)
            processed_array = np.sqrt(grad_x ** 2 + grad_y ** 2)

        elif operation_value == 'bordas_sobel':
            kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
            kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            grad_y = self.aplicar_filtro_manual(img_array, kernel_y)
            grad_x = self.aplicar_filtro_manual(img_array, kernel_x)
            processed_array = np.sqrt(grad_x ** 2 + grad_y ** 2)

        elif operation_value == 'mediana':
            processed_array = self.aplicar_filtro_mediana_manual(img_array, window_size=3)

        elif operation_value == 'equalizacao_histograma':
            self.processed_pil_image = ImageOps.equalize(img_gray)

        if processed_array is not None:
            processed_array = np.clip(processed_array, 0, 255)
            self.processed_pil_image = Image.fromarray(processed_array.astype(np.uint8))

        if self.processed_pil_image:
            self.display_image(self.processed_pil_image, self.processed_label)
            self.btn_save.config(state=tk.NORMAL)

        self.root.config(cursor="")  # Restaurar o cursor padrão

    def display_image(self, pil_image, label):
        max_size = (500, 500)
        display_image = pil_image.copy()
        display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(display_image)
        label.config(image=tk_image, text="")
        label.image = tk_image

    def save_image(self):
        if not self.processed_pil_image:
            messagebox.showerror("Erro", "Não há imagem processada para salvar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Bitmap", "*.bmp")])
        if not filepath: return
        try:
            if self.processed_pil_image.mode != 'RGB':
                self.processed_pil_image.convert('L').save(filepath)
            else:
                self.processed_pil_image.save(filepath)
            messagebox.showinfo("Sucesso", f"Imagem salva com sucesso em:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()