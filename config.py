"""Configurações centralizadas (Fonte Única da Verdade) do jogo 'Rota Acessível'.

Todas as constantes de janela, grade, física, tempos, custos, paletas de cores
(normal acolhedora estilo cartoon e alto contraste), escalas de fonte (normal e
grande), perfis de moradores, estados da máquina de estados, nomes de assets e
funções de resolução de caminhos compatíveis com Python e PyInstaller ficam aqui.
"""

import os
import sys

# =============================================================================
# CAMINHOS COMPATÍVEIS COM EXECUÇÃO NORMAL E PYINSTALLER
# =============================================================================
if getattr(sys, "frozen", False):
    PASTA_BASE = getattr(
        sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable))
    )
    PASTA_EXECUTAVEL = os.path.dirname(os.path.abspath(sys.executable))
else:
    PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
    PASTA_EXECUTAVEL = PASTA_BASE

PASTA_DATA = os.path.abspath(os.path.join(PASTA_BASE, "data"))


def caminho_arquivo(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto para um asset somente leitura em data/.

    Args:
        nome_arquivo: Nome do arquivo de imagem ou áudio dentro de data/.

    Returns:
        Caminho absoluto completo para o recurso solicitado.
    """
    return os.path.join(PASTA_DATA, nome_arquivo)


def caminho_save(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto gravável para arquivos de progresso do usuário.

    Args:
        nome_arquivo: Nome do arquivo gravável (ex.: 'progresso.json').

    Returns:
        Caminho absoluto gravável na pasta do executável/script.
    """
    return os.path.join(PASTA_EXECUTAVEL, nome_arquivo)


# =============================================================================
# JANELA, GRADE E TAXA DE QUADROS
# =============================================================================
TITULO_JOGO = "Rota Acessível — Vila Nova (Acessibilidade e Inclusão)"
TILE = 48
COLS = 20
ROWS = 11
HUD_ALTURA = 96
LARGURA = COLS * TILE              # 960 px
ALTURA = HUD_ALTURA + ROWS * TILE  # 624 px
FPS = 60
DT_MAXIMO = 0.05                   # teto de delta time para estabilidade física

# =============================================================================
# FÍSICA, MOVIMENTO FLUIDO E INTERAÇÃO
# =============================================================================
VELOCIDADE_JOGADOR = 245.0         # pixels por segundo (ágil e responsivo)
ACELERACAO_JOGADOR = 18.0          # suavidade de arranque/parada
CORNER_NUDGE_MAX = 16              # deslizamento automático em quinas (px)
VELOCIDADE_MORADOR = 205.0         # pixels por segundo
RAIO_INTERACAO = 72.0              # raio confortável para destaque [E]
HITBOX_JOGADOR_MARGEM = 11         # hitbox 26x26 dentro de 48x48 (zero travamento)

# =============================================================================
# REGRAS DE TEMPO, PENALIDADE E FEEDBACK
# =============================================================================
PENALIDADE_ERRO = 5.0              # segundos descontados ao encontrar bloqueio
TEMPO_ALERTA_CRITICO = 15.0        # segundos para alerta visual no cronômetro
DURACAO_FEEDBACK = 7.0             # segundos de exibição da barra educativa
ALTURA_FEEDBACK = 64               # altura da faixa educativa inferior

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

TEMPO_FASE_2 = 85.0
RECURSOS_FASE_2 = 4
CUSTO_OTIMO_FASE_2 = 3

TEMPO_FASE_3 = 80.0
RECURSOS_FASE_3 = 4
CUSTO_OTIMO_FASE_3 = 3

TEMPO_FASE_4 = 75.0
RECURSOS_FASE_4 = 5
CUSTO_OTIMO_FASE_4 = 5

NIVEL_AUTONOMIA_EXEMPLAR = "Rota Exemplar"
NIVEL_AUTONOMIA_EFICIENTE = "Rota Eficiente"
NIVEL_AUTONOMIA_SEGURA = "Rota Segura"
NIVEL_AUTONOMIA_BLOQUEADA = "Rota Bloqueada"

# =============================================================================
# PERFIS DE MORADORES (COERÊNCIA TOTAL ENTRE PERSONAGEM E BARREIRAS DA FASE)
# =============================================================================
PERFIL_CADEIRANTE = "cadeirante"
PERFIL_SURDO = "surdo"
PERFIL_BAIXA_VISAO = "baixa_visao"

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
ARQUIVO_IMG_MORADOR_SURDO = "morador_surdo.png"
ARQUIVO_IMG_MORADOR_BAIXA_VISAO = "morador_baixa_visao.png"

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
AUDIO_VOLUME_MUSICA = 0.22

# =============================================================================
# ESCALAS DE FONTE (ACESSIBILIDADE: TECLA [F] NORMAL / GRANDE)
# =============================================================================
FONTE_FAMILIA = "segoeui"

FONTES_NORMAL = {
    "titulo": 36,
    "subtitulo": 20,
    "media": 16,
    "normal": 14,
    "pequena": 13,
    "sigla": 18,
}

FONTES_GRANDE = {
    "titulo": 40,
    "subtitulo": 23,
    "media": 18,
    "normal": 16,
    "pequena": 15,
    "sigla": 21,
}

BORDA_ALTO_CONTRASTE = 4

# =============================================================================
# PALETAS DE CORES (CARTOON URBANO ACOLHEDOR E MODO ALTO CONTRASTE)
# =============================================================================
CORES_NORMAL = {
    "fundo_tela": (244, 236, 224),       # creme quente acolhedor (estilo Vila Nova)
    "faixa_servico": (122, 168, 108),    # grama / canteiro urbano lateral
    "asfalto": (78, 86, 98),             # rua asfaltada na borda inferior
    "faixa_rua": (245, 240, 226),        # faixas de pedestres
    "calcada_clara": (235, 228, 214),    # piso de calçada ensolarada
    "calcada_escura": (225, 217, 202),   # alternância sutil de lajotas
    "meio_fio": (184, 174, 158),         # borda da calçada
    "grade_linha": (208, 200, 186),      # junta discreta das lajotas
    "hud_fundo": (38, 52, 68),           # barra superior azul-ardósia elegante
    "hud_cartao": (52, 70, 90),          # pílulas internas do HUD
    "hud_borda": (232, 168, 72),         # filete dourado quente
    "texto_principal": (250, 248, 244),
    "texto_escuro": (42, 34, 28),        # texto em cartões claros
    "texto_secundario": (205, 216, 228),
    "texto_suave_escuro": (106, 92, 80),
    "destaque_e": (255, 198, 41),
    "destaque_e_texto": (34, 26, 18),
    "sucesso_fundo": (26, 104, 72),
    "sucesso_borda": (74, 222, 128),
    "erro_fundo": (153, 38, 38),
    "erro_borda": (252, 165, 165),
    "aviso": (251, 191, 36),
    "botao_fundo": (255, 251, 245),
    "botao_hover": (254, 240, 214),
    "botao_borda": (196, 122, 62),
    "painel_fundo": (252, 247, 238),
    "painel_borda": (186, 154, 118),
    "rota_livre": (34, 176, 98),
    "rota_preview": (42, 157, 214),
    "partida_marcador": (37, 99, 215),
    "destino_marcador": (22, 156, 84),
    "overlay": (24, 30, 40, 188),
    # Cores temáticas por fase (fachadas/elementos decorativos)
    "fase_1_acento": (214, 116, 68),
    "fase_2_acento": (59, 130, 196),
    "fase_3_acento": (68, 158, 106),
    "fase_4_acento": (212, 76, 76),
    # Cores de referência para tiles/partículas
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
    "tile_borda": (48, 42, 36),
    "tile_sigla": (255, 255, 255),
}

CORES_ALTO_CONTRASTE = {
    "fundo_tela": (0, 0, 0),
    "faixa_servico": (28, 28, 28),
    "asfalto": (12, 12, 12),
    "faixa_rua": (255, 255, 255),
    "calcada_clara": (18, 18, 18),
    "calcada_escura": (28, 28, 28),
    "meio_fio": (255, 255, 0),
    "grade_linha": (115, 115, 115),
    "hud_fundo": (0, 0, 0),
    "hud_cartao": (18, 18, 18),
    "hud_borda": (255, 255, 0),
    "texto_principal": (255, 255, 255),
    "texto_escuro": (255, 255, 255),
    "texto_secundario": (255, 255, 0),
    "texto_suave_escuro": (255, 255, 0),
    "destaque_e": (255, 255, 0),
    "destaque_e_texto": (0, 0, 0),
    "sucesso_fundo": (0, 68, 0),
    "sucesso_borda": (0, 255, 128),
    "erro_fundo": (110, 0, 0),
    "erro_borda": (255, 80, 80),
    "aviso": (255, 255, 0),
    "botao_fundo": (12, 12, 12),
    "botao_hover": (42, 42, 0),
    "botao_borda": (255, 255, 0),
    "painel_fundo": (6, 6, 6),
    "painel_borda": (255, 255, 255),
    "rota_livre": (0, 255, 128),
    "rota_preview": (0, 255, 255),
    "partida_marcador": (0, 200, 255),
    "destino_marcador": (255, 255, 0),
    "overlay": (0, 0, 0, 224),
    "fase_1_acento": (255, 255, 0),
    "fase_2_acento": (0, 255, 255),
    "fase_3_acento": (0, 255, 128),
    "fase_4_acento": (255, 120, 0),
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
