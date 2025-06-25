from customtkinter import CTkFrame
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import math

class ImageFrame(CTkFrame):
    def __init__(self, master,**kwargs):
        super().__init__(master,**kwargs)

        self.original_image = None

        # Botão de carregamento
        ctk.CTkButton(self, text="CARREGAR IMAGEM", font=("Segoe UI Black", 35), command=self.load_image).pack(pady=30)

        self.original_label = ctk.CTkScrollableFrame(self, label_text="Original")
        self.original_label.place(relx=0.025,rely=0.2,relwidth=0.45,relheight=0.7)

        self.transformed_label = ctk.CTkScrollableFrame(self, label_text="Transformada")
        self.transformed_label.place(relx=0.525,rely=0.2,relwidth=0.45,relheight=0.7)
        
        self.original_image_label = ctk.CTkLabel(self.original_label, text="")
        self.original_image_label.pack(anchor=ctk.CENTER)

        self.transformed_image_label = ctk.CTkLabel(self.transformed_label, text="")
        self.transformed_image_label.pack(anchor=ctk.CENTER)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.bmp")])
        if not file_path:
            return
        image = Image.open(file_path).convert("L")  # Tons de cinza
        self.original_image = np.array(image)
        self.display_image(self.original_image, self.original_image_label)

    def display_image(self, img_array, label):
        image = Image.fromarray(img_array)
        image = image.resize((round(image.width), round(image.height)))
        image_tk = ImageTk.PhotoImage(image)
        label.configure(image=image_tk)
        label.image = image_tk

    def transform_image(self, matrix, output_size=None):
        if self.original_image is None:
            return
        
        src = self.original_image
        h, w = src.shape

        # Define tamanho de saída
        if output_size is None:
            output_size = (h * 5, w * 5)
        out_h, out_w = output_size
        dst = np.zeros((out_h, out_w), dtype=np.uint8)

        inv_matrix = np.linalg.inv(matrix)  # Usamos inversa para retroprojeção

        print(inv_matrix)
        
        for y_dst in range(out_h):
            for x_dst in range(out_w):
                # Coordenada no destino → homogênea
                vec_dst = np.array([x_dst, y_dst, 1])
                # Aplica inversa para encontrar origem
                x_src, y_src, _ = inv_matrix @ vec_dst
                x_src, y_src = int(round(x_src)), int(round(y_src))
                if 0 <= x_src < w and 0 <= y_src < h:
                    dst[y_dst, x_dst] = src[y_src, x_src]

        self.display_image(dst, self.transformed_image_label)

    # ---------- Matrizes de Transformação ----------

    def apply_scale(self,sx,sy):
        M = np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0,  0, 1]
        ])
        self.transform_image(M)

    def apply_translation(self,tx,ty):
        M = np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ])
        self.transform_image(M)

    def apply_reflectionX(self):
        # Reflexão horizontal em relação ao eixo Y
        M = np.array([
            [-1, 0, self.original_image.shape[1]],  # Inverte x e move para direita
            [0, 1, 0],
            [0, 0, 1]
        ])
        self.transform_image(M)
        
    def apply_reflectionY(self):
        # Reflexão horizontal em relação ao eixo Y
        M = np.array([
            [1, 0, 0],  # Inverte x e move para direita
            [0, -1, self.original_image.shape[1]],
            [0, 0, 1]
        ])
        self.transform_image(M)

    def apply_shear(self,sh_x,sh_y):
        M = np.array([
            [1, sh_x, 0],
            [sh_y, 1,    0],
            [0, 0,    1]
        ])
        self.transform_image(M)

    def apply_rotation(self,angle):
        angle = math.radians(angle)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx, cy = self.original_image.shape[1] // 2, self.original_image.shape[0] // 2

        # Translação para origem → Rotação → Volta
        T1 = np.array([
            [1, 0, -cx],
            [0, 1, -cy],
            [0, 0, 1]
        ])

        R = np.array([
            [cos_a, -sin_a, 0],
            [sin_a,  cos_a, 0],
            [0,      0,     1]
        ])

        T2 = np.array([
            [1, 0, cx],
            [0, 1, cy],
            [0, 0, 1]
        ])

        M = T2 @ R @ T1
        self.transform_image(M)
