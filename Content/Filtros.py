from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk # Removido ImageTk, pois usaremos CTkImage
import numpy as np

# Define as máscaras (kernels) para os filtros de convolução
KERNELS = {
    "Filtro da Média": np.array([
        [1/9, 1/9, 1/9],
        [1/9, 1/9, 1/9],
        [1/9, 1/9, 1/9]
    ]),
    "Passa-Altas Básico": np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]),
    "Bordas (Sobel)": {
        "Gx": np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]),
        "Gy": np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    },
    "Bordas (Prewitt)": {
        "Gx": np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]),
        "Gy": np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
    },
    "Bordas (Roberts)": {
         "Gx": np.array([[1, 0], [0, -1]]),
         "Gy": np.array([[0, 1], [-1, 0]])
    },
    "Bordas (Roberts Cruzado)": {
        "Gx": np.array([[1, 0], [0, -1]]),
        "Gy": np.array([[0, 1], [-1, 0]])
    },
    "Realce (High-Boost)": lambda k: np.array([
        [-1, -1, -1],
        [-1, 8 + k, -1],
        [-1, -1, -1]
    ])
}

class Filter(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # --- Variáveis de estado ---
        self.original_pil_image = None
        self.original_np_image = None
        self.transformed_np_image = None
        self.image_display_size = (512, 512)
        self.current_filter = "Negativo"

        # --- Configuração do Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame de Controles (Esquerda) ---
        self.controls_frame = ctk.CTkFrame(self, width=350)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_frame.grid_propagate(False)

        # --- Frame de Imagens (Direita) ---
        self.images_frame = ctk.CTkFrame(self)
        self.images_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.setup_controls()
        self.setup_image_display()
        self.setup_pixel_inspector()
        self.setup_mask_display()

        self.apply_button.configure(state="disabled")
        self.filter_menu.configure(state="disabled")

    def setup_controls(self):
        """Configura os widgets no painel de controle."""
        self.controls_frame.grid_rowconfigure(8, weight=1)
        
        load_button = ctk.CTkButton(self.controls_frame, text="Carregar Imagem", command=self.load_image)
        load_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        filter_label = ctk.CTkLabel(self.controls_frame, text="Selecione o Filtro:")
        filter_label.grid(row=1, column=0, padx=10, pady=(10,0), sticky="w", columnspan=2)
        
        filter_options = [
            "Negativo", "Gamma", "Logarítmica", "Sigmoide", "Ajuste de Faixa Dinâmica", "Linear",
            "Filtro da Média", "Filtro da Mediana", "Passa-Altas Básico",
            "Bordas (Sobel)", "Bordas (Prewitt)", "Bordas (Roberts)", "Bordas (Roberts Cruzado)", "Realce (High-Boost)"
        ]
        self.filter_menu = ctk.CTkOptionMenu(self.controls_frame, values=filter_options, command=self.on_filter_change)
        self.filter_menu.grid(row=2, column=0, padx=0, pady=0, sticky="ew", columnspan=2)

        self.params_frame = ctk.CTkFrame(self.controls_frame)
        self.params_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.apply_button = ctk.CTkButton(self.controls_frame, text="Aplicar Filtro", command=self.apply_filter)
        self.apply_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

    def setup_image_display(self):
        """Configura os labels para exibir as imagens."""
        ctk.CTkLabel(self.images_frame, text="Imagem Original", font=ctk.CTkFont(weight="bold")).pack()
        self.original_image_label = ctk.CTkLabel(self.images_frame, text="")
        self.original_image_label.pack()

        ctk.CTkLabel(self.images_frame, text="Imagem Transformada", font=ctk.CTkFont(weight="bold")).pack()
        self.transformed_image_label = ctk.CTkLabel(self.images_frame, text="")
        self.transformed_image_label.pack()

        self.original_image_label.bind("<Motion>", self.update_pixel_info)
        self.transformed_image_label.bind("<Motion>", self.update_pixel_info)
        self.original_image_label.bind("<Leave>", self.clear_inspectors)
        self.transformed_image_label.bind("<Leave>", self.clear_inspectors)

    def setup_pixel_inspector(self):
        """Configura as grades para exibir os valores dos pixels."""
        inspector_frame = ctk.CTkFrame(self.controls_frame)
        inspector_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        inspector_frame.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(inspector_frame, text="Original 5x5", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
        self.original_inspector_grid = self._create_inspector_grid(inspector_frame, 1, 0)

        ctk.CTkLabel(inspector_frame, text="Transformada 5x5", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
        self.transformed_inspector_grid = self._create_inspector_grid(inspector_frame, 1, 1)

    def _create_inspector_grid(self, parent, start_row, start_col):
        """Função auxiliar para criar uma grade de labels 5x5 para o inspetor."""
        grid_labels = []
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=start_row, column=start_col, padx=5, pady=5)
        for r in range(5):
            row_list = []
            for c in range(5):
                label = ctk.CTkLabel(frame, text="-", width=35, height=25, font=("Courier", 15))
                label.grid(row=r, column=c, padx=1, pady=1)
                row_list.append(label)
            grid_labels.append(row_list)
        return grid_labels

    def setup_mask_display(self):
        """Configura a grade para exibir a máscara do filtro."""
        self.mask_frame = ctk.CTkFrame(self.controls_frame)
        self.mask_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.mask_label = ctk.CTkLabel(self.mask_frame, text="Máscara do Filtro", font=ctk.CTkFont(weight="bold"))
        self.mask_label.pack()

        self.mask_grid_frame = ctk.CTkFrame(self.mask_frame, fg_color="transparent")
        self.mask_grid_frame.pack(pady=5)

    def load_image(self):
        """Abre uma caixa de diálogo para carregar uma imagem."""
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.pgm")])
        if not file_path:
            return

        self.original_pil_image = Image.open(file_path).convert("L")
        self.original_np_image = np.array(self.original_pil_image).astype(np.float32)

        self.transformed_np_image = None
        self.transformed_image_label.configure(image=None, text="Imagem Transformada")
        self.clear_inspectors(None)

        self.display_image(self.original_pil_image, self.original_image_label)

        self.apply_button.configure(state="normal")
        self.filter_menu.configure(state="normal")
        self.on_filter_change(self.filter_menu.get())

    def display_image(self, pil_image, label):
        """Exibe uma imagem PIL em um CTkLabel usando CTkImage."""
        # CORREÇÃO 2: Usando ctk.CTkImage
        w, h = pil_image.size
        ratio = min(self.image_display_size[0] / w, self.image_display_size[1] / h)
        new_size = (int(w), int(h))
        
        # O CTkImage espera a imagem PIL original, ele mesmo lida com o redimensionamento.
        # No entanto, para manter a consistência do display, vamos redimensionar antes.
        resized_img = pil_image# .resize(new_size, Image.Resampling.LANCZOS)
        
        ctk_image = ImageTk.PhotoImage(resized_img)
        
        label.configure(image=ctk_image, text="")
        label.image = ctk_image

    def apply_filter(self):
        """Aplica o filtro selecionado na imagem original."""
        if self.original_np_image is None:
            return

        filter_name = self.filter_menu.get()
        source_image = self.original_np_image.copy()
        
        # Lógica dos filtros... (sem alterações aqui)
        if filter_name == "Negativo":
            self.transformed_np_image = 255 - source_image
        elif filter_name == "Gamma":
            gamma = self.gamma_slider.get()
            c = 255 / (255 ** gamma)
            self.transformed_np_image = c * (source_image ** gamma)
        elif filter_name == "Logarítmica":
            # Adiciona um pequeno epsilon para evitar log(0) se a imagem tiver pixels pretos
            c = 255 / np.log(1 + np.max(source_image))
            self.transformed_np_image = c * np.log(1 + source_image)
        elif filter_name == "Sigmoide":
            a = self.sigmoid_a_slider.get()
            b = self.sigmoid_b_slider.get()
            norm_img = source_image / 255.0
            self.transformed_np_image = 255 * (1 / (1 + np.exp(-a * (norm_img - b))))
        elif filter_name == "Ajuste de Faixa Dinâmica":
            min_val, max_val = np.min(source_image), np.max(source_image)
            self.transformed_np_image = 255 * (source_image - min_val) / (max_val - min_val)
        elif filter_name == "Linear":
             a, b = 0, 255
             fa, fb = self.linear_fa_slider.get(), self.linear_fb_slider.get()
             lut = np.arange(256, dtype=np.float32)
             mask = (lut >= a) & (lut <= b)
             lut[mask] = fa + (lut[mask] - a) * (fb - fa) / (b - a)
             self.transformed_np_image = lut[source_image.astype(np.uint8)]
        elif filter_name in ["Filtro da Média", "Passa-Altas Básico"]:
            kernel = KERNELS[filter_name]
            self.transformed_np_image = self._manual_convolve(source_image, kernel)
        elif filter_name == "Filtro da Mediana":
            self.transformed_np_image = self._manual_median_filter(source_image, 3)
        elif filter_name in ["Bordas (Sobel)", "Bordas (Prewitt)"]:
            kernels = KERNELS[filter_name]
            gx_img = self._manual_convolve(source_image, kernels["Gx"])
            gy_img = self._manual_convolve(source_image, kernels["Gy"])
            self.transformed_np_image = np.abs(gx_img) + np.abs(gy_img)
        elif filter_name in ["Bordas (Roberts)", "Bordas (Roberts Cruzado)"]:
            kernels = KERNELS["Bordas (Roberts)"]
            gx_img = self._manual_convolve(source_image, kernels["Gx"])
            gy_img = self._manual_convolve(source_image, kernels["Gy"])
            self.transformed_np_image = np.abs(gx_img) + np.abs(gy_img)
        elif filter_name == "Realce (High-Boost)":
            k = self.highboost_k_slider.get()
            kernel = KERNELS[filter_name](k)
            self.transformed_np_image = self._manual_convolve(source_image, kernel)

        self.transformed_np_image = np.clip(self.transformed_np_image, 0, 255)
        transformed_pil = Image.fromarray(self.transformed_np_image.astype(np.uint8))
        self.display_image(transformed_pil, self.transformed_image_label)
        self.update_pixel_info(None)

    def _manual_convolve(self, image, kernel):
        """Aplica convolução manualmente, pixel a pixel."""
        k_h, k_w = kernel.shape
        h, w = image.shape
        
        pad_h, pad_w = k_h // 2, k_w // 2
        
        # CORREÇÃO 1: Substituir 'replicate' por 'edge'
        padded_image = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')
        
        output_image = np.zeros_like(image)
        
        for y in range(h):
            for x in range(w):
                neighborhood = padded_image[y : y + k_h, x : x + k_w]
                pixel_value = np.sum(neighborhood * kernel)
                output_image[y, x] = pixel_value
                
        return output_image
        
    def _manual_median_filter(self, image, size):
        """Aplica filtro da mediana manualmente."""
        h, w = image.shape
        pad = size // 2
        
        # CORREÇÃO 1: Substituir 'replicate' por 'edge'
        padded_image = np.pad(image, pad, mode='edge')
        output_image = np.zeros_like(image)

        for y in range(h):
            for x in range(w):
                neighborhood = padded_image[y : y + size, x : x + size]
                median_value = np.median(neighborhood)
                output_image[y, x] = median_value
                
        return output_image

    def on_filter_change(self, filter_name):
        """Chamado quando o usuário seleciona um novo filtro no menu."""
        # O resto desta função permanece o mesmo...
        self.current_filter = filter_name
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        if filter_name == "Gamma":
            ctk.CTkLabel(self.params_frame, text="Gamma (γ):").pack(pady=(5,0))
            self.gamma_slider = ctk.CTkSlider(self.params_frame, from_=0.1, to=5.0, number_of_steps=49,command=self.atualizar_valor_label)
            self.gamma_slider.set(1.0)
            self.gamma_slider.pack(pady=5, padx=10, fill="x")
        elif filter_name == "Sigmoide":
            ctk.CTkLabel(self.params_frame, text="Ganho (a):").pack(pady=(5,0))
            self.sigmoid_a_slider = ctk.CTkSlider(self.params_frame, from_=0.1, to=10.0, number_of_steps=99,command=self.atualizar_valor_label)
            self.sigmoid_a_slider.set(5.0)
            self.sigmoid_a_slider.pack(pady=5, padx=10, fill="x")
            ctk.CTkLabel(self.params_frame, text="Centro (b):").pack(pady=(5,0))
            self.sigmoid_b_slider = ctk.CTkSlider(self.params_frame, from_=0.0, to=1.0, number_of_steps=100,command=self.atualizar_valor_label)
            self.sigmoid_b_slider.set(0.5)
            self.sigmoid_b_slider.pack(pady=5, padx=10, fill="x")
        elif filter_name == "Linear":
            ctk.CTkLabel(self.params_frame, text="Saída em 0 (f(a)):").pack(pady=(5,0))
            self.linear_fa_slider = ctk.CTkSlider(self.params_frame, from_=0, to=255, number_of_steps=255,command=self.atualizar_valor_label)
            self.linear_fa_slider.set(50)
            self.linear_fa_slider.pack(pady=5, padx=10, fill="x")
            ctk.CTkLabel(self.params_frame, text="Saída em 255 (f(b)):").pack(pady=(5,0))
            self.linear_fb_slider = ctk.CTkSlider(self.params_frame, from_=0, to=255, number_of_steps=255,command=self.atualizar_valor_label)
            self.linear_fb_slider.set(200)
            self.linear_fb_slider.pack(pady=5, padx=10, fill="x")
        elif filter_name == "Realce (High-Boost)":
            ctk.CTkLabel(self.params_frame, text="Fator de Realce (k):").pack(pady=(5,0))
            self.highboost_k_slider = ctk.CTkSlider(self.params_frame, from_=0.1, to=5.0, number_of_steps=49,command=self.atualizar_valor_label)
            self.highboost_k_slider.set(1.0)
            self.highboost_k_slider.pack(pady=5, padx=10, fill="x")
        
        self.valor_label = ctk.CTkLabel(self.params_frame, text="Valor: 0.0", font=("", 16))
        self.valor_label.pack(anchor=ctk.S)
        
        self.update_mask_display()

    def atualizar_valor_label(self, valor):
        # Formata o valor para ter duas casas decimais e atualiza o texto do label
        texto_formatado = f"Valor: {valor:.2f}"
        self.valor_label.configure(text=texto_formatado)

    def update_mask_display(self):
        """Atualiza a grade que exibe a máscara do filtro."""
        for widget in self.mask_grid_frame.winfo_children():
            widget.destroy()
        
        kernel, filter_name = None, self.current_filter

        if filter_name in ["Filtro da Média", "Passa-Altas Básico"]:
            kernel = KERNELS[filter_name]
        elif "Bordas" in filter_name:
            # Pega o nome base do filtro (ex: "Sobel")
            base_name = filter_name.split(' ')[0]
            if base_name in KERNELS:
                kernel = KERNELS[base_name]["Gx"]
                self.mask_label.configure(text=f"Máscara ({filter_name} - Gx)")
        elif filter_name == "Realce (High-Boost)":
            k = self.highboost_k_slider.get() if hasattr(self, 'highboost_k_slider') else 1.0
            kernel = KERNELS[filter_name](k)
        
        if kernel is None:
            self.mask_label.configure(text="Máscara (não aplicável)")
            return

        self.mask_label.configure(text=f"Máscara ({filter_name})")
        h, w = kernel.shape
        for r in range(h):
            for c in range(w):
                val = kernel[r, c]
                text = f"{val:.2f}" if isinstance(val, float) else str(val)
                label = ctk.CTkLabel(self.mask_grid_frame, text=text, width=40, font=("Courier", 10))
                label.grid(row=r, column=c, padx=2, pady=2)

    def update_pixel_info(self, event):
        """Atualiza os inspetores de pixel 5x5 com base na posição do cursor."""
        if self.original_np_image is None or event is None: return
        
        # widget = event.widget
        
        if self.original_image_label.image is None: return
        
        img_w, img_h = self.original_image_label.image.width(),self.original_image_label.image.height()
        orig_h, orig_w = self.original_np_image.shape
        
        if img_w == 0 or img_h == 0: return
        
        scale_x, scale_y = orig_w / img_w, orig_h / img_h
        img_x, img_y = int(event.x ), int(event.y)

        self._update_grid(self.original_inspector_grid, self.original_np_image, img_y, img_x)
        if self.transformed_np_image is not None:
            self._update_grid(self.transformed_inspector_grid, self.transformed_np_image, img_y, img_x)
        else:
            self._clear_grid(self.transformed_inspector_grid)

    def _update_grid(self, grid_labels, image_data, center_y, center_x):
        h, w = image_data.shape
        
        for r_offset in range(-2, 3):
            for c_offset in range(-2, 3):
                y, x = center_y + r_offset, center_x + c_offset
                label = grid_labels[r_offset + 2][c_offset + 2]
                if 0 <= y < h and 0 <= x < w:
                    label.configure(text=str(int(image_data[y, x])))
                else:
                    label.configure(text="-")

    def clear_inspectors(self, event):
        self._clear_grid(self.original_inspector_grid)
        self._clear_grid(self.transformed_inspector_grid)

    def _clear_grid(self, grid_labels):
        for row in grid_labels:
            for label in row:
                label.configure(text="-")