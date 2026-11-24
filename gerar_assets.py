"""Gerador procedural de assets cartoon 2D (sprites PNG 48x48 e áudios WAV).

Utiliza apenas pygame e a biblioteca padrão do Python (os, wave, struct, math)
para criar a pasta data/ e salvar os sprites de Alex, dos 3 perfis reais de
moradores (cadeirante, pessoa surda e pessoa com baixa visão/bengala branca),
das barreiras urbanas e dos efeitos sonoros + trilha calma em WAV.
"""

import math
import os
import struct
import wave
from typing import List

import pygame

from config import (
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


def _criar_superficie() -> pygame.Surface:
    """Cria uma superfície transparente 48x48 px pronta para desenho cartoon."""
    return pygame.Surface((TILE, TILE), pygame.SRCALPHA)


def _gerar_player() -> None:
    """Gera o sprite de Alex (agente urbano com colete de alta visibilidade)."""
    surf = _criar_superficie()
    # Sombra macia no piso
    pygame.draw.ellipse(surf, (38, 32, 26, 85), (9, 36, 30, 10))
    # Tênis / pés
    pygame.draw.ellipse(surf, (35, 48, 68), (14, 36, 9, 6))
    pygame.draw.ellipse(surf, (35, 48, 68), (25, 36, 9, 6))
    # Braços
    pygame.draw.circle(surf, (37, 99, 235), (11, 28), 5)
    pygame.draw.circle(surf, (37, 99, 235), (37, 28), 5)
    pygame.draw.circle(surf, (24, 34, 52), (11, 28), 5, 2)
    pygame.draw.circle(surf, (24, 34, 52), (37, 28), 5, 2)
    # Tronco + colete amarelo vibrante
    pygame.draw.rect(surf, (37, 99, 235), (13, 21, 22, 18), border_radius=7)
    pygame.draw.rect(surf, (250, 204, 21), (15, 22, 18, 15), border_radius=5)
    pygame.draw.rect(surf, (241, 245, 249), (15, 27, 18, 3))
    pygame.draw.rect(surf, (241, 245, 249), (15, 32, 18, 2))
    pygame.draw.rect(surf, (24, 34, 52), (13, 21, 22, 18), 2, border_radius=7)
    # Cabeça expressiva
    pygame.draw.circle(surf, (238, 190, 154), (24, 15), 9)
    pygame.draw.circle(surf, (248, 210, 180), (22, 13), 4)
    # Boné azul com aba lateral (ajuda a perceber direção)
    pygame.draw.rect(surf, (29, 78, 216), (15, 5, 18, 7), border_radius=4)
    pygame.draw.rect(surf, (30, 58, 138), (18, 9, 17, 3), border_radius=2)
    # Olhos + sorriso discreto
    pygame.draw.circle(surf, (24, 28, 36), (22, 15), 1)
    pygame.draw.circle(surf, (24, 28, 36), (28, 15), 1)
    pygame.draw.circle(surf, (24, 34, 52), (24, 15), 9, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PLAYER))


def _gerar_morador_cadeirante() -> None:
    """Gera o sprite de Clara/Lucas (morador em cadeira de rodas — Fases 1 e 2)."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (38, 32, 26, 90), (5, 36, 38, 10))
    # Rodas laterais grandes
    pygame.draw.rect(surf, (30, 41, 59), (5, 12, 7, 26), border_radius=3)
    pygame.draw.rect(surf, (30, 41, 59), (36, 12, 7, 26), border_radius=3)
    pygame.draw.rect(surf, (203, 213, 225), (7, 15, 3, 20), border_radius=1)
    pygame.draw.rect(surf, (203, 213, 225), (38, 15, 3, 20), border_radius=1)
    # Estrutura da cadeira e apoio frontal
    pygame.draw.rect(surf, (71, 85, 105), (14, 34, 20, 5), border_radius=2)
    pygame.draw.rect(surf, (37, 99, 235), (12, 13, 24, 22), border_radius=6)
    pygame.draw.rect(surf, (24, 34, 52), (12, 13, 24, 22), 2, border_radius=6)
    # Pessoa (camisa rosa-vinho + cabeça)
    pygame.draw.ellipse(surf, (219, 39, 119), (14, 17, 20, 14))
    pygame.draw.circle(surf, (226, 174, 138), (24, 15), 7)
    pygame.draw.arc(surf, (58, 36, 26), (17, 8, 14, 12), 0, math.pi, 4)
    pygame.draw.circle(surf, (24, 34, 52), (24, 15), 7, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_MORADOR))


def _gerar_morador_surdo() -> None:
    """Gera o sprite de Sofia (moradora surda a pé — Fase 3, sem cadeira de rodas)."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (38, 32, 26, 85), (10, 36, 28, 10))
    # Pés
    pygame.draw.ellipse(surf, (44, 54, 68), (15, 36, 8, 6))
    pygame.draw.ellipse(surf, (44, 54, 68), (25, 36, 8, 6))
    # Braços (um ligeiramente erguido em gesto de comunicação)
    pygame.draw.circle(surf, (13, 148, 136), (11, 27), 5)
    pygame.draw.circle(surf, (13, 148, 136), (37, 24), 5)
    pygame.draw.circle(surf, (24, 34, 52), (11, 27), 5, 2)
    pygame.draw.circle(surf, (24, 34, 52), (37, 24), 5, 2)
    # Blusa turquesa vibrante + lenço coral
    pygame.draw.rect(surf, (13, 148, 136), (14, 21, 20, 18), border_radius=7)
    pygame.draw.rect(surf, (249, 115, 22), (17, 21, 14, 5), border_radius=3)
    pygame.draw.rect(surf, (24, 34, 52), (14, 21, 20, 18), 2, border_radius=7)
    # Cabelo castanho + cabeça
    pygame.draw.circle(surf, (78, 46, 30), (24, 14), 10)
    pygame.draw.circle(surf, (236, 186, 150), (24, 15), 8)
    # Aparelho auditivo/implante discreto azul-claro na lateral
    pygame.draw.circle(surf, (56, 189, 248), (32, 15), 3)
    pygame.draw.circle(surf, (24, 34, 52), (24, 15), 8, 2)
    # Olhos
    pygame.draw.circle(surf, (24, 28, 36), (21, 15), 1)
    pygame.draw.circle(surf, (24, 28, 36), (27, 15), 1)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_MORADOR_SURDO))


def _gerar_morador_baixa_visao() -> None:
    """Gera o sprite de Mateus (morador com baixa visão e bengala branca — Fase 4)."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (38, 32, 26, 85), (10, 36, 28, 10))
    # Pés
    pygame.draw.ellipse(surf, (44, 54, 68), (15, 36, 8, 6))
    pygame.draw.ellipse(surf, (44, 54, 68), (25, 36, 8, 6))
    # Bengala branca direcional com ponta vermelha na frente
    pygame.draw.line(surf, (24, 34, 52), (33, 27), (44, 42), 5)
    pygame.draw.line(surf, (255, 255, 255), (33, 27), (43, 41), 3)
    pygame.draw.circle(surf, (220, 38, 38), (44, 42), 3)
    # Braços e casaco roxo-índigo
    pygame.draw.circle(surf, (99, 102, 241), (11, 28), 5)
    pygame.draw.circle(surf, (99, 102, 241), (35, 28), 5)
    pygame.draw.circle(surf, (24, 34, 52), (11, 28), 5, 2)
    pygame.draw.circle(surf, (24, 34, 52), (35, 28), 5, 2)
    pygame.draw.rect(surf, (99, 102, 241), (14, 21, 20, 18), border_radius=7)
    pygame.draw.rect(surf, (250, 204, 21), (21, 22, 6, 15), border_radius=2)
    pygame.draw.rect(surf, (24, 34, 52), (14, 21, 20, 18), 2, border_radius=7)
    # Cabeça + óculos escuros de proteção visual
    pygame.draw.circle(surf, (198, 144, 108), (24, 15), 8)
    pygame.draw.arc(surf, (30, 24, 20), (16, 7, 16, 11), 0, math.pi, 4)
    pygame.draw.rect(surf, (20, 24, 32), (17, 13, 6, 4), border_radius=1)
    pygame.draw.rect(surf, (20, 24, 32), (25, 13, 6, 4), border_radius=1)
    pygame.draw.line(surf, (20, 24, 32), (23, 15), (25, 15), 2)
    pygame.draw.circle(surf, (24, 34, 52), (24, 15), 8, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_MORADOR_BAIXA_VISAO))


def _gerar_lixeira() -> None:
    """Gera o sprite cartoon de lixeira urbana bloqueando a faixa livre."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (38, 32, 26, 85), (8, 36, 32, 9))
    pygame.draw.rect(surf, (28, 148, 88), (10, 13, 28, 27), border_radius=6)
    pygame.draw.rect(surf, (20, 116, 68), (26, 13, 12, 27), border_radius=5)
    pygame.draw.rect(surf, (24, 48, 34), (10, 13, 28, 27), 2, border_radius=6)
    pygame.draw.rect(surf, (56, 186, 120), (8, 7, 32, 10), border_radius=4)
    pygame.draw.rect(surf, (24, 48, 34), (8, 7, 32, 10), 2, border_radius=4)
    pygame.draw.rect(surf, (20, 36, 28), (16, 10, 16, 4), border_radius=2)
    for pos_x in (17, 24, 31):
        pygame.draw.line(surf, (16, 86, 50), (pos_x, 21), (pos_x, 36), 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_LIXEIRA))


def _gerar_degrau() -> None:
    """Gera o sprite de degrau abrupto sem rebaixamento."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (166, 92, 46), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (226, 148, 82), (4, 5, 40, 11))
    pygame.draw.rect(surf, (192, 110, 54), (4, 19, 40, 11))
    pygame.draw.rect(surf, (136, 70, 32), (4, 33, 40, 11))
    pygame.draw.rect(surf, (250, 204, 21), (4, 4, 40, 4))
    pygame.draw.line(surf, (58, 28, 12), (4, 17), (44, 17), 3)
    pygame.draw.line(surf, (58, 28, 12), (4, 31), (44, 31), 3)
    pygame.draw.rect(surf, (58, 28, 12), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_DEGRAU))


def _gerar_buraco() -> None:
    """Gera o sprite de buraco irregular no pavimento."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (196, 188, 174), (2, 2, 44, 44), border_radius=5)
    poligono_borda = [(9, 14), (22, 7), (38, 13), (41, 28), (32, 40), (14, 38), (7, 25)]
    poligono_fundo = [(14, 18), (24, 12), (34, 18), (35, 28), (26, 35), (16, 33), (12, 24)]
    pygame.draw.polygon(surf, (112, 92, 78), poligono_borda)
    pygame.draw.polygon(surf, (44, 36, 36), poligono_fundo)
    for inicio, fim in (
        ((9, 14), (4, 6)),
        ((38, 13), (44, 7)),
        ((32, 40), (41, 44)),
        ((14, 38), (6, 44)),
    ):
        pygame.draw.line(surf, (68, 58, 56), inicio, fim, 2)
    pygame.draw.rect(surf, (78, 68, 64), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_BURACO))


def _gerar_poste() -> None:
    """Gera o sprite de poste/canteiro fixo arborizado (estilo orla de Maricá)."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (38, 32, 26, 75), (6, 36, 36, 9))
    # Floreira/base de concreto fixa com borda arredondada
    pygame.draw.rect(surf, (132, 124, 114), (5, 7, 38, 34), border_radius=8)
    pygame.draw.rect(surf, (96, 88, 80), (5, 28, 38, 13), border_radius=6)
    pygame.draw.rect(surf, (46, 40, 36), (5, 7, 38, 34), 2, border_radius=8)
    # Folhagem verde decorativa na base + coluna metálica do poste no centro
    pygame.draw.circle(surf, (68, 142, 74), (15, 22), 7)
    pygame.draw.circle(surf, (84, 164, 88), (33, 22), 7)
    pygame.draw.circle(surf, (76, 152, 80), (24, 30), 7)
    pygame.draw.circle(surf, (58, 68, 82), (24, 21), 10)
    pygame.draw.circle(surf, (176, 186, 200), (24, 21), 7)
    pygame.draw.circle(surf, (242, 246, 252), (22, 19), 3)
    pygame.draw.circle(surf, (30, 38, 48), (24, 21), 10, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_POSTE))


def _gerar_rampa() -> None:
    """Gera o sprite de rampa acessível azul com guias táteis amarelas."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (30, 126, 202), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (58, 166, 236), (6, 6, 36, 36), border_radius=3)
    pygame.draw.rect(surf, (250, 204, 21), (4, 6, 4, 36))
    pygame.draw.rect(surf, (250, 204, 21), (40, 6, 4, 36))
    seta = [(14, 24), (25, 14), (25, 20), (35, 20), (35, 28), (25, 28), (25, 34)]
    pygame.draw.polygon(surf, (255, 255, 255), seta)
    pygame.draw.rect(surf, (16, 62, 110), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_RAMPA))


def _gerar_piso_ok() -> None:
    """Gera o sprite de pavimento nivelado com visto branco."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (112, 186, 130), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (146, 210, 162), (6, 6, 36, 36), border_radius=3)
    pygame.draw.lines(surf, (255, 255, 255), False, [(13, 25), (21, 33), (35, 16)], 4)
    pygame.draw.rect(surf, (36, 98, 54), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PISO_OK))


def _gerar_sem_piso_tatil() -> None:
    """Gera o sprite de trecho crítico sem piso tátil direcional."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (176, 168, 188), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (124, 58, 237), (4, 4, 40, 40), 3, border_radius=4)
    for pos_y in (12, 24, 36):
        pygame.draw.line(surf, (233, 213, 255), (10, pos_y), (18, pos_y), 3)
        pygame.draw.line(surf, (233, 213, 255), (30, pos_y), (38, pos_y), 3)
    pygame.draw.circle(surf, (88, 28, 135), (24, 24), 9)
    pygame.draw.circle(surf, (250, 204, 21), (24, 24), 4)
    pygame.draw.rect(surf, (59, 7, 100), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_SEM_PISO_TATIL))


def _gerar_piso_tatil() -> None:
    """Gera o sprite de piso tátil direcional amarelo (ABNT NBR 9050)."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (234, 179, 8), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (250, 204, 21), (5, 5, 38, 38), border_radius=3)
    for pos_y in (11, 19, 27, 35):
        pygame.draw.rect(surf, (161, 98, 7), (8, pos_y, 32, 4), border_radius=2)
        pygame.draw.rect(surf, (254, 240, 138), (8, pos_y, 32, 2), border_radius=1)
    pygame.draw.rect(surf, (113, 63, 18), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PISO_TATIL))


def _gerar_aviso_sonoro() -> None:
    """Gera o sprite de alto-falante com aviso exclusivamente sonoro."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (217, 78, 18), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (249, 115, 22), (5, 5, 38, 38), border_radius=3)
    pygame.draw.polygon(
        surf,
        (255, 255, 255),
        [(10, 19), (17, 19), (25, 12), (25, 36), (17, 29), (10, 29)],
    )
    pygame.draw.arc(surf, (254, 240, 138), (22, 14, 12, 20), -math.pi / 3, math.pi / 3, 3)
    pygame.draw.arc(surf, (254, 240, 138), (26, 10, 14, 28), -math.pi / 3, math.pi / 3, 3)
    pygame.draw.rect(surf, (124, 45, 18), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_AVISO_SONORO))


def _gerar_painel_visual() -> None:
    """Gera o sprite de painel visual acessível (comunicação visual + sonora)."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (14, 116, 144), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (15, 23, 42), (6, 8, 36, 26), border_radius=4)
    pygame.draw.rect(surf, (56, 189, 248), (6, 8, 36, 26), 2, border_radius=4)
    pygame.draw.rect(surf, (250, 204, 21), (10, 13, 28, 4), border_radius=1)
    pygame.draw.rect(surf, (241, 245, 249), (10, 20, 20, 3), border_radius=1)
    pygame.draw.rect(surf, (74, 222, 128), (10, 26, 24, 3), border_radius=1)
    pygame.draw.rect(surf, (226, 232, 240), (19, 35, 10, 7), border_radius=2)
    pygame.draw.rect(surf, (12, 74, 110), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PAINEL_VISUAL))


def _gerar_destino() -> None:
    """Gera o sprite do ponto de chegada acessível com bandeira quadriculada."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (22, 148, 82), (2, 2, 44, 44), border_radius=6)
    bloco = 8
    for linha in range(4):
        for col in range(4):
            cor = (248, 250, 252) if (linha + col) % 2 == 0 else (18, 86, 50)
            pygame.draw.rect(
                surf, cor, (8 + col * bloco, 8 + linha * bloco, bloco, bloco)
            )
    pygame.draw.rect(surf, (250, 204, 21), (2, 2, 44, 44), 3, border_radius=6)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_DESTINO))


def _salvar_wav(nome_arquivo: str, amostras: List[float]) -> None:
    """Grava uma lista de amostras normalizadas [-1.0, 1.0] em WAV mono 16-bit."""
    caminho = caminho_arquivo(nome_arquivo)
    with wave.open(caminho, "w") as arquivo_wav:
        arquivo_wav.setnchannels(1)
        arquivo_wav.setsampwidth(2)
        arquivo_wav.setframerate(AUDIO_SAMPLE_RATE)
        frames = bytearray()
        for valor in amostras:
            limitado = max(-1.0, min(1.0, valor))
            frames.extend(struct.pack("<h", int(limitado * 32767)))
        arquivo_wav.writeframes(bytes(frames))


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
    """Gera um acorde instrumental calmo com ataque e decaimento sem estalos."""
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
    """Gera uma trilha instrumental calma em loop sem estalo em data/musica.wav."""
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
        _gerar_tom(280.0, 0.12, 0.5) + _gerar_tom(195.0, 0.18, 0.5),
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
    """Cria a pasta data/ e gera todos os sprites PNG e áudios WAV do jogo."""
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
    print(f"Assets cartoon gerados com sucesso em: {PASTA_DATA}")
