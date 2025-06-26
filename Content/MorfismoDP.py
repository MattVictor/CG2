import customtkinter as ctk
from tkinter import filedialog, messagebox, Text
import numpy as np
import imageio
import os
from PIL import Image, ImageTk
import threading

# --------------------------------------------------------------------------
# ALGORITMO DE MORPHING (BEIER-NEELY)
# --------------------------------------------------------------------------

class Linha:
    """Classe auxiliar para representar uma linha de controle."""
    def __init__(self, p1, p2):
        self.P = np.array(p1, dtype=float)
        self.Q = np.array(p2, dtype=float)
        self.vetor_PQ = self.Q - self.P
        self.vetor_perpendicular = np.array([-self.vetor_PQ[1], self.vetor_PQ[0]])
        self.comprimento_quadrado = self.vetor_PQ[0]**2 + self.vetor_PQ[1]**2
        if self.comprimento_quadrado == 0:
            self.comprimento_quadrado = 1e-6 # Evitar divisão por zero

    def obter_coords_relativas(self, X):
        """Calcula as coordenadas (u, v) de um ponto X em relação à linha."""
        vetor_PX = X - self.P
        u = np.dot(vetor_PX, self.vetor_PQ) / self.comprimento_quadrado
        v = np.dot(vetor_PX, self.vetor_perpendicular) / np.sqrt(self.comprimento_quadrado)
        return u, v

    def obter_ponto_absoluto(self, u, v):
        """Calcula o ponto X a partir das coordenadas relativas (u, v)."""
        return self.P + u * self.vetor_PQ + (v * self.vetor_perpendicular) / np.sqrt(self.comprimento_quadrado)


def deformar_imagem(img_origem, pontos_origem, pontos_destino, a=1.0, b=2.0, p=0.5):
    """Deforma uma imagem de origem para se alinhar com a geometria de destino."""
    # A lógica original usa pares de pontos para formar linhas.
    # Garantimos que a lista de pontos tenha um número par de elementos.
    num_linhas = len(pontos_origem) // 2
    linhas_origem = [Linha(pontos_origem[i*2], pontos_origem[i*2+1]) for i in range(num_linhas)]
    linhas_destino = [Linha(pontos_destino[i*2], pontos_destino[i*2+1]) for i in range(num_linhas)]

    altura, largura = img_origem.shape
    img_deformada = np.zeros_like(img_origem)

    for y_dst in range(altura):
        for x_dst in range(largura):
            ponto_X = np.array([x_dst, y_dst])
            deslocamento_total = np.zeros(2, dtype=float)
            peso_total = 0.0

            for i in range(len(linhas_destino)):
                linha_dst = linhas_destino[i]
                linha_src = linhas_origem[i]

                u, v = linha_dst.obter_coords_relativas(ponto_X)
                ponto_X_fonte = linha_src.obter_ponto_absoluto(u, v)
                deslocamento = ponto_X_fonte - ponto_X
                
                dist = 0
                if 0 <= u <= 1:
                    dist = abs(v)
                elif u < 0:
                    dist = np.linalg.norm(ponto_X - linha_dst.P)
                else: # u > 1
                    dist = np.linalg.norm(ponto_X - linha_dst.Q)

                # Evita peso infinito se a distância for zero
                peso = (linha_src.comprimento_quadrado**p / (a + dist))**b
                
                deslocamento_total += deslocamento * peso
                peso_total += peso
            
            if peso_total > 1e-6:
                ponto_final_fonte = ponto_X + deslocamento_total / peso_total
            else:
                ponto_final_fonte = ponto_X

            x_src, y_src = ponto_final_fonte

            if 0 <= x_src < largura - 1 and 0 <= y_src < altura - 1:
                x1, y1 = int(x_src), int(y_src)
                x2, y2 = x1 + 1, y1 + 1
                
                fx = x_src - x1
                fy = y_src - y1

                c1 = img_origem[y1, x1] * (1 - fx) + img_origem[y1, x2] * fx
                c2 = img_origem[y2, x1] * (1 - fx) + img_origem[y2, x2] * fx
                cor = c1 * (1 - fy) + c2 * fy
                img_deformada[y_dst, x_dst] = np.clip(cor, 0, 255)

    return img_deformada.astype(np.uint8)


def morph(img_inicial, img_final, pontos_inicial, pontos_final, t):
    """Calcula um único frame do morphing para um tempo 't'."""
    pontos_intermediarios = (1 - t) * pontos_inicial + t * pontos_final
    img_inicial_deformada = deformar_imagem(img_inicial, pontos_inicial, pontos_intermediarios)
    img_final_deformada = deformar_imagem(img_final, pontos_final, pontos_intermediarios)
    img_morph = ((1 - t) * img_inicial_deformada.astype(float) + t * img_final_deformada.astype(float)).astype(np.uint8)
    return img_morph

# --------------------------------------------------------------------------
# APLICAÇÃO GRÁFICA (CUSTOMTKINTER)
# --------------------------------------------------------------------------

class Morphing(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        # Variáveis de estado
        self.img_initial_pil = None
        self.img_initial_np = None
        self.img_final_pil = None
        self.img_final_np = None
        self.points_initial = []
        self.points_final = []
        
        self.gif_frames = []
        self.gif_photo_images = []
        self.gif_animation_id = None
        self.gif_path = "resultado_morphing.gif"

        # Configuração da grade principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- Coluna da Imagem Inicial ----
        self.frame_initial = self._create_image_frame("Imagem Inicial", 0)
        self.btn_load_initial = ctk.CTkButton(self.frame_initial, text="Carregar Imagem Inicial", command=self.load_initial_image)
        self.btn_load_initial.pack(pady=5, padx=10, fill='x')
        self.lbl_image_initial = self._create_image_label(self.frame_initial)
        self.lbl_coords_initial = self._create_coords_label(self.frame_initial)
        self.entry_initial, self.btn_add_initial, self.txt_points_initial = self._create_point_controls(
            self.frame_initial, self.add_initial_point
        )
        self.lbl_image_initial.bind("<Motion>", lambda event: self.update_coords(event, self.lbl_coords_initial))
        self.lbl_image_initial.bind("<Leave>", lambda event: self.clear_coords(self.lbl_coords_initial))


        # ---- Coluna da Imagem Final ----
        self.frame_final = self._create_image_frame("Imagem Final", 1)
        self.btn_load_final = ctk.CTkButton(self.frame_final, text="Carregar Imagem Final", command=self.load_final_image)
        self.btn_load_final.pack(pady=5, padx=10, fill='x')
        self.lbl_image_final = self._create_image_label(self.frame_final)
        self.lbl_coords_final = self._create_coords_label(self.frame_final)
        self.entry_final, self.btn_add_final, self.txt_points_final = self._create_point_controls(
            self.frame_final, self.add_final_point
        )
        self.lbl_image_final.bind("<Motion>", lambda event: self.update_coords(event, self.lbl_coords_final))
        self.lbl_image_final.bind("<Leave>", lambda event: self.clear_coords(self.lbl_coords_final))

        # ---- Coluna de Controle e Resultado ----
        self.frame_controls = ctk.CTkFrame(self)
        self.frame_controls.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_controls, text="Controles e Resultado", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(self.frame_controls, text="Número de Frames:").pack(pady=(10,0))
        self.entry_num_frames = ctk.CTkEntry(self.frame_controls)
        self.entry_num_frames.insert(0, "60")
        self.entry_num_frames.pack(pady=5, padx=10, fill='x')

        self.btn_start = ctk.CTkButton(self.frame_controls, text="Iniciar Morphing", command=self.start_morphing_thread, height=40)
        self.btn_start.pack(pady=20, padx=10, fill='x')

        self.progress_bar = ctk.CTkProgressBar(self.frame_controls)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5, padx=10, fill='x')

        self.lbl_gif_result = ctk.CTkLabel(self.frame_controls, text="O GIF resultante aparecerá aqui.", height=400)
        self.lbl_gif_result.pack(pady=10, padx=10, fill='both', expand=True)

    # ---- Métodos de criação de widgets ----
    def _create_image_frame(self, title, col):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(pady=10)
        return frame

    def _create_image_label(self, parent_frame):
        label = ctk.CTkLabel(parent_frame, text="Nenhuma imagem carregada.", height=300)
        label.pack(pady=5, padx=10, fill='both', expand=True)
        return label
    
    def _create_coords_label(self, parent_frame):
        label = ctk.CTkLabel(parent_frame, text="Coords: (-, -)")
        label.pack(pady=2)
        return label

    def _create_point_controls(self, parent_frame, add_command):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame.pack(pady=5, padx=10, fill='x')
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)

        entry = ctk.CTkEntry(frame, placeholder_text="x, y")
        entry.grid(row=0, column=0, sticky="ew", padx=(0,5))
        
        btn = ctk.CTkButton(frame, text="Add Ponto", command=add_command)
        btn.grid(row=0, column=1, sticky="ew")

        txt = Text(frame, height=5, width=30, background="#2b2b2b", foreground="white", relief="flat", font=("Consolas", 10))
        txt.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        
        return entry, btn, txt

    # ---- Métodos de evento e lógica ----
    def load_initial_image(self):
        self._load_image(is_initial=True)

    def load_final_image(self):
        self._load_image(is_initial=False)

    def _load_image(self, is_initial):
        path = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=(("Arquivos de Imagem", "*.png *.jpg *.jpeg *.bmp *.pgm"), ("Todos os arquivos", "*.*"))
        )
        if not path:
            return
        
        try:
            # Carrega a imagem para exibição (PIL)
            img_pil = Image.open(path)
            
            # Carrega a imagem para processamento (imageio) e converte para escala de cinza
            img_np_color = imageio.imread(path)
            if len(img_np_color.shape) == 3: # Se for colorida
                # Converte para escala de cinza usando a fórmula de luminância
                img_np = np.dot(img_np_color[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
            else: # Se já for escala de cinza ou PGM
                img_np = img_np_color

            # Redimensiona para exibição se for muito grande, mantendo a proporção
            max_disp_w, max_disp_h = 400, 300
            img_pil.thumbnail((max_disp_w, max_disp_h))

            if is_initial:
                self.img_initial_pil = Image.open(path) # Armazena a original
                self.img_initial_np = img_np
                self.lbl_image_initial.configure(image=ctk.CTkImage(light_image=img_pil, size=img_pil.size), text="")
                self.points_initial.clear()
                self.txt_points_initial.delete('1.0', 'end')
            else:
                self.img_final_pil = Image.open(path) # Armazena a original
                self.img_final_np = img_np
                self.lbl_image_final.configure(image=ctk.CTkImage(light_image=img_pil, size=img_pil.size), text="")
                self.points_final.clear()
                self.txt_points_final.delete('1.0', 'end')
        
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar a imagem.\nErro: {e}")

    def add_initial_point(self):
        self._add_point(self.entry_initial, self.points_initial, self.txt_points_initial, self.img_initial_pil)

    def add_final_point(self):
        self._add_point(self.entry_final, self.points_final, self.txt_points_final, self.img_final_pil)

    def _add_point(self, entry, point_list, text_widget, image_pil):
        if not image_pil:
            messagebox.showwarning("Aviso", "Carregue uma imagem antes de adicionar pontos.")
            return
        
        try:
            coords_str = entry.get().split(',')
            x = int(coords_str[0].strip())
            y = int(coords_str[1].strip())

            if not (0 <= x < image_pil.width and 0 <= y < image_pil.height):
                 messagebox.showwarning("Coordenada Inválida", f"O ponto ({x},{y}) está fora dos limites da imagem ({image_pil.width}x{image_pil.height}).")
                 return

            point_list.append([x, y])
            text_widget.insert('end', f"Ponto {len(point_list)}: ({x}, {y})\n")
            entry.delete(0, 'end')
        except (ValueError, IndexError):
            messagebox.showerror("Erro de Formato", "Por favor, insira as coordenadas no formato 'x, y'.")

    def update_coords(self, event, coord_label):
        coord_label.configure(text=f"Coords: ({event.x}, {event.y})")
        
    def clear_coords(self, coord_label):
        coord_label.configure(text="Coords: (-, -)")

    def start_morphing_thread(self):
        # Validações
        if self.img_initial_np is None or self.img_final_np is None:
            messagebox.showerror("Erro", "Você deve carregar as duas imagens antes de iniciar.")
            return
        if self.img_initial_np.shape != self.img_final_np.shape:
            messagebox.showerror("Erro", "As imagens devem ter exatamente as mesmas dimensões (largura x altura).")
            return
        if len(self.points_initial) != len(self.points_final):
            messagebox.showerror("Erro", "O número de pontos de controle nas duas imagens deve ser igual.")
            return
        if not self.points_initial:
            messagebox.showerror("Erro", "Adicione pelo menos um par de pontos de controle.")
            return
        # O algoritmo requer um número par de pontos para formar linhas.
        if len(self.points_initial) % 2 != 0:
            messagebox.showwarning("Aviso", "O número de pontos de controle deve ser par para formar linhas. O último ponto será ignorado.")

        self.btn_start.configure(state="disabled", text="Processando...")
        self.progress_bar.set(0)
        
        # Inicia o processamento pesado em uma thread separada para não travar a GUI
        thread = threading.Thread(target=self._run_morphing_logic)
        thread.daemon = True
        thread.start()

    def _run_morphing_logic(self):
        """Função executada na thread de background."""
        try:
            num_frames = int(self.entry_num_frames.get())
            altura, largura = self.img_initial_np.shape
            
            # Adiciona os cantos para fixar as bordas
            cantos = np.array([[0, 0], [largura - 1, 0], [0, altura - 1], [largura - 1, altura - 1]])
            pontos_inicial = np.vstack([np.array(self.points_initial), cantos])
            pontos_final = np.vstack([np.array(self.points_final), cantos])

            self.gif_frames = []
            output_dir = "frames_morphing"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for i in range(num_frames):
                t = i / (num_frames - 1)
                
                frame_morph = morph(self.img_initial_np, self.img_final_np, pontos_inicial, pontos_final, t)
                self.gif_frames.append(frame_morph)
                
                progress_value = (i + 1) / num_frames
                self.after(0, lambda v=progress_value: self.progress_bar.set(v)) # Agenda a atualização da GUI

            imageio.mimsave(self.gif_path, self.gif_frames, fps=30)
            
            # Agenda a exibição do GIF na thread principal da GUI
            self.after(0, self.display_gif)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro no Morphing", f"Ocorreu um erro: {e}"))
        finally:
            self.after(0, lambda: self.btn_start.configure(state="normal", text="Iniciar Morphing"))

    def display_gif(self):
        """Carrega e inicia a animação do GIF."""
        if self.gif_animation_id:
            self.after_cancel(self.gif_animation_id)

        try:
            self.gif_photo_images = []
            with Image.open(self.gif_path) as gif:
                for frame in range(gif.n_frames):
                    gif.seek(frame)
                    # Cria uma cópia para garantir que o frame não seja descartado
                    frame_image = gif.copy()
                    self.gif_photo_images.append(ImageTk.PhotoImage(frame_image))
            
            self.lbl_gif_result.configure(text="")
            self._animate_gif(0)
            messagebox.showinfo("Sucesso", f"Morphing concluído! GIF salvo como '{self.gif_path}'")
        except Exception as e:
            messagebox.showerror("Erro ao exibir GIF", f"Não foi possível exibir o resultado: {e}")

    def _animate_gif(self, frame_index):
        if not self.gif_photo_images:
            return
        
        image = self.gif_photo_images[frame_index]
        self.lbl_gif_result.configure(image=image)
        
        next_frame_index = (frame_index + 1) % len(self.gif_photo_images)
        self.gif_animation_id = self.after(33, self._animate_gif, next_frame_index) # Aprox. 30 fps