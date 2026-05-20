import tkinter as tk
import random
import math

# Configurações da janela
LARGURA = 600
ALTURA = 700
VELOCIDADE = 20

# Tamanhos base do Minecraft
JOGADOR_TAM = 35
ESTRELA_TAM = 30
TNT_TAM = 33

# Estado do Jogo
jogador_x = LARGURA // 2
jogador_y = ALTURA - 70
pontos = 0
vidas = 4
teclas_pressionadas = set()
jogo_ativo = True

# Lista de objetos na tela
lista_estrelas = []
lista_tnts = []
baloes_texto = []

# Sequência de ondas de estrelas pedido por você: 2 -> 3 -> 1 -> 3 -> 1 -> ...
sequencia_ondas = [2, 3, 1, 3, 1]
indice_onda = 0

# Janela Principal
janela = tk.Tk()
janela.title("Capture a Estrela! 💫💫")
janela.resizable(False, False)

canvas = tk.Canvas(janela, width=LARGURA, height=ALTURA, bg="#14141f")
canvas.pack()

# Criar os elementos fixos na tela
placar = canvas.create_text(12, 12, anchor="nw", text="XP: 0", fill="#55FF55", font=("Courier New", 16, "bold"))
txt_vidas = canvas.create_text(LARGURA - 10, 10, anchor="ne", text="VIDAS: ♨️♨️♨️♨️", fill="#FF5555", font=("Courier New", 14, "bold"))

# Criar o Jogador (Steve de Diamante)
jogador = canvas.create_rectangle(
    jogador_x, jogador_y, jogador_x + JOGADOR_TAM, jogador_y + JOGADOR_TAM,
    fill="#00AAAA", outline="#00FFFF", width=3
)

def calcular_pontos_estrela(cx, cy, r_ext, r_int, n=4):
    """Cria uma Estrela do Nether estilizada de 4 pontas estilo Minecraft."""
    pontos_lista = []
    for i in range(n * 2):
        angulo = (i * math.pi / n) - math.pi / 2
        r = r_ext if i % 2 == 0 else r_int
        pontos_lista.append(cx + r * math.cos(angulo))
        pontos_lista.append(cy + r * math.sin(angulo))
    return pontos_lista

def criar_nova_onda():
    global indice_onda, lista_estrelas, lista_tnts

    # Limpa estrelas e TNTs antigas se houver
    for est in lista_estrelas: canvas.delete(est['id'])
    for tnt in lista_tnts: canvas.delete(tnt['id'])
    lista_estrelas.clear()
    lista_tnts.clear()

    # Define quantas estrelas vão cair nessa rodada baseado na sua lista sequencial
    qtd_estrelas = sequencia_ondas[indice_onda]
    indice_onda = (indice_onda + 1) % len(sequencia_ondas) # Avança ou reinicia a sequência

    # Cria as estrelas nos locais aleatórios do céu
    for _ in range(qtd_estrelas):
        ex = random.randint(10, LARGURA - ESTRELA_TAM - 10)
        ey = random.randint(-150, -40) # Brotam acima da tela para irem caindo
        vel = random.randint(3, 6)

        id_desenho = canvas.create_polygon([0,0,0,0], fill="#FFFFFF", outline="#AAAAAA", width=2)
        lista_estrelas.append({'id': id_desenho, 'x': ex, 'y': ey, 'vel': vel})

    # Adiciona blocos de TNT perigosos para ele se esquivar (quantidade aumenta com os pontos)
    qtd_tnts = random.randint(1, 3) + (pontos // 5)
    for _ in range(min(qtd_tnts, 6)): # Limita a no máximo 6 TNTs na tela para não travar
        tx = random.randint(10, LARGURA - TNT_TAM - 10)
        ty = random.randint(-200, -40)
        vel = random.randint(4, 7)

        # TNT Vermelha quadriculada do Minecraft
        id_tnt = canvas.create_rectangle(tx, ty, tx + TNT_TAM, ty + TNT_TAM, fill="#FF2222", outline="#FFFFFF", width=2)
        lista_tnts.append({'id': id_tnt, 'x': tx, 'y': ty, 'vel': vel})

def criar_balao_mais_um(x, y):
    """Gera o balão flutuante '+1' verde de XP na tela."""
    id_balao = canvas.create_text(x, y, text="+1 XP", fill="#55FF55", font=("Courier New", 14, "bold"))
    baloes_texto.append({'id': id_balao, 'y': y, 'tempo': 0})

def atualizar_objetos():
    global pontos, vidas, jogo_ativo
    if not jogo_ativo: return

    # 1. Movimentar e desenhar Estrelas
    for est in lista_estrelas:
        est['y'] += est['vel']
        cx = est['x'] + ESTRELA_TAM // 2
        cy = est['y'] + ESTRELA_TAM // 2
        coords = calcular_pontos_estrela(cx, cy, ESTRELA_TAM // 2, ESTRELA_TAM // 4)
        canvas.coords(est['id'], *coords)

        # Se passar do fundo da tela, volta pro topo
        if est['y'] > ALTURA:
            est['y'] = random.randint(-100, -40)
            est['x'] = random.randint(10, LARGURA - ESTRELA_TAM - 10)

        # Colisão Jogador com Estrela
        if (jogador_x < est['x'] + ESTRELA_TAM and jogador_x + JOGADOR_TAM > est['x'] and
            jogador_y < est['y'] + ESTRELA_TAM and jogador_y + JOGADOR_TAM > est['y']):
            pontos += 1
            canvas.itemconfig(placar, text=f"XP: {pontos}")
            criar_balao_mais_um(est['x'], est['y'])

            # Efeito piscar de sucesso verde
            canvas.config(bg="#003300")
            janela.after(80, lambda: canvas.config(bg="#14141f"))

            # Quando pega todas as estrelas da onda atual, brota a próxima onda
            criar_nova_onda()
            break

    # 2. Movimentar e desenhar TNTs perigosas
    for tnt in lista_tnts:
        tnt['y'] += tnt['vel']
        canvas.coords(tnt['id'], tnt['x'], tnt['y'], tnt['x'] + TNT_TAM, tnt['y'] + TNT_TAM)

        if tnt['y'] > ALTURA:
            tnt['y'] = random.randint(-150, -40)
            tnt['x'] = random.randint(10, LARGURA - TNT_TAM - 10)

        # Colisão Jogador com TNT (Perde Vida)
        if (jogador_x < tnt['x'] + TNT_TAM and jogador_x + JOGADOR_TAM > tnt['x'] and
            jogador_y < tnt['y'] + TNT_TAM and jogador_y + JOGADOR_TAM > tnt['y']):
            vidas -= 1

            # Atualiza os corações na tela
            coracoes = "♨️ " * vidas if vidas > 0 else "GAME OVER"
            canvas.itemconfig(txt_vidas, text=f"VIDAS: {coracoes}")

            # Efeito piscar de dano vermelho na tela
            canvas.config(bg="#440000")
            janela.after(120, lambda: canvas.config(bg="#14141f"))

            if vidas <= 0:
                finalizar_jogo()
                return
            else:
                # Reseta a onda para dar respiro ao jogador
                criar_nova_onda()
                break

    # 3. Animar os balões de texto subindo e sumindo
    for b in baloes_texto[:]:
        b['y'] -= 2
        b['tempo'] += 1
        canvas.coords(b['id'], canvas.coords(b['id'])[0], b['y'])
        if b['tempo'] > 15: # Remove o balão depois de subir um pouco
            canvas.delete(b['id'])
            baloes_texto.remove(b)

def mover_jogador():
    global jogador_x, jogador_y
    if not jogo_ativo: return

    # Jogador se move MAIS RÁPIDO agora (velocidade 8 em vez de 5!)
    passo = 8

    if "Left" in teclas_pressionadas and jogador_x > 0:
        jogador_x -= passo
    if "Right" in teclas_pressionadas and jogador_x < LARGURA - JOGADOR_TAM:
        jogador_x += passo
    if "Up" in teclas_pressionadas and jogador_y > 0:
        jogador_y -= passo
    if "Down" in teclas_pressionadas and jogador_y < ALTURA - JOGADOR_TAM:
        jogador_y += passo

    canvas.coords(jogador, jogador_x, jogador_y, jogador_x + JOGADOR_TAM, jogador_y + JOGADOR_TAM)

def finalizar_jogo():
    global jogo_ativo
    jogo_ativo = False

    # Tela de Game Over estilizada do Minecraft
    canvas.create_rectangle(0, 0, LARGURA, ALTURA, fill="#110000", stipple="gray50", tags="fim")
    canvas.create_text(LARGURA//2, ALTURA//3, text="Você Morreu!", fill="#FF2222", font=("Courier New", 32, "bold"), tags="fim")
    canvas.create_text(LARGURA//2, ALTURA//2, text=f"Pontuação Final: {pontos} XP", fill="#FFFFFF", font=("Courier New", 18), tags="fim")

    # Botão jogar de novo integrado ao Canvas
    botao_reiniciar = tk.Button(janela, text="JOGAR DE NOVO 🔁", font=("Courier New", 14, "bold"), bg="#55FF55", fg="#000000", command=reiniciar_jogo)
    canvas.create_window(LARGURA//2, ALTURA * 2 // 3, window=botao_reiniciar, tags="fim")

def reiniciar_jogo():
    global jogador_x, jogador_y, pontos, vidas, jogo_ativo, indice_onda
    canvas.delete("fim") # Remove os textos e botão de game over

    jogador_x = LARGURA // 2
    jogador_y = ALTURA - 70
    pontos = 0
    vidas = 4
    indice_onda = 0
    jogo_ativo = True

    canvas.itemconfig(placar, text="XP: 0")
    canvas.itemconfig(txt_vidas, text="VIDAS: ♨️♨️♨️♨️")
    canvas.coords(jogador, jogador_x, jogador_y, jogador_x + JOGADOR_TAM, jogador_y + JOGADOR_TAM)

    criar_nova_onda()

def tecla_pressionada(evento): teclas_pressionadas.add(evento.keysym)
def tecla_solta(evento): teclas_pressionadas.discard(evento.keysym)

def loop_jogo():
    mover_jogador()
    atualizar_objetos()
    janela.after(VELOCIDADE, loop_jogo)

janela.bind("<KeyPress>", tecla_pressionada)
janela.bind("<KeyRelease>", tecla_solta)

# Inicialização
criar_nova_onda()
loop_jogo()
janela.mainloop()
