__package__

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

class MorphologyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Morfologia Matemática")
        self.root.geometry("1100x700")

        # Variáveis de estado
        self.morf_img_array = None
        self.morf_img_original_pil = None

        # --- Chama o método que constrói a interface ---
        self.criar_interface_morfologia()

    def criar_interface_morfologia(self):
        """Cria todos os widgets para a interface de morfologia."""
        # Layout
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        display_frame = tk.Frame(self.root, padx=10, pady=10)
        display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Controles
        tk.Button(control_frame, text="Carregar Imagem", command=self.morf_carregar_imagem).pack(side=tk.LEFT, padx=10)
        
        # Seletor de Modo (Binário / Nível de Cinza)
        self.morf_mode_var = tk.StringVar(value="cinza")
        tk.Label(control_frame, text="Modo:").pack(side=tk.LEFT, padx=(20, 5))
        tk.Radiobutton(control_frame, text="Nível de Cinza", variable=self.morf_mode_var, value="cinza", command=self.morf_processar_e_exibir_original).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="Binário", variable=self.morf_mode_var, value="binario", command=self.morf_processar_e_exibir_original).pack(side=tk.LEFT)

        # Seletor de Operador Morfológico
        operations = ["Dilatação", "Erosão", "Abertura", "Fechamento", "Gradiente Morfológico", "Extração de Fronteira"]
        self.morf_op_var = tk.StringVar(value="Dilatação")
        op_menu = ttk.Combobox(control_frame, textvariable=self.morf_op_var, values=operations, state="readonly", width=25)
        op_menu.pack(side=tk.LEFT, padx=10)

        # Seletor de Elemento Estruturante
        elementos_estruturantes = ["Quadrado 3x3", "Cruz 3x3", "Disco 5x5"]
        self.morf_ee_var = tk.StringVar(value="Quadrado 3x3")
        ee_menu = ttk.Combobox(control_frame, textvariable=self.morf_ee_var, values=elementos_estruturantes, state="readonly", width=15)
        ee_menu.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Aplicar", command=self.morf_aplicar_operacao).pack(side=tk.LEFT, padx=10)

        # Displays de Imagem
        self.morf_label_orig = tk.Label(display_frame, text="Imagem Original", relief="solid", bd=1); self.morf_label_orig.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.morf_label_proc = tk.Label(display_frame, text="Imagem Processada", relief="solid", bd=1); self.morf_label_proc.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def morf_carregar_imagem(self):
        """Carrega uma imagem, processa de acordo com o modo e exibe."""
        path = filedialog.askopenfilename(filetypes=[("Imagens", "*.pgm *.jpg *.png"), ("Todos os arquivos", "*.*")])
        if not path: return
        self.morf_img_original_pil = Image.open(path).convert("L")
        self.morf_processar_e_exibir_original()

    def morf_processar_e_exibir_original(self):
        """Converte a imagem para binária ou cinza e a exibe no painel original."""
        if not self.morf_img_original_pil: return
        
        if self.morf_mode_var.get() == "binario":
            # Binariza a imagem usando um limiar (threshold) de 128
            img_array_temp = np.array(self.morf_img_original_pil)
            self.morf_img_array = ((img_array_temp > 127) * 255).astype('uint8')
        else: # "cinza"
            self.morf_img_array = np.array(self.morf_img_original_pil)
        
        self._exibir_imagem(Image.fromarray(self.morf_img_array), self.morf_label_orig)
        self.morf_label_proc.config(image='', text="Imagem Processada"); self.morf_label_proc.image = None

    def morf_aplicar_operacao(self):
        """Verifica os inputs e chama a função de processamento morfológico."""
        if self.morf_img_array is None:
            messagebox.showerror("Erro", "Carregue uma imagem primeiro.")
            return

        self.root.config(cursor="watch"); self.root.update()
        
        # Garante que a imagem original esteja no formato correto antes de aplicar
        self.morf_processar_e_exibir_original()

        op = self.morf_op_var.get()
        ee = self._get_elemento_estruturante(self.morf_ee_var.get())
        is_binary = (self.morf_mode_var.get() == "binario")
        
        resultado_array = None
        try:
            if op == "Dilatação": resultado_array = self._dilatacao_manual(self.morf_img_array, ee, is_binary)
            elif op == "Erosão": resultado_array = self._erosao_manual(self.morf_img_array, ee, is_binary)
            elif op == "Abertura":
                erodido = self._erosao_manual(self.morf_img_array, ee, is_binary)
                resultado_array = self._dilatacao_manual(erodido, ee, is_binary)
            elif op == "Fechamento":
                dilatado = self._dilatacao_manual(self.morf_img_array, ee, is_binary)
                resultado_array = self._erosao_manual(dilatado, ee, is_binary)
            elif op == "Gradiente Morfológico":
                dilatado = self._dilatacao_manual(self.morf_img_array, ee, is_binary).astype(np.float32)
                erodido = self._erosao_manual(self.morf_img_array, ee, is_binary).astype(np.float32)
                resultado_array = dilatado - erodido
            elif op == "Extração de Fronteira":
                erodido = self._erosao_manual(self.morf_img_array, ee, is_binary).astype(np.float32)
                resultado_array = self.morf_img_array.astype(np.float32) - erodido
            
            if resultado_array is not None:
                resultado_final = np.clip(resultado_array, 0, 255).astype(np.uint8)
                self._exibir_imagem(Image.fromarray(resultado_final), self.morf_label_proc)
        finally:
            self.root.config(cursor="")

    #----------------------------------------------------------------#
    # MÉTODOS AUXILIARES
    #----------------------------------------------------------------#
    def _exibir_imagem(self, pil_image, label, max_size=500):
        """Redimensiona e exibe uma imagem da PIL em um Label do Tkinter."""
        if pil_image is None: return
        img = pil_image.copy()
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image=img)
        label.config(image=photo); label.image = photo
    
    def _get_elemento_estruturante(self, nome_ee):
        """Retorna a matriz NumPy para um dado Elemento Estruturante."""
        if nome_ee == "Quadrado 3x3":
            return np.ones((3, 3), dtype=np.uint8)
        elif nome_ee == "Cruz 3x3":
            return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
        elif nome_ee == "Disco 5x5":
            return np.array([[0,0,1,0,0],[0,1,1,1,0],[1,1,1,1,1],[0,1,1,1,0],[0,0,1,0,0]], dtype=np.uint8)
        return np.ones((3, 3), dtype=np.uint8) # Padrão

    def _dilatacao_manual(self, image_array, ee, is_binary):
        """Aplica a dilatação manual, para binário ou nível de cinza."""
        # Cria uma cópia da imagem de entrada para ser a saída
        output_array = np.copy(image_array)
        # Cria uma imagem de preenchimento para tratar as bordas
        img_pad = np.pad(image_array, pad_width=1, mode='edge')

        for y in range(image_array.shape[0]):
            for x in range(image_array.shape[1]):
                # Extrai a vizinhança da imagem com preenchimento
                vizinhanca = img_pad[y:y+3, x:x+3]
                if is_binary:
                    # Se qualquer pixel da vizinhança sob o EE for branco, o resultado é branco
                    output_array[y, x] = 255 if np.any(vizinhanca[ee == 1] == 255) else 0
                else:
                    # O resultado é o valor máximo da vizinhança sob o EE
                    output_array[y, x] = np.max(vizinhanca[ee == 1])
        return output_array

    def _erosao_manual(self, image_array, ee, is_binary):
        """Aplica a erosão manual, para binário ou nível de cinza."""
        output_array = np.copy(image_array)
        img_pad = np.pad(image_array, pad_width=1, mode='edge')

        for y in range(image_array.shape[0]):
            for x in range(image_array.shape[1]):
                vizinhanca = img_pad[y:y+3, x:x+3]
                if is_binary:
                    # Se todos os pixels sob o EE forem brancos, o resultado é branco
                    output_array[y, x] = 255 if np.all(vizinhanca[ee == 1] == 255) else 0
                else:
                    # O resultado é o valor mínimo da vizinhança sob o EE
                    output_array[y, x] = np.min(vizinhanca[ee == 1])
        return output_array

if __name__ == "__main__":
    root = tk.Tk()
    app = MorphologyApp(root)
    root.mainloop()