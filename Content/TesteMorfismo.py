import numpy as np
import imageio
import os

# --------------------------------------------------------------------------
# PARÂMETROS DE CONFIGURAÇÃO (MODIFIQUE AQUI)
# --------------------------------------------------------------------------

# 1. Nomes dos arquivos de imagem (devem ter as mesmas dimensões)
ARQUIVO_IMAGEM_INICIAL = './Imagens/crianca.pgm'  # Substitua pela sua imagem de infância
ARQUIVO_IMAGEM_FINAL = './Imagens/adulto.pgm'    # Substitua pela sua imagem atual

# 2. Número de frames para a animação do morphing
NUM_FRAMES = 60 # Um valor como 60 gera uma animação de ~2 segundos a 30fps

# 3. Pontos de controle correspondentes
#    Defina os pontos (x, y) para as características principais.
#    A ordem DEVE ser a mesma em ambas as listas.
#    Exemplo: O primeiro ponto em 'inicial' corresponde ao primeiro em 'final'.
#    Os cantos da imagem (0,0), (largura-1, 0), etc., são adicionados
#    automaticamente para garantir que as bordas permaneçam fixas.
#
#    ===> SUBSTITUA ESTES PONTOS PELOS SEUS <===
lista_pontos_inicial = np.array([
    [256,87], #Ponta Esquerda da Cabeça
    [99,99], #Ponta Direita da Cabeça
    [212, 189], # Ex: olho esquerdo
    [150, 190], # Ex: olho direito
    [182, 233], # Ex: ponta do nariz
    [214, 251], # Ex: canto esquerdo da boca
    [147, 250], # Ex: canto direito da boca
    [180, 304], # Ex: queixo
])

lista_pontos_final = np.array([
    [248,75], #Ponta Esquerda da Cabeça
    [93,82], ##Ponta Direita da Cabeça
    [211, 139],  # Ex: olho esquerdo (nova posição)
    [130, 137], # Ex: olho direito (nova posição)
    [172, 181], # Ex: ponta do nariz (nova posição)
    [205, 221], # Ex: canto esquerdo da boca (nova posição)
    [133, 224], # Ex: canto direito da boca (nova posição)
    [168, 296], # Ex: queixo (nova posição)
])
# --------------------------------------------------------------------------

class Linha:
    """Classe auxiliar para representar uma linha de controle."""
    def __init__(self, p1, p2):
        self.P = np.array(p1, dtype=float)
        self.Q = np.array(p2, dtype=float)
        self.vetor_PQ = self.Q - self.P
        self.vetor_perpendicular = np.array([-self.vetor_PQ[1], self.vetor_PQ[0]])
        self.comprimento_quadrado = self.vetor_PQ[0]**2 + self.vetor_PQ[1]**2

    def obter_coords_relativas(self, X):
        """Calcula as coordenadas (u, v) de um ponto X em relação à linha."""
        vetor_PX = X - self.P
        # Projeção de PX em PQ para obter u
        u = np.dot(vetor_PX, self.vetor_PQ) / self.comprimento_quadrado
        # Projeção de PX na perpendicular de PQ para obter v
        v = np.dot(vetor_PX, self.vetor_perpendicular) / np.sqrt(self.comprimento_quadrado)
        return u, v

    def obter_ponto_absoluto(self, u, v):
        """Calcula o ponto X a partir das coordenadas relativas (u, v)."""
        return self.P + u * self.vetor_PQ + (v * self.vetor_perpendicular) / np.sqrt(self.comprimento_quadrado)


def deformar_imagem(img_origem, pontos_origem, pontos_destino, a=1.0, b=2.0, p=0.5):
    """
    Deforma uma imagem de origem para se alinhar com a geometria de destino.
    Usa o algoritmo de Beier-Neely (Field Morphing).
    """
    linhas_origem = [Linha(pontos_origem[i], pontos_origem[i+1]) for i in range(0, len(pontos_origem)-1, 2)]
    linhas_destino = [Linha(pontos_destino[i], pontos_destino[i+1]) for i in range(0, len(pontos_destino)-1, 2)]

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
                
                # Calcula o peso da linha
                dist = np.abs(v)
                if 0 <= u <= 1:
                    dist = abs(v)
                elif u < 0:
                    dist = np.linalg.norm(ponto_X - linha_dst.P)
                else: # u > 1
                    dist = np.linalg.norm(ponto_X - linha_dst.Q)

                peso = (linha_src.comprimento_quadrado**p / (a + dist))**b
                
                deslocamento_total += deslocamento * peso
                peso_total += peso
            
            ponto_final_fonte = ponto_X + deslocamento_total / peso_total
            x_src, y_src = ponto_final_fonte

            # Interpolação bilinear para obter a cor
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
    """
    Calcula um único frame do morphing para um tempo 't'.
    """
    # 1. Interpola os pontos de controle
    pontos_intermediarios = (1 - t) * pontos_inicial + t * pontos_final

    # 2. Deforma ambas as imagens para a geometria intermediária
    img_inicial_deformada = deformar_imagem(img_inicial, pontos_inicial, pontos_intermediarios)
    img_final_deformada = deformar_imagem(img_final, pontos_final, pontos_intermediarios)

    # 3. Dissolução cruzada das cores
    img_morph = ((1 - t) * img_inicial_deformada.astype(float) + t * img_final_deformada.astype(float)).astype(np.uint8)
    
    return img_morph


def main():
    print("Iniciando o processo de morphing...")
    
    try:
        img_inicial = imageio.imread(ARQUIVO_IMAGEM_INICIAL)
        img_final = imageio.imread(ARQUIVO_IMAGEM_FINAL)
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado! Verifique se '{e.filename}' está na mesma pasta do script.")
        return

    if img_inicial.shape != img_final.shape:
        print("Erro: As imagens inicial e final devem ter as mesmas dimensões (largura x altura).")
        return

    # Adiciona os cantos das imagens aos pontos de controle para fixar as bordas
    altura, largura = img_inicial.shape
    cantos = np.array([
        [0, 0], [largura - 1, 0], [0, altura - 1], [largura - 1, altura - 1]
    ])
    pontos_inicial = np.vstack([lista_pontos_inicial, cantos])
    pontos_final = np.vstack([lista_pontos_final, cantos])

    frames = []
    output_dir = "frames_morphing"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Gerando {NUM_FRAMES} frames...")
    for i in range(NUM_FRAMES):
        t = i / (NUM_FRAMES - 1)
        
        print(f"  - Processando frame {i+1}/{NUM_FRAMES} (t = {t:.2f})")
        
        frame_morph = morph(img_inicial, img_final, pontos_inicial, pontos_final, t)
        frames.append(frame_morph)
        
        # Salva cada frame como um arquivo PGM individual
        nome_frame = os.path.join(output_dir, f'frame_{i:03d}.pgm')
        imageio.imwrite(nome_frame, frame_morph, format='pgm')

    print("\nFrames gerados com sucesso na pasta 'frames_morphing'.")

    # Cria um GIF animado com os frames
    gif_path = "resultado_morphing.gif"
    print(f"Criando GIF animado em '{gif_path}'...")
    imageio.mimsave(gif_path, frames, fps=30)

    print("\nProcesso concluído!")

if __name__ == '__main__':
    main()