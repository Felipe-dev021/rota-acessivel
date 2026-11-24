"""Gerador procedural de assets iniciais (sprites PNG 48x48 e áudios WAV).

Utiliza apenas pygame e a biblioteca padrão do Python (os, wave, struct, math)
para criar a pasta data/ e salvar os sprites com sombreamento sutil, contornos
nítidos e silhuetas reconhecíveis, além dos efeitos sonoros curtos em WAV.
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
    """Cria uma superfície transparente 48x48 px pronta para desenho.

    Returns:
        Superfície RGBA vazia com dimensões TILE x TILE.
    """
    return pygame.Surface((TILE, TILE), pygame.SRCALPHA)


def _gerar_player() -> None:
    """Gera o sprite de Alex (agente de acessibilidade com colete refletivo)."""
    surf = _criar_superficie()
    # Sombra suave projetada no piso
    pygame.draw.ellipse(surf, (15, 23, 42, 95), (9, 36, 30, 10))
    # Braços e ombros com contorno
    pygame.draw.circle(surf, (23, 74, 148), (11, 28), 5)
    pygame.draw.circle(surf, (23, 74, 148), (37, 28), 5)
    pygame.draw.circle(surf, (15, 34, 68), (11, 28), 5, 1)
    pygame.draw.circle(surf, (15, 34, 68), (37, 28), 5, 1)
    # Tronco e colete de alta visibilidade com sombreamento
    pygame.draw.rect(surf, (23, 74, 148), (13, 21, 22, 19), border_radius=6)
    pygame.draw.rect(surf, (250, 204, 21), (15, 22, 18, 16), border_radius=4)
    pygame.draw.rect(surf, (234, 179, 8), (15, 33, 18, 5), border_radius=2)
    # Faixas refletivas prateadas
    pygame.draw.rect(surf, (241, 245, 249), (15, 26, 18, 3))
    pygame.draw.rect(surf, (241, 245, 249), (15, 31, 18, 2))
    pygame.draw.rect(surf, (15, 23, 42), (13, 21, 22, 19), 2, border_radius=6)
    # Cabeça com iluminação sutil
    pygame.draw.circle(surf, (234, 186, 150), (24, 15), 9)
    pygame.draw.circle(surf, (245, 204, 172), (22, 13), 4)
    # Boné azul institucional
    pygame.draw.rect(surf, (29, 78, 216), (15, 6, 18, 6), border_radius=3)
    pygame.draw.rect(surf, (30, 58, 138), (14, 10, 20, 3), border_radius=1)
    # Olhos e contorno da cabeça
    pygame.draw.circle(surf, (15, 23, 42), (21, 15), 1)
    pygame.draw.circle(surf, (15, 23, 42), (27, 15), 1)
    pygame.draw.circle(surf, (15, 23, 42), (24, 15), 9, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PLAYER))


def _gerar_morador() -> None:
    """Gera o sprite do Morador em cadeira de rodas com silhueta bem definida."""
    surf = _criar_superficie()
    # Sombra no chão
    pygame.draw.ellipse(surf, (15, 23, 42, 100), (5, 36, 38, 10))
    # Rodas laterais com aro metálico
    pygame.draw.rect(surf, (30, 41, 59), (5, 12, 7, 26), border_radius=3)
    pygame.draw.rect(surf, (30, 41, 59), (36, 12, 7, 26), border_radius=3)
    pygame.draw.rect(surf, (203, 213, 225), (7, 15, 3, 20), border_radius=1)
    pygame.draw.rect(surf, (203, 213, 225), (38, 15, 3, 20), border_radius=1)
    # Estrutura da cadeira e apoio frontal de pés
    pygame.draw.rect(surf, (71, 85, 105), (14, 34, 20, 5), border_radius=2)
    pygame.draw.rect(surf, (37, 99, 235), (12, 13, 24, 22), border_radius=6)
    pygame.draw.rect(surf, (29, 78, 216), (12, 26, 24, 9), border_radius=4)
    pygame.draw.rect(surf, (15, 23, 42), (12, 13, 24, 22), 2, border_radius=6)
    # Pessoa (ombros + cabeça com destaque)
    pygame.draw.ellipse(surf, (219, 39, 119), (14, 17, 20, 14))
    pygame.draw.ellipse(surf, (131, 24, 67), (14, 17, 20, 14), 1)
    pygame.draw.circle(surf, (224, 172, 136), (24, 15), 7)
    pygame.draw.arc(surf, (45, 30, 22), (17, 8, 14, 12), 0, math.pi, 4)
    pygame.draw.circle(surf, (15, 23, 42), (24, 15), 7, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_MORADOR))


def _gerar_lixeira() -> None:
    """Gera o sprite de lixeira urbana bloqueando a faixa livre."""
    surf = _criar_superficie()
    pygame.draw.ellipse(surf, (15, 23, 42, 95), (8, 36, 32, 9))
    # Corpo verde com sombreamento lateral
    pygame.draw.rect(surf, (22, 130, 78), (10, 13, 28, 27), border_radius=6)
    pygame.draw.rect(surf, (16, 102, 60), (26, 13, 12, 27), border_radius=5)
    pygame.draw.rect(surf, (15, 48, 32), (10, 13, 28, 27), 2, border_radius=6)
    # Tampa superior com abertura
    pygame.draw.rect(surf, (52, 174, 114), (8, 7, 32, 10), border_radius=4)
    pygame.draw.rect(surf, (15, 48, 32), (8, 7, 32, 10), 2, border_radius=4)
    pygame.draw.rect(surf, (20, 36, 28), (16, 10, 16, 4), border_radius=2)
    # Frisos verticais
    for pos_x in (17, 24, 31):
        pygame.draw.line(surf, (14, 78, 46), (pos_x, 21), (pos_x, 36), 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_LIXEIRA))


def _gerar_degrau() -> None:
    """Gera o sprite de degrau/desnível abrupto com faixas de profundidade."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (154, 82, 38), (2, 2, 44, 44), border_radius=5)
    # Três níveis simulando sombra de degraus
    pygame.draw.rect(surf, (218, 138, 72), (4, 5, 40, 11))
    pygame.draw.rect(surf, (182, 100, 48), (4, 19, 40, 11))
    pygame.draw.rect(surf, (124, 62, 28), (4, 33, 40, 11))
    # Faixa de alerta amarela no topo
    pygame.draw.rect(surf, (250, 204, 21), (4, 4, 40, 4))
    # Linhas de quebra de nível bem marcadas
    pygame.draw.line(surf, (58, 26, 10), (4, 17), (44, 17), 3)
    pygame.draw.line(surf, (58, 26, 10), (4, 31), (44, 31), 3)
    pygame.draw.rect(surf, (58, 26, 10), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_DEGRAU))


def _gerar_buraco() -> None:
    """Gera o sprite de buraco irregular com rachaduras no pavimento."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (180, 184, 192), (2, 2, 44, 44), border_radius=5)
    poligono_borda = [(9, 14), (22, 7), (38, 13), (41, 28), (32, 40), (14, 38), (7, 25)]
    poligono_fundo = [(14, 18), (24, 12), (34, 18), (35, 28), (26, 35), (16, 33), (12, 24)]
    pygame.draw.polygon(surf, (96, 78, 68), poligono_borda)
    pygame.draw.polygon(surf, (34, 28, 30), poligono_fundo)
    # Rachaduras radiais nítidas
    for inicio, fim in (
        ((9, 14), (4, 6)),
        ((38, 13), (44, 7)),
        ((32, 40), (41, 44)),
        ((14, 38), (6, 44)),
    ):
        pygame.draw.line(surf, (58, 52, 56), inicio, fim, 2)
    pygame.draw.rect(surf, (66, 58, 62), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_BURACO))


def _gerar_poste() -> None:
    """Gera o sprite de poste estrutural fixo com base de concreto e coluna metálica."""
    surf = _criar_superficie()
    # Base de concreto fixa
    pygame.draw.rect(surf, (118, 126, 138), (5, 5, 38, 38), border_radius=6)
    pygame.draw.rect(surf, (88, 96, 108), (5, 28, 38, 15), border_radius=5)
    pygame.draw.rect(surf, (42, 48, 58), (5, 5, 38, 38), 2, border_radius=6)
    # Coluna circular metálica com reflexo
    pygame.draw.circle(surf, (62, 70, 82), (24, 24), 14)
    pygame.draw.circle(surf, (156, 166, 180), (24, 24), 10)
    pygame.draw.circle(surf, (226, 232, 240), (20, 20), 4)
    pygame.draw.circle(surf, (30, 41, 59), (24, 24), 14, 2)
    # Cantos sinalizando obstáculo fixo
    for p1, p2 in (
        ((9, 9), (14, 14)),
        ((39, 9), (34, 14)),
        ((9, 39), (14, 34)),
        ((39, 39), (34, 34)),
    ):
        pygame.draw.line(surf, (185, 28, 28), p1, p2, 2)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_POSTE))


def _gerar_rampa() -> None:
    """Gera o sprite de rampa acessível azul com guias táteis amarelas e seta."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (30, 122, 198), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (56, 162, 232), (6, 6, 36, 36), border_radius=3)
    # Faixas táteis laterais de alerta
    pygame.draw.rect(surf, (250, 204, 21), (4, 6, 4, 36))
    pygame.draw.rect(surf, (250, 204, 21), (40, 6, 4, 36))
    # Seta branca de acesso livre
    seta = [(14, 24), (25, 14), (25, 20), (35, 20), (35, 28), (25, 28), (25, 34)]
    pygame.draw.polygon(surf, (255, 255, 255), seta)
    pygame.draw.rect(surf, (15, 58, 108), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_RAMPA))


def _gerar_piso_ok() -> None:
    """Gera o sprite de pavimento nivelado e recuperado com visto de aprovação."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (112, 182, 128), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (144, 206, 158), (6, 6, 36, 36), border_radius=3)
    pygame.draw.lines(surf, (255, 255, 255), False, [(13, 25), (21, 33), (35, 16)], 4)
    pygame.draw.rect(surf, (36, 96, 52), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PISO_OK))


def _gerar_sem_piso_tatil() -> None:
    """Gera o sprite de trecho crítico sem sinalização tátil (acessibilidade visual)."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (152, 148, 168), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (124, 58, 237), (4, 4, 40, 40), 3, border_radius=4)
    # Contorno tracejado sugerindo ausência de piso tátil direcional
    for pos_y in (12, 24, 36):
        pygame.draw.line(surf, (233, 213, 255), (10, pos_y), (18, pos_y), 3)
        pygame.draw.line(surf, (233, 213, 255), (30, pos_y), (38, pos_y), 3)
    # Ponto de interrogação/alerta central
    pygame.draw.circle(surf, (88, 28, 135), (24, 24), 9)
    pygame.draw.circle(surf, (250, 204, 21), (24, 24), 4)
    pygame.draw.rect(surf, (59, 7, 100), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_SEM_PISO_TATIL))


def _gerar_piso_tatil() -> None:
    """Gera o sprite de piso tátil direcional amarelo conforme ABNT NBR 9050."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (234, 179, 8), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (250, 204, 21), (5, 5, 38, 38), border_radius=3)
    # Relevos direcionais paralelos característicos do piso tátil
    for pos_y in (11, 19, 27, 35):
        pygame.draw.rect(surf, (161, 98, 7), (8, pos_y, 32, 4), border_radius=2)
        pygame.draw.rect(surf, (254, 240, 138), (8, pos_y, 32, 2), border_radius=1)
    pygame.draw.rect(surf, (113, 63, 18), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PISO_TATIL))


def _gerar_aviso_sonoro() -> None:
    """Gera o sprite de ponto com aviso apenas sonoro (barreira para pessoas surdas)."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (217, 78, 18), (2, 2, 44, 44), border_radius=5)
    pygame.draw.rect(surf, (249, 115, 22), (5, 5, 38, 38), border_radius=3)
    # Silhueta de alto-falante branco + ondas sonoras
    pygame.draw.polygon(surf, (255, 255, 255), [(10, 19), (17, 19), (25, 12), (25, 36), (17, 29), (10, 29)])
    pygame.draw.arc(surf, (254, 240, 138), (22, 14, 12, 20), -math.pi / 3, math.pi / 3, 3)
    pygame.draw.arc(surf, (254, 240, 138), (26, 10, 14, 28), -math.pi / 3, math.pi / 3, 3)
    pygame.draw.rect(surf, (124, 45, 18), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_AVISO_SONORO))


def _gerar_painel_visual() -> None:
    """Gera o sprite de painel visual acessível (comunicação visual + sonora)."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (14, 116, 144), (2, 2, 44, 44), border_radius=5)
    # Tela informativa iluminada de alto contraste
    pygame.draw.rect(surf, (15, 23, 42), (6, 8, 36, 26), border_radius=4)
    pygame.draw.rect(surf, (56, 189, 248), (6, 8, 36, 26), 2, border_radius=4)
    # Linhas luminosas simulando texto acessível e ícone de visualização
    pygame.draw.rect(surf, (250, 204, 21), (10, 13, 28, 4), border_radius=1)
    pygame.draw.rect(surf, (241, 245, 249), (10, 20, 20, 3), border_radius=1)
    pygame.draw.rect(surf, (74, 222, 128), (10, 26, 24, 3), border_radius=1)
    # Base do totem informativo
    pygame.draw.rect(surf, (226, 232, 240), (19, 35, 10, 7), border_radius=2)
    pygame.draw.rect(surf, (12, 74, 110), (2, 2, 44, 44), 2, border_radius=5)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_PAINEL_VISUAL))


def _gerar_destino() -> None:
    """Gera o sprite do ponto de chegada com padrão quadriculado e borda dourada."""
    surf = _criar_superficie()
    pygame.draw.rect(surf, (22, 146, 80), (2, 2, 44, 44), border_radius=6)
    bloco = 8
    for linha in range(4):
        for col in range(4):
            cor = (248, 250, 252) if (linha + col) % 2 == 0 else (18, 86, 50)
            pygame.draw.rect(
                surf,
                cor,
                (8 + col * bloco, 8 + linha * bloco, bloco, bloco),
            )
    pygame.draw.rect(surf, (250, 204, 21), (2, 2, 44, 44), 3, border_radius=6)
    pygame.image.save(surf, caminho_arquivo(ARQUIVO_IMG_DESTINO))


def _salvar_wav(nome_arquivo: str, amostras: List[float]) -> None:
    """Grava uma lista de amostras normalizadas [-1.0, 1.0] em WAV mono 16-bit.

    Args:
        nome_arquivo: Nome do arquivo WAV dentro de data/.
        amostras: Lista de amplitudes em ponto flutuante entre -1.0 e 1.0.
    """
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
    """Gera um tom senoidal suave com envelope de ataque e decaimento.

    Args:
        frequencia: Frequência do tom em Hertz.
        duracao: Duração em segundos.
        amplitude: Amplitude máxima entre 0.0 e 1.0.

    Returns:
        Lista de amostras normalizadas.
    """
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
    """Gera um acorde instrumental calmo com ataque e decaimento sem estalos.

    Args:
        frequencias: Lista de frequências em Hz que compõem o acorde.
        duracao: Duração do acorde em segundos.
        amplitude: Amplitude total suave para música de fundo.

    Returns:
        Lista de amostras normalizadas entre -1.0 e 1.0.
    """
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
            # Fundamental + leve harmônico suave para timbre de piano elétrico
            soma += math.sin(2.0 * math.pi * freq * tempo) * 0.85
            soma += math.sin(2.0 * math.pi * (freq * 2.0) * tempo) * 0.15
        amostras.append((soma / divisor) * amplitude * envelope)
    return amostras


def _gerar_musica_fundo() -> None:
    """Gera uma trilha instrumental calma em loop sem estalo em data/musica.wav."""
    # Progressão calma e acolhedora: Cmaj7 -> Am7 -> Fmaj7 -> G6 (8 segundos em loop)
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
    # acao.wav: confirmação positiva em dois tons ascendentes
    som_acao = _gerar_tom(523.25, 0.08, 0.45) + _gerar_tom(783.99, 0.12, 0.45)
    _salvar_wav(ARQUIVO_SOM_ACAO, som_acao)

    # erro.wav: alerta grave descendente
    som_erro = _gerar_tom(280.0, 0.12, 0.5) + _gerar_tom(195.0, 0.18, 0.5)
    _salvar_wav(ARQUIVO_SOM_ERRO, som_erro)

    # vitoria.wav: arpejo maior alegre de conclusão
    som_vitoria = (
        _gerar_tom(523.25, 0.10, 0.45)
        + _gerar_tom(659.25, 0.10, 0.45)
        + _gerar_tom(783.99, 0.10, 0.45)
        + _gerar_tom(1046.50, 0.22, 0.50)
    )
    _salvar_wav(ARQUIVO_SOM_VITORIA, som_vitoria)

    # clique.wav: clique neutro para menus e alternâncias
    som_clique = _gerar_tom(660.0, 0.05, 0.35)
    _salvar_wav(ARQUIVO_SOM_CLIQUE, som_clique)

    # musica.wav: trilha instrumental calma em loop
    _gerar_musica_fundo()


def gerar_todos_assets() -> None:
    """Cria a pasta data/ e gera todos os sprites PNG e áudios WAV do jogo."""
    os.makedirs(PASTA_DATA, exist_ok=True)
    pygame.init()
    try:
        _gerar_player()
        _gerar_morador()
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
    print(f"Assets iniciais gerados com sucesso em: {PASTA_DATA}")
