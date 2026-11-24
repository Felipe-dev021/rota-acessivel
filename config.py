"""Configurações centralizadas (Fonte Única da Verdade) do jogo 'Rota Acessível'.

Todas as constantes de janela, grade, física ágil, tempos, custos, paletas
inspiradas em Maricá/RJ (modo normal ensolarado e modo alto contraste), escalas
de fonte, perfis de moradores, estados da máquina de estados, nomes de assets e
resolução de caminhos compatíveis com Python e PyInstaller residem aqui.
"""

import os
import sys

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


TITULO_JOGO = "Rota Acessível — Maricá/RJ (Acessibilidade e Inclusão)"
TILE = 48
ALTURA_SPRITE_25D = 64
COLS = 20
ROWS = 11
HUD_ALTURA = 96
LARGURA = COLS * TILE
ALTURA = HUD_ALTURA + ROWS * TILE
FPS = 60
DT_MAXIMO = 0.05

VELOCIDADE_JOGADOR = 335.0
VELOCIDADE_SPRINT = 465.0
CORNER_NUDGE_MAX = 22
VELOCIDADE_MORADOR = 245.0
RAIO_INTERACAO = 84.0
HITBOX_JOGADOR_LARGURA = 18
HITBOX_JOGADOR_ALTURA = 14

PENALIDADE_ERRO = 5.0
TEMPO_ALERTA_CRITICO = 15.0
DURACAO_FEEDBACK = 6.5
ALTURA_FEEDBACK = 64
DURACAO_POPUP = 1.25

CUSTO_LIXEIRA = 0
CUSTO_DEGRAU = 1
CUSTO_BURACO = 1
CUSTO_SEM_PISO_TATIL = 1
CUSTO_AVISO_SONORO = 1

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

PERFIL_CADEIRANTE = "cadeirante"
PERFIL_SURDO = "surdo"
PERFIL_BAIXA_VISAO = "baixa_visao"

ESTADO_MENU = "MENU"
ESTADO_INSTRUCOES = "INSTRUCOES"
ESTADO_MAPA = "MAPA"
ESTADO_BRIEFING = "BRIEFING"
ESTADO_JOGANDO = "JOGANDO"
ESTADO_PAUSA = "PAUSA"
ESTADO_TRANSICAO = "TRANSICAO"
ESTADO_FIM = "FIM"
ESTADO_CREDITOS = "CREDITOS"

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

AUDIO_SAMPLE_RATE = 22050
AUDIO_VOLUME_EFEITOS = 0.45
AUDIO_VOLUME_MUSICA = 0.20

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

CORES_NORMAL = {
    "fundo_tela": (246, 239, 226),
    "lagoa_azul": (42, 157, 204),
    "lagoa_brilho": (118, 208, 238),
    "ciclovia_vermelha": (196, 54, 54),
    "vermelhinho": (214, 40, 40),
    "faixa_servico": (92, 158, 86),
    "asfalto": (74, 82, 94),
    "faixa_rua": (248, 244, 234),
    "calcada_clara": (238, 231, 216),
    "calcada_escura": (228, 220, 204),
    "meio_fio": (182, 172, 154),
    "grade_linha": (212, 204, 188),
    "hud_fundo": (26, 46, 68),
    "hud_cartao": (38, 64, 92),
    "hud_borda": (220, 56, 56),
    "texto_principal": (250, 248, 244),
    "texto_escuro": (36, 32, 28),
    "texto_secundario": (205, 220, 234),
    "texto_suave_escuro": (102, 90, 78),
    "destaque_e": (255, 202, 40),
    "destaque_e_texto": (30, 24, 18),
    "sucesso_fundo": (22, 122, 86),
    "sucesso_borda": (74, 222, 128),
    "erro_fundo": (184, 72, 54),
    "erro_borda": (253, 186, 116),
    "aviso": (251, 191, 36),
    "botao_fundo": (255, 252, 246),
    "botao_hover": (254, 238, 212),
    "botao_borda": (206, 58, 52),
    "painel_fundo": (253, 249, 240),
    "painel_borda": (184, 156, 122),
    "rota_livre": (28, 178, 96),
    "rota_preview": (36, 156, 218),
    "partida_marcador": (32, 98, 214),
    "destino_marcador": (204, 44, 44),
    "overlay": (20, 28, 38, 188),
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
    "lagoa_azul": (0, 48, 80),
    "lagoa_brilho": (0, 255, 255),
    "ciclovia_vermelha": (90, 0, 0),
    "vermelhinho": (255, 60, 60),
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
