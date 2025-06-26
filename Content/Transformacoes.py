__package__ = None

import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np

# --- Classe Principal como um CTkFrame ---
class Transformation(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.original_pil_image = None
        self.processed_pil_image = None

        # --- Configuração do Grid do Frame Principal ---
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- Widgets da Interface ---
        
        # Frame de Controles
        control_frame = customtkinter.CTkFrame(self)
        control_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.btn_open = customtkinter.CTkButton(control_frame, text="Selecionar Imagem", command=self.select_image)
        self.btn_open.grid(row=0, column=0, padx=10, pady=10)
        
        self.lbl_path = customtkinter.CTkLabel(control_frame, text="Nenhuma imagem selecionada", anchor="w")
        self.lbl_path.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="ew")

        # Dicionário e Menu de Operações
        self.operations = {
            "Negativo da Imagem": "negativo_manual", "Transformação Gamma": "gamma_manual",
            "Transformação Logarítmica": "log_manual", "Transformação Sigmoide": "sigmoide_manual",
            "Ajuste de Faixa Dinâmica": "faixa_dinamica_manual",
            "Transformação Linear (Brilho/Contraste)": "linear_manual",
        }
        self.operation_menu = customtkinter.CTkComboBox(control_frame, values=list(self.operations.keys()), state="readonly")
        self.operation_menu.set("Negativo da Imagem")
        self.operation_menu.grid(row=1, column=0, padx=10, pady=10)

        self.btn_apply = customtkinter.CTkButton(control_frame, text="Aplicar Operação", command=self.apply_operation)
        self.btn_apply.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.btn_save = customtkinter.CTkButton(control_frame, text="Salvar Imagem", command=self.save_image, state="disabled")
        self.btn_save.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        ### ALTERADO: Criação de frames roláveis para as imagens ###
        scroll_frame_orig = customtkinter.CTkScrollableFrame(self, label_text="Imagem Original")
        scroll_frame_orig.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        scroll_frame_proc = customtkinter.CTkScrollableFrame(self, label_text="Imagem Processada")
        scroll_frame_proc.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # As labels agora são colocadas dentro dos frames roláveis
        self.original_label = customtkinter.CTkLabel(scroll_frame_orig, text="")
        self.original_label.pack()
        
        self.processed_label = customtkinter.CTkLabel(scroll_frame_proc, text="")
        self.processed_label.pack()

        # Inspetores de Pixels (sem alteração na criação)
        inspector_frame_orig = self._create_inspector_frame("Original")
        inspector_frame_orig.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.inspector_labels_orig = self._create_inspector_grid(inspector_frame_orig)

        inspector_frame_proc = self._create_inspector_frame("Processado")
        inspector_frame_proc.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.inspector_labels_proc = self._create_inspector_grid(inspector_frame_proc)

    # --- Funções do Inspetor ---
    def _create_inspector_frame(self, title):
        frame = customtkinter.CTkFrame(self)
        label = customtkinter.CTkLabel(frame, text=f"Inspetor 9x9 ({title})", font=customtkinter.CTkFont(weight="bold"))
        label.pack(pady=(5,5))
        return frame

    def _create_inspector_grid(self, parent_frame):
        grid_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        grid_frame.pack(pady=(0, 5))
        
        labels_list = []
        for r in range(9):
            row_list = []
            for c in range(9):
                label = customtkinter.CTkLabel(grid_frame, text="-", width=30, height=30, font=("Consolas", 11))
                if r == 4 and c == 4:
                    label.configure(fg_color="#8B0000", font=("Consolas", 11, "bold"))
                label.grid(row=r, column=c, padx=1, pady=1)
                row_list.append(label)
            labels_list.append(row_list)
        return labels_list

    ### ALTERADO: Lógica de atualização do inspetor simplificada ###
    def _update_inspectors(self, event):
        """Atualiza AMBAS as matrizes com base na posição do mouse."""
        # A coordenada do mouse agora é a coordenada do pixel, sem necessidade de tradução
        center_x, center_y = event.x, event.y

        # Preenche a matriz da imagem original
        if self.original_pil_image:
            self._fill_grid(self.inspector_labels_orig, self.original_pil_image, center_x, center_y)
        
        # Preenche a matriz da imagem processada USANDO AS MESMAS COORDENADAS
        if self.processed_pil_image:
            self._fill_grid(self.inspector_labels_proc, self.processed_pil_image, center_x, center_y)

    def _fill_grid(self, labels, pil_image, center_x, center_y):
        img_array = np.array(pil_image.convert("L"))
        img_h, img_w = img_array.shape

        for r in range(9):
            for c in range(9):
                sample_y, sample_x = center_y - 4 + r, center_x - 4 + c
                if 0 <= sample_y < img_h and 0 <= sample_x < img_w:
                    pixel_value = img_array[sample_y, sample_x]
                    labels[r][c].configure(text=str(pixel_value))
                else:
                    labels[r][c].configure(text="-")

    def _clear_inspectors(self, event=None):
        for r in range(9):
            for c in range(9):
                self.inspector_labels_orig[r][c].configure(text="-")
                self.inspector_labels_proc[r][c].configure(text="-")
    
    # --- Funções de Processamento (Inalteradas) ---
    def transformacao_negativo_manual(self, image_array): return 255 - image_array
    def transformacao_gamma_manual(self, image_array, gamma): return np.power(image_array / 255.0, gamma) * 255
    def transformacao_log_manual(self, image_array): return (255 / np.log(1 + np.max(image_array))) * np.log(1 + image_array)
    def transformacao_sigmoide_manual(self, image_array, w, s): return 255*(1/(1+np.exp(-(image_array-w)/(s if s!=0 else 1e-6))))
    def transformacao_faixa_dinamica_manual(self, image_array): f_min,f_max=np.min(image_array),np.max(image_array); return ((image_array-f_min)/(f_max-f_min if f_max!=f_min else 1))*255
    def transformacao_linear_manual(self, image_array, a, b): return a * image_array + b

    # --- Lógica Principal da Aplicação ---
    def get_input_dialog(self, title, text, input_type=float):
        dialog = customtkinter.CTkInputDialog(title=title, text=text)
        input_str = dialog.get_input()
        if input_str is None: return None
        try: return input_type(input_str)
        except (ValueError, TypeError): messagebox.showerror("Erro de Entrada", f"Valor inválido."); return None

    def apply_operation(self):
        if not self.original_pil_image: messagebox.showerror("Erro", "Selecione uma imagem."); return
        operation_key, operation_value = self.operation_menu.get(), self.operations[self.operation_menu.get()]
        self.winfo_toplevel().config(cursor="watch"); self.update_idletasks()
        img_array = np.array(self.original_pil_image.convert("L"), dtype=np.float32)
        processed_array = None
        
        if operation_value=='negativo_manual' or operation_value=='log_manual' or operation_value=='faixa_dinamica_manual':
            processed_array = getattr(self, operation_value)(img_array)
        elif operation_value == 'gamma_manual':
            gamma = self.get_input_dialog("Gamma", "Gamma (ex: 0.5):", float)
            if gamma is not None: processed_array = self.transformacao_gamma_manual(img_array, gamma)
        elif operation_value == 'sigmoide_manual':
            w = self.get_input_dialog("Centro Sigmoide", "Centro (w, ex: 128):", float)
            if w is not None:
                s = self.get_input_dialog("Largura Sigmoide", "Largura (σ, ex: 25):", float)
                if s is not None: processed_array = self.transformacao_sigmoide_manual(img_array, w, s)
        elif operation_value == 'linear_manual':
            a = self.get_input_dialog("Contraste", "Contraste (a, ex: 1.5):", float)
            if a is not None:
                b = self.get_input_dialog("Brilho", "Brilho (b, ex: -20):", int)
                if b is not None: processed_array = self.transformacao_linear_manual(img_array, a, b)

        if processed_array is not None:
            processed_array = np.clip(processed_array, 0, 255)
            self.processed_pil_image = Image.fromarray(processed_array.astype(np.uint8))
            self.display_image(self.processed_pil_image, self.processed_label)
            self.btn_save.configure(state="normal")
        self.winfo_toplevel().config(cursor="")

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.gif *.pgm")])
        if not path: return
        try:
            self.original_pil_image = Image.open(path)
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível carregar a imagem: {e}")
            return
            
        self.lbl_path.configure(text=path)
        self.display_image(self.original_pil_image, self.original_label)
        self.processed_label.configure(image=None)
        self._clear_inspectors()
        self.processed_pil_image = None
        self.btn_save.configure(state="disabled")

    ### ALTERADO: Função de exibição de imagem sem redimensionamento ###
    def display_image(self, pil_image, label_widget):
        # A imagem não é mais redimensionada
        tk_image = customtkinter.CTkImage(
            light_image=pil_image, 
            dark_image=pil_image, 
            size=pil_image.size
        )
        
        label_widget.configure(image=tk_image, text="")
        label_widget.image = tk_image # Mantém a referência
        
        # Vincula os eventos para o inspetor
        label_widget.bind("<Motion>", self._update_inspectors)
        label_widget.bind("<Leave>", self._clear_inspectors)

    def save_image(self):
        if not self.processed_pil_image: messagebox.showerror("Erro", "Não há imagem para salvar."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png"),("JPEG","*.jpg")])
        if not filepath: return
        try: 
            # Garante que a imagem processada seja salva no modo correto
            save_img = self.processed_pil_image.convert("RGB") if self.processed_pil_image.mode == 'RGBA' else self.processed_pil_image
            save_img.save(filepath)
            messagebox.showinfo("Sucesso", f"Imagem salva em:\n{filepath}")
        except Exception as e: 
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {e}")

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    app = customtkinter.CTk()
    app.title("Transformações de Intensidade de Imagem")
    app.geometry("1200x950")

    frame = Transformation(master=app)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    app.mainloop()