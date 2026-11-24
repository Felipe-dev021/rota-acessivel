"""Módulo da entidade jogável Alex (agente de acessibilidade) de 'Rota Acessível'.

Implementa a classe Jogador (herdeira de pygame.sprite.Sprite) com movimento
contínuo em 8 direções normalizado por vetor, física em float + dt, colisão
separada por eixo com hitbox reduzida usando pygame.sprite.spritecollide() e
detecção de barreiras alteráveis dentro do raio de interação.
"""

import math
from typing import Iterable, Optional

import pygame

from barreira import Barreira
from config import (
    ALTURA,
    ARQUIVO_IMG_PLAYER,
    CORES_ALTO_CONTRASTE,
    FONTE_FAMILIA,
    FONTES_GRANDE,
    FONTES_NORMAL,
    HITBOX_JOGADOR_MARGEM,
    HUD_ALTURA,
    LARGURA,
    RAIO_INTERACAO,
    TILE,
    VELOCIDADE_JOGADOR,
    caminho_arquivo,
)


class Jogador(pygame.sprite.Sprite):
    """Controla Alex, o agente de acessibilidade que percorre e adapta a via urbana."""

    def __init__(
        self,
        coluna: int,
        linha: int,
        grupo_solidos: Optional[pygame.sprite.Group] = None,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Inicializa Alex na célula informada da grade urbana.

        Args:
            coluna: Coluna inicial na grade (0 a COLS - 1).
            linha: Linha inicial na grade (0 a ROWS - 1).
            grupo_solidos: Grupo de sprites sólidos (postes fixos) para colisão.
            modo_alto_contraste: Define o estilo visual inicial.
            fonte_grande: Define a escala de fonte da sigla no alto contraste.
        """
        super().__init__()
        self.pos_x: float = float(coluna * TILE)
        self.pos_y: float = float(HUD_ALTURA + linha * TILE)
        self.grupo_solidos: pygame.sprite.Group = (
            grupo_solidos if grupo_solidos is not None else pygame.sprite.Group()
        )
        self.movimento_habilitado: bool = True

        self._imagem_normal: pygame.Surface = self._carregar_sprite()
        self.image: pygame.Surface = self._imagem_normal.copy()
        self.rect: pygame.Rect = self.image.get_rect(
            topleft=(round(self.pos_x), round(self.pos_y))
        )
        self.atualizar_visual(modo_alto_contraste, fonte_grande)

    def _carregar_sprite(self) -> pygame.Surface:
        """Carrega player.png a partir de data/ usando caminho_arquivo().

        Returns:
            Superfície pygame redimensionada para TILE x TILE.
        """
        superficie = pygame.image.load(caminho_arquivo(ARQUIVO_IMG_PLAYER))
        if pygame.display.get_surface() is not None:
            superficie = superficie.convert_alpha()
        if superficie.get_size() != (TILE, TILE):
            superficie = pygame.transform.smoothscale(superficie, (TILE, TILE))
        return superficie

    def definir_grupo_solidos(self, grupo_solidos: pygame.sprite.Group) -> None:
        """Vincula o grupo de obstáculos sólidos da fase atual para colisão.

        Args:
            grupo_solidos: Grupo contendo os sprites sólidos (postes fixos).
        """
        self.grupo_solidos = grupo_solidos

    def atualizar_visual(
        self,
        modo_alto_contraste: bool,
        fonte_grande: bool = False,
    ) -> None:
        """Alterna o visual de Alex entre sprite padrão e modo alto contraste.

        Args:
            modo_alto_contraste: True desenha círculo de alto contraste com 'A'.
            fonte_grande: True amplia a letra identificadora no alto contraste.
        """
        if not modo_alto_contraste:
            self.image = self._imagem_normal.copy()
        else:
            superficie = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.circle(
                superficie,
                CORES_ALTO_CONTRASTE["destaque_e"],
                (TILE // 2, TILE // 2),
                TILE // 2 - 4,
            )
            pygame.draw.circle(
                superficie,
                CORES_ALTO_CONTRASTE["tile_borda"],
                (TILE // 2, TILE // 2),
                TILE // 2 - 4,
                3,
            )
            escala = FONTES_GRANDE if fonte_grande else FONTES_NORMAL
            fonte = pygame.font.SysFont(FONTE_FAMILIA, escala["sigla"], bold=True)
            sigla = fonte.render("A", True, CORES_ALTO_CONTRASTE["destaque_e_texto"])
            superficie.blit(sigla, sigla.get_rect(center=(TILE // 2, TILE // 2)))
            self.image = superficie

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def _obter_hitbox(self, pos_x: float, pos_y: float) -> pygame.Rect:
        """Retorna a hitbox reduzida para deslizar suavemente nas quinas dos postes.

        Args:
            pos_x: Coordenada X candidata em float.
            pos_y: Coordenada Y candidata em float.

        Returns:
            Retângulo de colisão centralizado e reduzido por HITBOX_JOGADOR_MARGEM.
        """
        margem = HITBOX_JOGADOR_MARGEM
        return pygame.Rect(
            round(pos_x) + margem,
            round(pos_y) + margem,
            TILE - 2 * margem,
            TILE - 2 * margem,
        )

    def _colide_com_solidos(self, pos_x: float, pos_y: float) -> bool:
        """Verifica colisão com grupo_solidos usando pygame.sprite.spritecollide().

        Args:
            pos_x: Posição X candidata em float.
            pos_y: Posição Y candidata em float.

        Returns:
            True se a hitbox reduzida colidir com algum sprite sólido.
        """
        hitbox = self._obter_hitbox(pos_x, pos_y)
        colisoes = pygame.sprite.spritecollide(
            self,
            self.grupo_solidos,
            False,
            collided=lambda _jogador, solido: hitbox.colliderect(solido.rect),
        )
        return len(colisoes) > 0

    def update(self, dt: float) -> None:
        """Atualiza Alex com movimento contínuo em 8 direções, limites e colisão.

        Lê pygame.key.get_pressed(), normaliza o vetor de direção para manter a
        velocidade constante na diagonal, aplica VELOCIDADE_JOGADOR * dt em
        float e resolve colisão nos eixos X e Y separadamente.

        Args:
            dt: Tempo decorrido em segundos desde o último frame.
        """
        if not self.movimento_habilitado:
            return

        teclas = pygame.key.get_pressed()
        direcao = pygame.math.Vector2(0.0, 0.0)

        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            direcao.x -= 1.0
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            direcao.x += 1.0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            direcao.y -= 1.0
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            direcao.y += 1.0

        if direcao.length_squared() > 0.0:
            direcao = direcao.normalize()

        # Movimento e colisão no eixo X
        candidato_x = self.pos_x + direcao.x * VELOCIDADE_JOGADOR * dt
        candidato_x = max(0.0, min(float(LARGURA - TILE), candidato_x))
        if not self._colide_com_solidos(candidato_x, self.pos_y):
            self.pos_x = candidato_x

        # Movimento e colisão no eixo Y (área jogável abaixo do HUD: y >= HUD_ALTURA)
        candidato_y = self.pos_y + direcao.y * VELOCIDADE_JOGADOR * dt
        candidato_y = max(float(HUD_ALTURA), min(float(ALTURA - TILE), candidato_y))
        if not self._colide_com_solidos(self.pos_x, candidato_y):
            self.pos_y = candidato_y

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def obter_barreira_proxima(
        self,
        grupo_barreiras: Iterable[Barreira],
    ) -> Optional[Barreira]:
        """Retorna a barreira alterável não resolvida mais próxima dentro do raio.

        Args:
            grupo_barreiras: Grupo ou coleção de sprites Barreira da fase atual.

        Returns:
            Barreira alterável mais próxima dentro de RAIO_INTERACAO pixels, ou None.
        """
        centro_x = self.pos_x + TILE / 2.0
        centro_y = self.pos_y + TILE / 2.0

        mais_proxima: Optional[Barreira] = None
        menor_distancia = RAIO_INTERACAO

        for barreira in grupo_barreiras:
            if not isinstance(barreira, Barreira) or not barreira.alteravel:
                continue
            bx, by = barreira.centro()
            distancia = math.hypot(bx - centro_x, by - centro_y)
            if distancia <= menor_distancia:
                menor_distancia = distancia
                mais_proxima = barreira

        return mais_proxima

    def reposicionar(self, coluna: int, linha: int) -> None:
        """Posiciona Alex diretamente na célula (coluna, linha) da grade.

        Args:
            coluna: Coluna alvo na grade.
            linha: Linha alvo na grade.
        """
        self.pos_x = float(coluna * TILE)
        self.pos_y = float(HUD_ALTURA + linha * TILE)
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))
