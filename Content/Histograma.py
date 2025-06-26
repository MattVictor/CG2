import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import numpy as np

# --- Configurações Globais do Tema ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Equalize(ctk.CTkFrame):
    """
    Um frame completo que encapsula toda a funcionalidade de visualização
    e equalização de histograma de uma imagem.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.original_pil_image = None

        # --- Estrutura da Interface ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        display_frame = ctk.CTkFrame(self, fg_color="transparent")
        display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        display_frame.grid_columnconfigure((0, 1), weight=1)
        display_frame.grid_rowconfigure((0, 1), weight=1)

        # --- Controles ---
        self.btn_open = ctk.CTkButton(control_frame, text="Selecionar Imagem", command=self.select_image, height=35)
        self.btn_open.pack(side="left", padx=10)
        self.btn_apply = ctk.CTkButton(control_frame, text="Equalizar Histograma", command=self.apply_equalization, height=35)
        self.btn_apply.pack(side="left", padx=10)

        # --- Áreas de Exibição 2x2 ---
        orig_img_frame = ctk.CTkFrame(display_frame)
        orig_img_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.label_orig = ctk.CTkLabel(orig_img_frame, text="Imagem Original")
        self.label_orig.pack(fill="both", expand=True, padx=5, pady=5)

        eq_img_frame = ctk.CTkFrame(display_frame)
        eq_img_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.label_eq = ctk.CTkLabel(eq_img_frame, text="Imagem Equalizada")
        self.label_eq.pack(fill="both", expand=True, padx=5, pady=5)

        hist_orig_frame = ctk.CTkFrame(display_frame)
        hist_orig_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(hist_orig_frame, text="Histograma Original", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        self.hist_orig_canvas = tk.Canvas(hist_orig_frame, bg="#2b2b2b", relief="sunken", bd=1, highlightthickness=0)
        self.hist_orig_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        hist_eq_frame = ctk.CTkFrame(display_frame)
        hist_eq_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(hist_eq_frame, text="Histograma Equalizado", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        self.hist_eq_canvas = tk.Canvas(hist_eq_frame, bg="#2b2b2b", relief="sunken", bd=1, highlightthickness=0)
        self.hist_eq_canvas.pack(fill="both", expand=True, padx=5, pady=5)

    def _plot_histogram(self, canvas, histogram_data):
        canvas.delete("all")
        if histogram_data is None or len(histogram_data) == 0:
            return
        canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()
        bar_color, axis_color = "#a0a0a0", "#c0c0c0"
        plot_height = canvas_height - 20
        max_count = max(histogram_data)
        if max_count == 0: return
        bar_width = canvas_width / len(histogram_data)
        for i, count in enumerate(histogram_data):
            bar_height = (count / max_count) * plot_height
            x0, y0 = i * bar_width, canvas_height - bar_height
            x1, y1 = (i + 1) * bar_width, canvas_height
            canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="")
        canvas.create_line(0, canvas_height, canvas_width, canvas_height, fill=axis_color)
        canvas.create_text(10, canvas_height - 10, text="0", anchor="sw", fill=axis_color)
        canvas.create_text(canvas_width - 10, canvas_height - 10, text="255", anchor="se", fill=axis_color)

    def equalizacao_histograma_manual(self, image_array):
        histograma_original, _ = np.histogram(image_array.flatten(), bins=256, range=[0, 256])
        cdf = histograma_original.cumsum()
        cdf_masked = np.ma.masked_equal(cdf, 0)
        if (cdf_masked.max() - cdf_masked.min()) == 0:
            cdf_final = np.ma.filled(cdf_masked, 0).astype('uint8')
        else:
            cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
            cdf_final = np.ma.filled(cdf_masked, 0).astype('uint8')
        img_equalizada_array = cdf_final[image_array.astype('uint8')]
        histograma_equalizado, _ = np.histogram(img_equalizada_array.flatten(), bins=256, range=[0, 256])
        return img_equalizada_array, histograma_original, histograma_equalizado

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*")])
        if not path: return
        try:
            self.original_pil_image = Image.open(path).convert("L")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível ler o arquivo de imagem.\n\nErro: {e}")
            return
        self.display_image(self.original_pil_image, self.label_orig)
        self.label_eq.configure(image=None, text="Imagem Equalizada")
        self._plot_histogram(self.hist_orig_canvas, [])
        self._plot_histogram(self.hist_eq_canvas, [])
        self.update_idletasks()
        img_array = np.array(self.original_pil_image)
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        self._plot_histogram(self.hist_orig_canvas, hist)

    def apply_equalization(self):
        if not self.original_pil_image:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return
        self.configure(cursor="watch")
        self.update()
        img_array = np.array(self.original_pil_image)
        eq_array, hist_orig, hist_eq = self.equalizacao_histograma_manual(img_array)
        img_equalizada = Image.fromarray(eq_array)
        self.display_image(img_equalizada, self.label_eq)
        self._plot_histogram(self.hist_orig_canvas, hist_orig)
        self._plot_histogram(self.hist_eq_canvas, hist_eq)
        self.configure(cursor="")

    def display_image(self, pil_image, ctk_label):
        """Redimensiona e exibe uma imagem da PIL em um CTkLabel."""
        parent_frame = ctk_label.master
        max_width, max_height = parent_frame.winfo_width() - 20, parent_frame.winfo_height() - 20
        if max_width <= 1 or max_height <= 1:
            max_width, max_height = 500, 500
        display_image = pil_image.copy()
        display_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        ctk_img = ctk.CTkImage(light_image=display_image, dark_image=display_image, size=display_image.size)
        
        ctk_label.configure(image=ctk_img, text="")
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Guarda uma referência da imagem no próprio widget para evitar que
        # o coletor de lixo do Python a remova da memória.
        ctk_label.image = ctk_img