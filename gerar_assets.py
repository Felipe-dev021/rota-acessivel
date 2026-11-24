"""Gerador procedural de assets 2.5D elevados (48x64 em pé e 48x48 de piso).

Desenha sprites em 2x HD (96x128 para entidades/objetos 3D em pé e 96x96 para
pisos) e aplica smoothscale, criando projeção 3/4 estilo Zelda/Stardew Valley
com altura vertical real, iluminação solar e estética de Maricá/RJ.
"""

import math
import os
import struct
import wave
from typing import List

import pygame

from config import (
    ALTURA_SPRITE_25D,
    ARQUIVO_IMG_AVISO_SONORO,
    ARQUIVO_IMG_BURACO,
    ARQUIVO_IMG_DEGRAU,
    ARQUIVO_IMG_DESTINO,
    ARQUIVO_IMG_LIXEIRA,
    ARQUIVO_IMG_MORADOR,
    ARQUIVO_IMG_MORADOR_BAIXA_VISAO,
    ARQUIVO_IMG_MORADOR_SURDO,
    ARQUIVO_IMG_PAINEL_VISUAL,
    ARQUIVO_IMG_PISO_OK,
    ARQUIVO_IMG_PISO_TATIL,
    ARQUIVO_IMG_PLAYER,
    ARQUIVO_IMG_POSTE,
    ARQUIVO_IMG_RAMPA,
    ARQUIVO_IMG_SEM_PISO_TATIL,
    ARQUIVO_MUSICA_FUNDO,
    ARQUIVO_SOM_ACAO,
    ARQUIVO_SOM_CLIQUE,
    ARQUIVO_SOM_ERRO,
    ARQUIVO_SOM_VITORIA,
    AUDIO_SAMPLE_RATE,
    PASTA_DATA,
    TILE,
    caminho_arquivo,
)

HD_LARG = TILE * 2
HD_PISO = TILE * 2
HD_ALTO = ALTURA_SPRITE_25D * 2


def _criar_tela_piso() -> pygame.Surface:
    """Cria superfície transparente 96x96 px para elementos planos de piso."""
    return pygame.Surface((HD_LARG, HD_PISO), pygame.SRCALPHA)


def _criar_tela_alto() -> pygame.Surface:
    """Cria superfície transparente 96x128 px para entidades e objetos 2.5D em pé."""
    return pygame.Surface((HD_LARG, HD_ALTO), pygame.SRCALPHA)


def _salvar_piso(surf_hd: pygame.Surface, nome_arquivo: str) -> None:
    """Aplica smoothscale 96x96 -> 48x48 e salva o sprite de piso em data/."""
    final = pygame.transform.smoothscale(surf_hd, (TILE, TILE))
    pygame.image.save(final, caminho_arquivo(nome_arquivo))


def _salvar_alto(surf_hd: pygame.Surface, nome_arquivo: str) -> None:
    """Aplica smoothscale 96x128 -> 48x64 e salva o sprite 2.5D elevado em data/."""
    final = pygame.transform.smoothscale(surf_hd, (TILE, ALTURA_SPRITE_25D))
    pygame.image.save(final, caminho_arquivo(nome_arquivo))


def _gerar_player() -> None:
    """Gera Alex em projeção 3/4 2.5D (48x64) com corpo completo e boné de Maricá."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 90), (20, 102, 62, 18))
    pygame.draw.rect(s, (38, 56, 86), (32, 82, 13, 24), border_radius=5)
    pygame.draw.rect(s, (38, 56, 86), (51, 82, 13, 24), border_radius=5)
    pygame.draw.ellipse(s, (28, 38, 56), (28, 100, 20, 12))
    pygame.draw.ellipse(s, (28, 38, 56), (48, 100, 20, 12))
    pygame.draw.ellipse(s, (242, 246, 250), (31, 106, 14, 4))
    pygame.draw.ellipse(s, (242, 246, 250), (51, 106, 14, 4))
    pygame.draw.rect(s, (28, 78, 198), (15, 52, 14, 28), border_radius=7)
    pygame.draw.rect(s, (28, 78, 198), (67, 52, 14, 28), border_radius=7)
    pygame.draw.circle(s, (242, 194, 158), (22, 80), 6)
    pygame.draw.circle(s, (242, 194, 158), (74, 80), 6)
    pygame.draw.rect(s, (24, 32, 48), (15, 52, 14, 28), 3, border_radius=7)
    pygame.draw.rect(s, (24, 32, 48), (67, 52, 14, 28), 3, border_radius=7)
    pygame.draw.rect(s, (28, 78, 198), (26, 48, 44, 40), border_radius=12)
    pygame.draw.rect(s, (234, 179, 8), (30, 50, 36, 34), border_radius=9)
    pygame.draw.rect(s, (254, 224, 68), (30, 50, 24, 22), border_radius=7)
    pygame.draw.rect(s, (245, 250, 255), (30, 62, 36, 6))
    pygame.draw.rect(s, (245, 250, 255), (30, 72, 36, 4))
    pygame.draw.rect(s, (24, 32, 48), (26, 48, 44, 40), 3, border_radius=12)
    pygame.draw.circle(s, (226, 174, 138), (48, 30), 20)
    pygame.draw.circle(s, (246, 204, 170), (45, 26), 15)
    pygame.draw.circle(s, (244, 142, 132, 115), (36, 36), 4)
    pygame.draw.circle(s, (244, 142, 132, 115), (60, 36), 4)
    pygame.draw.rect(s, (186, 32, 32), (28, 10, 40, 14), border_radius=8)
    pygame.draw.rect(s, (236, 68, 68), (28, 10, 28, 8), border_radius=6)
    pygame.draw.rect(s, (150, 22, 22), (38, 18, 36, 6), border_radius=3)
    pygame.draw.circle(s, (22, 26, 34), (42, 31), 3)
    pygame.draw.circle(s, (22, 26, 34), (56, 31), 3)
    pygame.draw.circle(s, (255, 255, 255), (43, 30), 1)
    pygame.draw.circle(s, (255, 255, 255), (57, 30), 1)
    pygame.draw.arc(s, (80, 42, 32), (42, 33, 14, 9), math.pi + 0.3, 2 * math.pi - 0.3, 2)
    pygame.draw.circle(s, (24, 32, 48), (48, 30), 20, 3)
    _salvar_alto(s, ARQUIVO_IMG_PLAYER)


def _gerar_morador_cadeirante() -> None:
    """Gera Clara/Lucas em projeção 2.5D (48x64) com cadeira de rodas detalhada."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 95), (14, 102, 74, 18))
    pygame.draw.rect(s, (24, 32, 46), (10, 52, 14, 56), border_radius=7)
    pygame.draw.rect(s, (24, 32, 46), (72, 52, 14, 56), border_radius=7)
    pygame.draw.rect(s, (214, 226, 240), (14, 58, 6, 44), border_radius=3)
    pygame.draw.rect(s, (214, 226, 240), (76, 58, 6, 44), border_radius=3)
    pygame.draw.rect(s, (29, 78, 216), (24, 42, 48, 52), border_radius=12)
    pygame.draw.rect(s, (59, 130, 246), (26, 44, 36, 30), border_radius=10)
    pygame.draw.rect(s, (68, 82, 102), (28, 94, 40, 12), border_radius=4)
    pygame.draw.rect(s, (24, 32, 48), (24, 42, 48, 52), 3, border_radius=12)
    pygame.draw.rect(s, (219, 39, 119), (28, 48, 40, 32), border_radius=10)
    pygame.draw.circle(s, (78, 46, 32), (48, 30), 20)
    pygame.draw.circle(s, (238, 188, 152), (48, 33), 17)
    pygame.draw.circle(s, (22, 26, 34), (42, 33), 3)
    pygame.draw.circle(s, (22, 26, 34), (54, 33), 3)
    pygame.draw.arc(s, (80, 42, 32), (42, 35, 12, 8), math.pi + 0.3, 2 * math.pi - 0.3, 2)
    pygame.draw.circle(s, (24, 32, 48), (48, 33), 17, 3)
    _salvar_alto(s, ARQUIVO_IMG_MORADOR)


def _gerar_morador_surdo() -> None:
    """Gera Sofia (moradora surda a pé) em projeção 2.5D (48x64)."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 90), (20, 102, 58, 18))
    pygame.draw.rect(s, (46, 56, 74), (32, 84, 13, 22), border_radius=5)
    pygame.draw.rect(s, (46, 56, 74), (51, 84, 13, 22), border_radius=5)
    pygame.draw.ellipse(s, (34, 42, 56), (28, 100, 19, 11))
    pygame.draw.ellipse(s, (34, 42, 56), (49, 100, 19, 11))
    pygame.draw.rect(s, (13, 148, 136), (15, 52, 13, 26), border_radius=6)
    pygame.draw.rect(s, (13, 148, 136), (68, 44, 13, 26), border_radius=6)
    pygame.draw.circle(s, (242, 192, 154), (74, 42), 6)
    pygame.draw.rect(s, (24, 32, 48), (15, 52, 13, 26), 3, border_radius=6)
    pygame.draw.rect(s, (24, 32, 48), (68, 44, 13, 26), 3, border_radius=6)
    pygame.draw.rect(s, (11, 126, 116), (26, 48, 44, 40), border_radius=12)
    pygame.draw.rect(s, (20, 174, 160), (28, 50, 30, 24), border_radius=10)
    pygame.draw.rect(s, (249, 115, 22), (34, 50, 28, 9), border_radius=5)
    pygame.draw.rect(s, (24, 32, 48), (26, 48, 44, 40), 3, border_radius=12)
    pygame.draw.circle(s, (82, 46, 28), (48, 28), 22)
    pygame.draw.circle(s, (242, 192, 154), (48, 32), 18)
    pygame.draw.circle(s, (56, 189, 248), (66, 32), 5)
    pygame.draw.circle(s, (22, 26, 34), (42, 32), 3)
    pygame.draw.circle(s, (22, 26, 34), (54, 32), 3)
    pygame.draw.arc(s, (80, 42, 32), (42, 34, 12, 8), math.pi + 0.3, 2 * math.pi - 0.3, 2)
    pygame.draw.circle(s, (24, 32, 48), (48, 32), 18, 3)
    _salvar_alto(s, ARQUIVO_IMG_MORADOR_SURDO)


def _gerar_morador_baixa_visao() -> None:
    """Gera Mateus (baixa visão com bengala branca) em projeção 2.5D (48x64)."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 90), (20, 102, 58, 18))
    pygame.draw.rect(s, (46, 56, 74), (32, 84, 13, 22), border_radius=5)
    pygame.draw.rect(s, (46, 56, 74), (51, 84, 13, 22), border_radius=5)
    pygame.draw.ellipse(s, (34, 42, 56), (28, 100, 19, 11))
    pygame.draw.ellipse(s, (34, 42, 56), (49, 100, 19, 11))
    pygame.draw.line(s, (22, 18, 14, 70), (68, 78), (92, 112), 7)
    pygame.draw.line(s, (24, 32, 48), (66, 72), (90, 108), 9)
    pygame.draw.line(s, (255, 255, 255), (66, 72), (88, 106), 5)
    pygame.draw.circle(s, (220, 38, 38), (90, 108), 5)
    pygame.draw.rect(s, (79, 70, 229), (15, 52, 13, 26), border_radius=6)
    pygame.draw.rect(s, (79, 70, 229), (66, 52, 13, 26), border_radius=6)
    pygame.draw.rect(s, (79, 70, 229), (26, 48, 44, 40), border_radius=12)
    pygame.draw.rect(s, (129, 140, 248), (28, 50, 30, 24), border_radius=10)
    pygame.draw.rect(s, (250, 204, 21), (42, 50, 12, 34), border_radius=4)
    pygame.draw.rect(s, (24, 32, 48), (26, 48, 44, 40), 3, border_radius=12)
    pygame.draw.circle(s, (206, 152, 114), (48, 31), 18)
    pygame.draw.arc(s, (34, 26, 22), (30, 12, 36, 24), 0, math.pi, 10)
    pygame.draw.rect(s, (20, 24, 32), (33, 26, 13, 8), border_radius=3)
    pygame.draw.rect(s, (20, 24, 32), (50, 26, 13, 8), border_radius=3)
    pygame.draw.line(s, (20, 24, 32), (46, 30), (50, 30), 3)
    pygame.draw.arc(s, (70, 38, 28), (42, 35, 12, 7), math.pi + 0.3, 2 * math.pi - 0.3, 2)
    pygame.draw.circle(s, (24, 32, 48), (48, 31), 18, 3)
    _salvar_alto(s, ARQUIVO_IMG_MORADOR_BAIXA_VISAO)


def _gerar_lixeira() -> None:
    """Gera lixeira urbana 2.5D elevada (48x64) com tampa abobadada e sombra."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 95), (20, 100, 68, 20))
    pygame.draw.rect(s, (74, 84, 98), (40, 88, 16, 22), border_radius=4)
    pygame.draw.rect(s, (18, 110, 62), (18, 46, 60, 56), border_radius=12)
    pygame.draw.rect(s, (38, 168, 100), (18, 44, 36, 54), border_radius=10)
    pygame.draw.rect(s, (18, 48, 30), (18, 44, 60, 58), 4, border_radius=12)
    pygame.draw.ellipse(s, (72, 206, 134), (14, 24, 68, 30))
    pygame.draw.ellipse(s, (18, 48, 30), (14, 24, 68, 30), 4)
    pygame.draw.ellipse(s, (20, 42, 30), (28, 33, 40, 12))
    for px in (34, 48, 62):
        pygame.draw.line(s, (14, 82, 48), (px, 60), (px, 92), 4)
    _salvar_alto(s, ARQUIVO_IMG_LIXEIRA)


def _gerar_poste() -> None:
    """Gera canteiro 2.5D elevado (48x64) com muro 3D, arbusto e luminária alta!"""
    s = _criar_tela_alto()
    pygame.draw.rect(s, (22, 18, 14, 80), (18, 56, 74, 66), border_radius=14)
    pygame.draw.rect(s, (112, 100, 90), (8, 64, 76, 54), border_radius=12)
    pygame.draw.rect(s, (168, 158, 144), (8, 44, 76, 42), border_radius=12)
    pygame.draw.rect(s, (84, 72, 62), (16, 52, 60, 26), border_radius=8)
    pygame.draw.rect(s, (52, 44, 38), (8, 44, 76, 74), 4, border_radius=12)
    pygame.draw.circle(s, (46, 118, 54), (32, 68), 17)
    pygame.draw.circle(s, (46, 118, 54), (62, 68), 17)
    pygame.draw.circle(s, (86, 178, 90), (30, 58), 14)
    pygame.draw.circle(s, (104, 198, 102), (58, 56), 14)
    pygame.draw.circle(s, (250, 204, 21), (26, 54), 4)
    pygame.draw.circle(s, (244, 114, 182), (62, 52), 4)
    pygame.draw.rect(s, (66, 78, 94), (42, 16, 12, 58), border_radius=5)
    pygame.draw.rect(s, (132, 146, 166), (42, 16, 5, 58), border_radius=3)
    pygame.draw.circle(s, (254, 240, 138, 110), (48, 18), 18)
    pygame.draw.circle(s, (254, 243, 176), (48, 18), 11)
    pygame.draw.arc(s, (36, 46, 62), (35, 5, 26, 20), 0, math.pi, 6)
    pygame.draw.circle(s, (36, 46, 62), (48, 18), 11, 3)
    _salvar_alto(s, ARQUIVO_IMG_POSTE)


def _gerar_aviso_sonoro() -> None:
    """Gera poste de alto-falante 2.5D elevado (48x64) com ondas sonoras."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 90), (22, 102, 60, 18))
    pygame.draw.rect(s, (92, 102, 116), (42, 62, 12, 48), border_radius=4)
    pygame.draw.rect(s, (184, 58, 14), (10, 24, 76, 58), border_radius=12)
    pygame.draw.rect(s, (249, 115, 22), (10, 16, 76, 54), border_radius=12)
    pygame.draw.polygon(
        s, (255, 255, 255), [(22, 34), (34, 34), (48, 22), (48, 60), (34, 48), (22, 48)]
    )
    pygame.draw.arc(s, (254, 240, 138), (44, 24, 22, 36), -math.pi / 3, math.pi / 3, 6)
    pygame.draw.arc(s, (254, 240, 138), (52, 18, 26, 48), -math.pi / 3, math.pi / 3, 6)
    pygame.draw.rect(s, (124, 45, 18), (10, 16, 76, 66), 4, border_radius=12)
    _salvar_alto(s, ARQUIVO_IMG_AVISO_SONORO)


def _gerar_painel_visual() -> None:
    """Gera totem de painel visual 2.5D elevado (48x64) com tela LED luminosa."""
    s = _criar_tela_alto()
    pygame.draw.ellipse(s, (22, 18, 14, 90), (22, 102, 60, 18))
    pygame.draw.rect(s, (148, 163, 184), (38, 72, 20, 38), border_radius=5)
    pygame.draw.rect(s, (12, 92, 118), (8, 18, 80, 62), border_radius=10)
    pygame.draw.rect(s, (16, 26, 44), (14, 22, 68, 48), border_radius=7)
    pygame.draw.rect(s, (56, 189, 248), (14, 22, 68, 48), 4, border_radius=7)
    pygame.draw.rect(s, (250, 204, 21), (22, 30, 52, 8), border_radius=3)
    pygame.draw.rect(s, (241, 245, 249), (22, 43, 38, 6), border_radius=3)
    pygame.draw.rect(s, (74, 222, 128), (22, 54, 46, 6), border_radius=3)
    pygame.draw.rect(s, (12, 62, 94), (8, 18, 80, 62), 4, border_radius=10)
    _salvar_alto(s, ARQUIVO_IMG_PAINEL_VISUAL)


def _gerar_degrau() -> None:
    """Gera degrau 2.5D (48x48) com espelhos verticais e pisos iluminados."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (22, 18, 14, 75), (8, 10, 86, 84), border_radius=10)
    pygame.draw.rect(s, (140, 74, 34), (4, 4, 86, 86), border_radius=10)
    pygame.draw.rect(s, (238, 164, 98), (8, 8, 78, 16))
    pygame.draw.rect(s, (148, 78, 36), (8, 24, 78, 10))
    pygame.draw.rect(s, (218, 138, 74), (8, 36, 78, 16))
    pygame.draw.rect(s, (122, 60, 26), (8, 52, 78, 10))
    pygame.draw.rect(s, (194, 114, 56), (8, 64, 78, 16))
    pygame.draw.rect(s, (96, 44, 18), (8, 80, 78, 6))
    pygame.draw.rect(s, (250, 204, 21), (8, 8, 78, 6))
    pygame.draw.rect(s, (58, 28, 12), (4, 4, 86, 86), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_DEGRAU)


def _gerar_buraco() -> None:
    """Gera cratera 2.5D (48x48) com parede da laje exposta e profundidade."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (214, 206, 190), (4, 4, 88, 88), border_radius=10)
    borda = [(16, 26), (44, 14), (78, 24), (84, 56), (64, 82), (26, 78), (12, 50)]
    parede_3d = [(22, 34), (46, 24), (72, 32), (76, 56), (60, 74), (30, 70), (20, 48)]
    fundo = [(28, 44), (48, 36), (68, 42), (70, 58), (54, 70), (34, 66), (26, 52)]
    pygame.draw.polygon(s, (144, 124, 108), borda)
    pygame.draw.polygon(s, (88, 70, 62), parede_3d)
    pygame.draw.polygon(s, (36, 30, 30), fundo)
    for p1, p2 in (
        ((16, 26), (6, 10)),
        ((78, 24), (88, 12)),
        ((64, 82), (82, 88)),
        ((26, 78), (10, 88)),
    ):
        pygame.draw.line(s, (78, 68, 62), p1, p2, 4)
    pygame.draw.rect(s, (92, 82, 74), (4, 4, 88, 88), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_BURACO)


def _gerar_rampa() -> None:
    """Gera rampa 2.5D inclinada azul com chanfro lateral e guias táteis."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (20, 92, 158), (4, 10, 88, 82), border_radius=10)
    pygame.draw.rect(s, (56, 168, 240), (8, 6, 80, 74), border_radius=8)
    pygame.draw.rect(s, (92, 194, 252), (12, 10, 72, 28), border_radius=6)
    pygame.draw.rect(s, (250, 204, 21), (8, 10, 8, 68))
    pygame.draw.rect(s, (250, 204, 21), (80, 10, 8, 68))
    seta = [(28, 44), (50, 24), (50, 36), (70, 36), (70, 52), (50, 52), (50, 64)]
    pygame.draw.polygon(s, (255, 255, 255), seta)
    pygame.draw.rect(s, (16, 60, 108), (4, 6, 88, 86), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_RAMPA)


def _gerar_piso_ok() -> None:
    """Gera piso nivelado 2.5D com visto branco."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (78, 152, 96), (4, 8, 88, 84), border_radius=10)
    pygame.draw.rect(s, (134, 208, 152), (8, 6, 80, 78), border_radius=8)
    pygame.draw.lines(s, (255, 255, 255), False, [(26, 48), (42, 64), (70, 30)], 8)
    pygame.draw.rect(s, (34, 102, 54), (4, 6, 88, 86), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_PISO_OK)


def _gerar_sem_piso_tatil() -> None:
    """Gera trecho sem piso tátil com marcador 2.5D."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (186, 178, 198), (4, 4, 88, 88), border_radius=10)
    pygame.draw.rect(s, (124, 58, 237), (8, 8, 80, 80), 6, border_radius=8)
    for py in (24, 48, 72):
        pygame.draw.line(s, (238, 222, 255), (20, py), (36, py), 6)
        pygame.draw.line(s, (238, 222, 255), (60, py), (76, py), 6)
    pygame.draw.circle(s, (68, 20, 110), (50, 52), 18)
    pygame.draw.circle(s, (108, 40, 168), (48, 46), 18)
    pygame.draw.circle(s, (250, 204, 21), (48, 46), 8)
    pygame.draw.rect(s, (59, 7, 100), (4, 4, 88, 88), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_SEM_PISO_TATIL)


def _gerar_piso_tatil() -> None:
    """Gera piso tátil direcional 2.5D em alto-relevo."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (180, 122, 8), (4, 8, 88, 84), border_radius=10)
    pygame.draw.rect(s, (250, 204, 21), (8, 6, 80, 78), border_radius=8)
    for py in (18, 34, 50, 66):
        pygame.draw.rect(s, (161, 98, 7), (16, py + 3, 64, 8), border_radius=4)
        pygame.draw.rect(s, (254, 246, 168), (16, py, 64, 6), border_radius=3)
    pygame.draw.rect(s, (113, 63, 18), (4, 6, 88, 86), 4, border_radius=10)
    _salvar_piso(s, ARQUIVO_IMG_PISO_TATIL)


def _gerar_destino() -> None:
    """Gera plataforma de chegada 2.5D com bandeira quadriculada."""
    s = _criar_tela_piso()
    pygame.draw.rect(s, (16, 108, 58), (4, 10, 88, 82), border_radius=12)
    pygame.draw.rect(s, (24, 156, 86), (4, 4, 88, 80), border_radius=12)
    bloco = 16
    for linha in range(4):
        for col in range(4):
            cor = (250, 252, 250) if (linha + col) % 2 == 0 else (18, 92, 52)
            pygame.draw.rect(s, cor, (16 + col * bloco, 12 + linha * bloco, bloco, bloco))
    pygame.draw.rect(s, (250, 204, 21), (4, 4, 88, 80), 6, border_radius=12)
    _salvar_piso(s, ARQUIVO_IMG_DESTINO)


def _salvar_wav(nome_arquivo: str, amostras: List[float]) -> None:
    """Grava amostras normalizadas [-1.0, 1.0] em WAV mono 16-bit."""
    caminho = caminho_arquivo(nome_arquivo)
    try:
        with wave.open(caminho, "w") as arquivo_wav:
            arquivo_wav.setnchannels(1)
            arquivo_wav.setsampwidth(2)
            arquivo_wav.setframerate(AUDIO_SAMPLE_RATE)
            frames = bytearray()
            for valor in amostras:
                limitado = max(-1.0, min(1.0, valor))
                frames.extend(struct.pack("<h", int(limitado * 32767)))
            arquivo_wav.writeframes(bytes(frames))
    except PermissionError:
        if not os.path.isfile(caminho):
            raise


def _gerar_tom(frequencia: float, duracao: float, amplitude: float = 0.48) -> List[float]:
    """Gera um tom senoidal suave com envelope de ataque e decaimento."""
    total_amostras = int(AUDIO_SAMPLE_RATE * duracao)
    amostras: List[float] = []
    for indice in range(total_amostras):
        tempo = indice / AUDIO_SAMPLE_RATE
        ataque = min(1.0, indice / max(1, int(total_amostras * 0.08)))
        decaimento = min(1.0, (total_amostras - indice) / max(1, int(total_amostras * 0.25)))
        onda = math.sin(2.0 * math.pi * frequencia * tempo)
        amostras.append(onda * amplitude * ataque * decaimento)
    return amostras


def _gerar_acorde_suave(
    frequencias: List[float],
    duracao: float,
    amplitude: float = 0.16,
) -> List[float]:
    """Gera um acorde instrumental calmo sem estalos."""
    total = int(AUDIO_SAMPLE_RATE * duracao)
    amostras: List[float] = []
    divisor = max(1, len(frequencias))
    for indice in range(total):
        tempo = indice / AUDIO_SAMPLE_RATE
        ataque = min(1.0, indice / max(1, int(total * 0.12)))
        decaimento = min(1.0, (total - indice) / max(1, int(total * 0.15)))
        envelope = ataque * decaimento
        soma = 0.0
        for freq in frequencias:
            soma += math.sin(2.0 * math.pi * freq * tempo) * 0.85
            soma += math.sin(2.0 * math.pi * (freq * 2.0) * tempo) * 0.15
        amostras.append((soma / divisor) * amplitude * envelope)
    return amostras


def _gerar_musica_fundo() -> None:
    """Gera trilha instrumental calma em loop sem estalo em data/musica.wav."""
    progressao = [
        [261.63, 329.63, 392.00, 493.88],
        [220.00, 261.63, 329.63, 392.00],
        [174.61, 220.00, 261.63, 329.63],
        [196.00, 246.94, 293.66, 329.63],
    ]
    trilha: List[float] = []
    for acorde in progressao:
        trilha.extend(_gerar_acorde_suave(acorde, duracao=2.0, amplitude=0.18))
    _salvar_wav(ARQUIVO_MUSICA_FUNDO, trilha)


def _gerar_audios() -> None:
    """Gera os quatro efeitos sonoros WAV e a trilha sonora calma em data/."""
    _salvar_wav(
        ARQUIVO_SOM_ACAO,
        _gerar_tom(523.25, 0.08, 0.45) + _gerar_tom(783.99, 0.12, 0.45),
    )
    _salvar_wav(
        ARQUIVO_SOM_ERRO,
        _gerar_tom(280.0, 0.12, 0.45) + _gerar_tom(210.0, 0.16, 0.45),
    )
    _salvar_wav(
        ARQUIVO_SOM_VITORIA,
        _gerar_tom(523.25, 0.10, 0.45)
        + _gerar_tom(659.25, 0.10, 0.45)
        + _gerar_tom(783.99, 0.10, 0.45)
        + _gerar_tom(1046.50, 0.22, 0.50),
    )
    _salvar_wav(ARQUIVO_SOM_CLIQUE, _gerar_tom(660.0, 0.05, 0.35))
    _gerar_musica_fundo()


def gerar_todos_assets() -> None:
    """Cria a pasta data/ e gera todos os sprites 2.5D elevados e áudios WAV."""
    os.makedirs(PASTA_DATA, exist_ok=True)
    pygame.init()
    try:
        _gerar_player()
        _gerar_morador_cadeirante()
        _gerar_morador_surdo()
        _gerar_morador_baixa_visao()
        _gerar_lixeira()
        _gerar_degrau()
        _gerar_buraco()
        _gerar_sem_piso_tatil()
        _gerar_piso_tatil()
        _gerar_aviso_sonoro()
        _gerar_painel_visual()
        _gerar_poste()
        _gerar_rampa()
        _gerar_piso_ok()
        _gerar_destino()
        _gerar_audios()
    finally:
        pygame.quit()


if __name__ == "__main__":
    gerar_todos_assets()
    print(f"Assets 2.5D elevados gerados com sucesso em: {PASTA_DATA}")
