__package__

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np


# Widget personalizado para desenhar um histograma em um Canvas do Tkinter
class HistogramCanvas(tk.Frame):
    def __init__(self, parent, width=400, height=200):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, width=width, height=height, bg='white', relief="solid", bd=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def plot(self, histogram_data):
        """Desenha os dados do histograma no canvas."""
        self.canvas.delete("all")  # Limpa o desenho anterior

        if histogram_data is None or len(histogram_data) == 0:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # A altura precisa ser um pouco menor para dar uma margem
        plot_height = canvas_height - 10

        max_count = max(histogram_data)
        if max_count == 0: return  # Evita divisão por zero

        # Calcula a largura de cada barra
        bar_width = canvas_width / len(histogram_data)

        # Desenha uma barra para cada nível de intensidade
        for i, count in enumerate(histogram_data):
            # Normaliza a altura da barra para caber no canvas
            bar_height = (count / max_count) * plot_height

            x0 = i * bar_width
            y0 = canvas_height - bar_height
            x1 = (i + 1) * bar_width
            y1 = canvas_height

            self.canvas.create_rectangle(x0, y0, x1, y1, fill="gray", outline="")

        # Adiciona eixos simples
        self.canvas.create_line(0, canvas_height, canvas_width, canvas_height, fill='black')
        self.canvas.create_text(10, canvas_height - 10, text="0", anchor="sw")
        self.canvas.create_text(canvas_width - 10, canvas_height - 10, text="255", anchor="se")


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equalização de Histograma Manual")
        self.root.geometry("1100x800")

        self.original_pil_image = None

        # --- Estrutura da Interface ---
        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        display_frame = tk.Frame(root, padx=10, pady=10)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for i in range(2):
            display_frame.columnconfigure(i, weight=1)
            display_frame.rowconfigure(i, weight=1)

        # --- Controles ---
        self.btn_open = tk.Button(control_frame, text="Selecionar Imagem (lena.pgm)", command=self.select_image)
        self.btn_open.pack(side=tk.LEFT, padx=10)
        self.btn_apply = tk.Button(control_frame, text="Equalizar Histograma (Manual)", command=self.apply_equalization)
        self.btn_apply.pack(side=tk.LEFT, padx=10)

        # --- Áreas de Exibição 2x2 ---
        self.label_orig = tk.Label(display_frame, text="Imagem Original", relief="solid", bd=1);
        self.label_orig.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.label_eq = tk.Label(display_frame, text="Imagem Equalizada", relief="solid", bd=1);
        self.label_eq.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        hist_orig_frame = tk.Frame(display_frame);
        hist_orig_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        hist_eq_frame = tk.Frame(display_frame);
        hist_eq_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        tk.Label(hist_orig_frame, text="Histograma Original").pack()
        self.hist_orig_canvas = HistogramCanvas(hist_orig_frame)
        self.hist_orig_canvas.pack(fill=tk.BOTH, expand=True)

        tk.Label(hist_eq_frame, text="Histograma Equalizado").pack()
        self.hist_eq_canvas = HistogramCanvas(hist_eq_frame)
        self.hist_eq_canvas.pack(fill=tk.BOTH, expand=True)

    def equalizacao_histograma_manual(self, image_array):
        """
        Executa a equalização de histograma manualmente.
        Retorna: a imagem equalizada, o histograma original e o histograma da imagem equalizada.
        """
        # Passo 1: Calcular o histograma da imagem original
        # O .flatten() transforma a matriz 2D em uma lista 1D de pixels
        histograma_original, _ = np.histogram(image_array.flatten(), bins=256, range=[0, 256])

        # Passo 2: Calcular a Função de Distribuição Acumulada (CDF)
        # O .cumsum() calcula a soma acumulada, que é exatamente a CDF
        cdf = histograma_original.cumsum()

        # Passo 3: Normalizar a CDF para criar a tabela de mapeamento (Look-Up Table - LUT)
        # Removemos os zeros da CDF para o mapeamento e normalizamos
        cdf_masked = np.ma.masked_equal(cdf, 0)
        cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
        # Preenche os valores que eram zero com zero novamente
        cdf_final = np.ma.filled(cdf_masked, 0).astype('uint8')

        # Passo 4: Mapear os pixels da imagem original para os novos valores usando a LUT
        img_equalizada_array = cdf_final[image_array.astype('uint8')]

        # Passo 5: Calcular o histograma da nova imagem equalizada
        histograma_equalizado, _ = np.histogram(img_equalizada_array.flatten(), bins=256, range=[0, 256])

        return img_equalizada_array, histograma_original, histograma_equalizado

    def select_image(self):
        """Carrega uma imagem, a exibe e plota seu histograma inicial."""
        path = filedialog.askopenfilename(filetypes=[("PGM Images", "*.pgm"), ("All files", "*.*")])
        if not path: return

        self.original_pil_image = Image.open(path).convert("L")

        # Exibe a imagem original
        self.display_image(self.original_pil_image, self.label_orig)

        # Limpa as telas de resultado
        self.label_eq.config(image='', text="Imagem Equalizada");
        self.label_eq.image = None
        self.hist_orig_canvas.plot([])
        self.hist_eq_canvas.plot([])

        # Calcula e plota o histograma da imagem original
        self.root.update_idletasks()  # Força a atualização da UI para o canvas ter tamanho
        img_array = np.array(self.original_pil_image)
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        self.hist_orig_canvas.plot(hist)

    def apply_equalization(self):
        """Aplica a equalização e exibe todos os resultados."""
        if not self.original_pil_image:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return

        self.root.config(cursor="watch");
        self.root.update()

        img_array = np.array(self.original_pil_image)

        # Executa o algoritmo manual
        eq_array, hist_orig, hist_eq = self.equalizacao_histograma_manual(img_array)

        # Cria a imagem equalizada a partir do array
        img_equalizada = Image.fromarray(eq_array)

        # Exibe os resultados
        self.display_image(img_equalizada, self.label_eq)
        self.hist_orig_canvas.plot(hist_orig)
        self.hist_eq_canvas.plot(hist_eq)

        self.root.config(cursor="")

    def display_image(self, pil_image, label):
        """Redimensiona e exibe uma imagem da PIL em um Label do Tkinter."""
        max_width = label.winfo_width() if label.winfo_width() > 1 else 500
        max_height = label.winfo_height() if label.winfo_height() > 1 else 500

        display_image = pil_image.copy()
        display_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(display_image)
        label.config(image=tk_image, text="");
        label.image = tk_image


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()