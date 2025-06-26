from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import numpy as np

# --- Importações do Matplotlib ---
import matplotlib
matplotlib.use('TkAgg') # Define o backend do matplotlib para o tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Configurações Globais do Tema ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class Equalize(ctk.CTkFrame):
    """
    Um frame completo que encapsula toda a funcionalidade de visualização
    e equalização de histograma de uma imagem, usando Matplotlib para os gráficos.
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
        self.btn_open.pack(side="left", padx=250)
        self.btn_apply = ctk.CTkButton(control_frame, text="Equalizar Histograma", command=self.apply_equalization, height=35, state="disabled")
        self.btn_apply.pack(side="right", padx=250)

        # --- Áreas de Exibição 2x2 ---
        orig_img_frame = ctk.CTkFrame(display_frame)
        orig_img_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.label_orig = ctk.CTkLabel(orig_img_frame, text="Imagem Original")
        self.label_orig.pack(fill="both", expand=True, padx=5, pady=5)

        eq_img_frame = ctk.CTkFrame(display_frame)
        eq_img_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.label_eq = ctk.CTkLabel(eq_img_frame, text="Imagem Equalizada")
        self.label_eq.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Histograma Original (com Matplotlib) ---
        hist_orig_frame = ctk.CTkFrame(display_frame)
        hist_orig_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(hist_orig_frame, text="Histograma Original", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        
        self.fig_orig = Figure(dpi=100)
        self.ax_orig = self.fig_orig.add_subplot(111)
        self.canvas_orig = FigureCanvasTkAgg(self.fig_orig, master=hist_orig_frame)
        self.canvas_orig_widget = self.canvas_orig.get_tk_widget()
        self.canvas_orig_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Histograma Equalizado (com Matplotlib) ---
        hist_eq_frame = ctk.CTkFrame(display_frame)
        hist_eq_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(hist_eq_frame, text="Histograma Equalizado", font=ctk.CTkFont(weight="bold")).pack(pady=(5,0))
        
        self.fig_eq = Figure(dpi=100)
        self.ax_eq = self.fig_eq.add_subplot(111)
        self.canvas_eq = FigureCanvasTkAgg(self.fig_eq, master=hist_eq_frame)
        self.canvas_eq_widget = self.canvas_eq.get_tk_widget()
        self.canvas_eq_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Inicializa o estilo dos gráficos
        self._style_matplotlib_plot(self.fig_orig, self.ax_orig, "Histograma Original")
        self._style_matplotlib_plot(self.fig_eq, self.ax_eq, "Histograma Equalizado")
        self.canvas_orig.draw()
        self.canvas_eq.draw()


    def _style_matplotlib_plot(self, fig, ax, title):
        """Aplica um estilo escuro a um gráfico do Matplotlib."""
        fig.patch.set_facecolor('#2b2b2b')  # Cor de fundo da figura
        ax.set_facecolor('#242424')       # Cor de fundo da área de plotagem
        
        ax.set_title(title, color='white', fontsize=12)
        ax.set_xlabel("Nível de Cinza", color='white', fontsize=10)
        ax.set_ylabel("Frequência", color='white', fontsize=10)
        
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        for spine in ax.spines.values():
            spine.set_edgecolor('white')

    def _plot_histogram(self, fig, ax, canvas, histogram_data, title):
        """Plota os dados do histograma em um canvas do Matplotlib."""
        ax.clear() # Limpa o gráfico anterior

        if histogram_data is not None and len(histogram_data) > 0:
            ax.bar(range(len(histogram_data)), histogram_data, color="#a0a0a0", width=1.0)
            ax.set_xlim([0, 255]) # Garante que o eixo X vá de 0 a 255
        
        self._style_matplotlib_plot(fig, ax, title) # Reaplica o estilo
        canvas.draw() # Redesenha o canvas para mostrar as atualizações

    def equalizacao_histograma_manual(self, image_array):
        """Calcula a equalização do histograma e retorna os resultados."""
        histograma_original, _ = np.histogram(image_array.flatten(), bins=256, range=[0, 256])
        cdf = histograma_original.cumsum()
        cdf_masked = np.ma.masked_equal(cdf, 0)
        
        # Evita divisão por zero se a imagem for de uma única cor
        if (cdf_masked.max() - cdf_masked.min()) == 0:
            cdf_final = np.ma.filled(cdf_masked, 0).astype('uint8')
        else:
            cdf_masked = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
            cdf_final = np.ma.filled(cdf_masked, 0).astype('uint8')
            
        img_equalizada_array = cdf_final[image_array.astype('uint8')]
        histograma_equalizado, _ = np.histogram(img_equalizada_array.flatten(), bins=256, range=[0, 256])
        
        return img_equalizada_array, histograma_original, histograma_equalizado

    def select_image(self):
        """Abre o seletor de arquivos e carrega a imagem."""
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.png *.jpg *.jpeg *.bmp"), ("Todos os arquivos", "*.*")])
        if not path: return
        
        try:
            self.original_pil_image = Image.open(path).convert("L")
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível ler o arquivo de imagem.\n\nErro: {e}")
            return
            
        self.display_image(self.original_pil_image, self.label_orig)
        self.label_eq.configure(image=None, text="Imagem Equalizada")
        
        img_array = np.array(self.original_pil_image)
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=[0, 256])
        
        self._plot_histogram(self.fig_orig, self.ax_orig, self.canvas_orig, hist, "Histograma Original")
        self._plot_histogram(self.fig_eq, self.ax_eq, self.canvas_eq, [], "Histograma Equalizado") # Limpa o gráfico
        
        self.btn_apply.configure(state="normal") # Habilita o botão de aplicar

    def apply_equalization(self):
        """Aplica o algoritmo de equalização na imagem carregada."""
        if not self.original_pil_image:
            messagebox.showerror("Erro", "Por favor, selecione uma imagem primeiro.")
            return
            
        self.configure(cursor="watch")
        self.update_idletasks() # Garante que o cursor mude imediatamente
        
        img_array = np.array(self.original_pil_image)
        eq_array, hist_orig, hist_eq = self.equalizacao_histograma_manual(img_array)
        img_equalizada = Image.fromarray(eq_array)
        
        self.display_image(img_equalizada, self.label_eq)
        self._plot_histogram(self.fig_orig, self.ax_orig, self.canvas_orig, hist_orig, "Histograma Original")
        self._plot_histogram(self.fig_eq, self.ax_eq, self.canvas_eq, hist_eq, "Histograma Equalizado")
        
        self.configure(cursor="")

    def display_image(self, pil_image, ctk_label):
        """Redimensiona e exibe uma imagem da PIL em um CTkLabel."""
        parent_frame = ctk_label.master
        # Adiciona um pequeno delay para garantir que o frame tenha sido desenhado e tenha um tamanho
        parent_frame.update_idletasks() 
        max_width, max_height = parent_frame.winfo_width() - 20, parent_frame.winfo_height() - 20
        
        if max_width <= 1 or max_height <= 1:
            max_width, max_height = 500, 500 # Valor de fallback
            
        display_image = pil_image.copy()
        display_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        ctk_img = ctk.CTkImage(light_image=display_image, dark_image=display_image, size=display_image.size)
        
        ctk_label.configure(image=ctk_img, text="")
        # Guarda uma referência da imagem para evitar que seja removida pelo garbage collector
        ctk_label.image = ctk_img