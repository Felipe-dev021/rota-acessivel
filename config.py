"""Configurações centralizadas (Fonte Única da Verdade) do jogo 'Rota Acessível'.

Todas as constantes de janela, grade, física, tempos, custos, paletas de cores
(normal e alto contraste), escalas de fonte (normal e grande), estados da
máquina de estados, nomes de assets e funções de resolução de caminhos
compatíveis com execução direta e empacotamento PyInstaller residem aqui.
"""

import os
import sys

# =============================================================================
# CAMINHOS COMPATÍVEIS COM EXECUÇÃO NORMAL E PYINSTALLER
# =============================================================================
if getattr(sys, "frozen", False):
    PASTA_BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    PASTA_EXECUTAVEL = os.path.dirname(os.path.abspath(sys.executable))
else:
    PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
    PASTA_EXECUTAVEL = PASTA_BASE

PASTA_DATA = os.path.join(PASTA_BASE, "data")


def caminho_arquivo(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto para um asset somente leitura em data/.

    Compatível tanto com execução via Python quanto empacotado com PyInstaller.

    Args:
        nome_arquivo: Nome do arquivo de imagem, som ou recurso em data/.

    Returns:
        Caminho absoluto para o arquivo solicitado.
    """
    return os.path.join(PASTA_DATA, nome_arquivo)


def caminho_save(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto gravável para arquivos de progresso do usuário.

    Quando empacotado com PyInstaller (--onefile), grava ao lado do executável
    para preservar o progresso entre execuções.

    Args:
        nome_arquivo: Nome do arquivo gravável (ex.: 'progresso.json').

    Returns:
        Caminho absoluto gravável na pasta do executável/script.
    """
    return os.path.join(PASTA_EXECUTAVEL, nome_arquivo)


# =============================================================================
# JANELA, GRADE E TAXA DE QUADROS
# =============================================================================
TITULO_JOGO = "Rota Acessível — Acessibilidade e Inclusão (Tema 07)"
TILE = 48
COLS = 20
ROWS = 11
HUD_ALTURA = 96
LARGURA = COLS * TILE            # 960 px
ALTURA = HUD_ALTURA + ROWS * TILE  # 624 px
FPS = 60
DT_MAXIMO = 0.05                 # teto de delta time para estabilidade física

# =============================================================================
# FÍSICA, MOVIMENTO E INTERAÇÃO
# =============================================================================
VELOCIDADE_JOGADOR = 220.0       # pixels por segundo
VELOCIDADE_MORADOR = 190.0       # pixels por segundo
RAIO_INTERACAO = 64.0            # pixels entre centros
HITBOX_JOGADOR_MARGEM = 8        # margem reduzida para deslizar nas quinas

# =============================================================================
# REGRAS DE TEMPO, PENALIDADE E FEEDBACK
# =============================================================================
PENALIDADE_ERRO = 5.0            # segundos descontados ao encontrar bloqueio
TEMPO_ALERTA_CRITICO = 15.0      # segundos para destaque visual no cronômetro
DURACAO_FEEDBACK = 6.5           # segundos de exibição da barra educativa
ALTURA_FEEDBACK = 58             # altura da faixa inferior temporária

# =============================================================================
# CUSTOS DAS INTERVENÇÕES DE ACESSIBILIDADE
# =============================================================================
CUSTO_LIXEIRA = 0
CUSTO_DEGRAU = 1
CUSTO_BURACO = 1
CUSTO_SEM_PISO_TATIL = 1
CUSTO_AVISO_SONORO = 1

# =============================================================================
# ORÇAMENTO, TEMPO E CLASSIFICAÇÃO QUALITATIVA DE AUTONOMIA (4 FASES)
# =============================================================================
TEMPO_FASE_1 = 90.0
RECURSOS_FASE_1 = 3
CUSTO_OTIMO_FASE_1 = 1

TEMPO_FASE_2 = 80.0
RECURSOS_FASE_2 = 4
CUSTO_OTIMO_FASE_2 = 3

TEMPO_FASE_3 = 75.0
RECURSOS_FASE_3 = 4
CUSTO_OTIMO_FASE_3 = 3

TEMPO_FASE_4 = 70.0
RECURSOS_FASE_4 = 5
CUSTO_OTIMO_FASE_4 = 5

NIVEL_AUTONOMIA_EXEMPLAR = "Rota Exemplar"
NIVEL_AUTONOMIA_EFICIENTE = "Rota Eficiente"
NIVEL_AUTONOMIA_SEGURA = "Rota Segura"
NIVEL_AUTONOMIA_BLOQUEADA = "Rota Bloqueada"

# =============================================================================
# ESTADOS DA MÁQUINA DE ESTADOS
# =============================================================================
ESTADO_MENU = "MENU"
ESTADO_INSTRUCOES = "INSTRUCOES"
ESTADO_MAPA = "MAPA"
ESTADO_JOGANDO = "JOGANDO"
ESTADO_PAUSA = "PAUSA"
ESTADO_TRANSICAO = "TRANSICAO"
ESTADO_FIM = "FIM"
ESTADO_CREDITOS = "CREDITOS"

# =============================================================================
# TIPOS DE ELEMENTOS E BARREIRAS DO CENÁRIO
# =============================================================================
TIPO_LIXEIRA = "lixeira"
TIPO_DEGRAU = "degrau"
TIPO_BURACO = "buraco"
TIPO_SEM_PISO_TATIL = "sem_piso_tatil"
TIPO_AVISO_SONORO = "aviso_sonoro"
TIPO_POSTE = "poste"
TIPO_RAMPA = "rampa"
TIPO_PISO_OK = "piso_ok"
TIPO_PISO_TATIL = "piso_tatil"
TIPO_PAINEL_VISUAL = "painel_visual"
TIPO_DESTINO = "destino"

# =============================================================================
# NOMES DOS ARQUIVOS DE ASSETS (PASTA data/)
# =============================================================================
ARQUIVO_IMG_PLAYER = "player.png"
ARQUIVO_IMG_MORADOR = "morador.png"
ARQUIVO_IMG_LIXEIRA = "lixeira.png"
ARQUIVO_IMG_DEGRAU = "degrau.png"
ARQUIVO_IMG_BURACO = "buraco.png"
ARQUIVO_IMG_SEM_PISO_TATIL = "sem_piso_tatil.png"
ARQUIVO_IMG_AVISO_SONORO = "aviso_sonoro.png"
ARQUIVO_IMG_POSTE = "poste.png"
ARQUIVO_IMG_RAMPA = "rampa.png"
ARQUIVO_IMG_PISO_OK = "piso_ok.png"
ARQUIVO_IMG_PISO_TATIL = "piso_tatil.png"
ARQUIVO_IMG_PAINEL_VISUAL = "painel_visual.png"
ARQUIVO_IMG_DESTINO = "destino.png"

ARQUIVO_SOM_ACAO = "acao.wav"
ARQUIVO_SOM_ERRO = "erro.wav"
ARQUIVO_SOM_VITORIA = "vitoria.wav"
ARQUIVO_SOM_CLIQUE = "clique.wav"
ARQUIVO_MUSICA_FUNDO = "musica.wav"
ARQUIVO_SAVE_PROGRESSO = "progresso.json"

# =============================================================================
# PARÂMETROS DE ÁUDIO
# =============================================================================
AUDIO_SAMPLE_RATE = 22050
AUDIO_VOLUME_EFEITOS = 0.45
AUDIO_VOLUME_MUSICA = 0.25

# =============================================================================
# ESCALAS DE FONTE (ACESSIBILIDADE: TECLA [F] NORMAL / GRANDE)
# =============================================================================
FONTE_FAMILIA = "arial"

FONTES_NORMAL = {
    "titulo": 34,
    "subtitulo": 20,
    "media": 16,
    "normal": 14,
    "pequena": 13,
    "sigla": 18,
}

FONTES_GRANDE = {
    "titulo": 38,
    "subtitulo": 23,
    "media": 18,
    "normal": 16,
    "pequena": 15,
    "sigla": 21,
}

# Espessura da borda de alto contraste nos tiles
BORDA_ALTO_CONTRASTE = 4

# =============================================================================
# PALETAS DE CORES (MODO NORMAL E MODO ALTO CONTRASTE — TECLA [C])
# =============================================================================
CORES_NORMAL = {
    "fundo_tela": (24, 34, 48),
    "faixa_servico": (176, 184, 194),
    "calcada_clara": (218, 222, 228),
    "calcada_escura": (204, 210, 218),
    "grade_linha": (172, 180, 190),
    "hud_fundo": (20, 32, 52),
    "hud_borda": (68, 136, 204),
    "texto_principal": (245, 248, 252),
    "texto_secundario": (188, 206, 226),
    "destaque_e": (255, 214, 10),
    "destaque_e_texto": (18, 24, 34),
    "sucesso_fundo": (20, 92, 56),
    "sucesso_borda": (74, 222, 128),
    "erro_fundo": (127, 29, 29),
    "erro_borda": (248, 113, 113),
    "aviso": (250, 204, 21),
    "botao_fundo": (38, 70, 115),
    "botao_borda": (96, 165, 250),
    "painel_fundo": (28, 42, 64),
    "painel_borda": (82, 122, 170),
    "rota_livre": (34, 197, 94),
    "rota_preview": (56, 189, 248),
    "partida_marcador": (37, 99, 235),
    "destino_marcador": (22, 163, 74),
    "overlay": (12, 18, 28, 196),
    # Cores de referência para partículas e modo alto contraste
    "tile_lixeira": (46, 134, 95),
    "tile_degrau": (186, 104, 52),
    "tile_buraco": (82, 70, 74),
    "tile_sem_piso_tatil": (168, 85, 247),
    "tile_aviso_sonoro": (234, 88, 12),
    "tile_poste": (96, 104, 116),
    "tile_rampa": (44, 152, 214),
    "tile_piso_ok": (118, 184, 126),
    "tile_piso_tatil": (234, 179, 8),
    "tile_painel_visual": (14, 165, 233),
    "tile_destino": (34, 168, 92),
    "tile_borda": (38, 46, 58),
    "tile_sigla": (255, 255, 255),
}

CORES_ALTO_CONTRASTE = {
    "fundo_tela": (0, 0, 0),
    "faixa_servico": (32, 32, 32),
    "calcada_clara": (16, 16, 16),
    "calcada_escura": (26, 26, 26),
    "grade_linha": (120, 120, 120),
    "hud_fundo": (0, 0, 0),
    "hud_borda": (255, 255, 0),
    "texto_principal": (255, 255, 255),
    "texto_secundario": (255, 255, 0),
    "destaque_e": (255, 255, 0),
    "destaque_e_texto": (0, 0, 0),
    "sucesso_fundo": (0, 64, 0),
    "sucesso_borda": (0, 255, 128),
    "erro_fundo": (104, 0, 0),
    "erro_borda": (255, 80, 80),
    "aviso": (255, 255, 0),
    "botao_fundo": (0, 0, 0),
    "botao_borda": (255, 255, 0),
    "painel_fundo": (8, 8, 8),
    "painel_borda": (255, 255, 255),
    "rota_livre": (0, 255, 128),
    "rota_preview": (0, 255, 255),
    "partida_marcador": (0, 200, 255),
    "destino_marcador": (255, 255, 0),
    "overlay": (0, 0, 0, 224),
    # Cores de alto contraste por elemento (sempre acompanhadas de sigla)
    "tile_lixeira": (0, 175, 255),
    "tile_degrau": (255, 128, 0),
    "tile_buraco": (235, 0, 180),
    "tile_sem_piso_tatil": (200, 100, 255),
    "tile_aviso_sonoro": (255, 90, 90),
    "tile_poste": (235, 0, 0),
    "tile_rampa": (0, 235, 235),
    "tile_piso_ok": (0, 225, 100),
    "tile_piso_tatil": (255, 235, 0),
    "tile_painel_visual": (0, 220, 255),
    "tile_destino": (255, 255, 0),
    "tile_borda": (255, 255, 255),
    "tile_sigla": (0, 0, 0),
}
