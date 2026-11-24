"""Módulo da entidade jogável Alex (agente de acessibilidade de Maricá/RJ).

Implementa a classe Jogador (herdeira de pygame.sprite.Sprite) com resposta
imediata em 8 direções, corrida ágil segurando SHIFT (Sprint), deslizamento
automático suave em quinas (corner-nudging), animação leve de passos e detecção
de barreiras alteráveis dentro do raio de interação.
"""

import math
from typing import Iterable, Optional

import pygame

from barreira import Barreira
from config import (
    ALTURA,
    ARQUIVO_IMG_PLAYER,
    CORES_ALTO_CONTRASTE,
    CORNER_NUDGE_MAX,
    FONTE_FAMILIA,
    FONTES_GRANDE,
    FONTES_NORMAL,
    HITBOX_JOGADOR_MARGEM,
    HUD_ALTURA,
    LARGURA,
    RAIO_INTERACAO,
    TILE,
    VELOCIDADE_JOGADOR,
    VELOCIDADE_SPRINT,
    caminho_arquivo,
)


class Jogador(pygame.sprite.Sprite):
    """Controla Alex, o agente urbano que percorre e adapta as calçadas de Maricá."""

    def __init__(
        self,
        coluna: int,
        linha: int,
        grupo_solidos: Optional[pygame.sprite.Group] = None,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Inicializa Alex na célula informada da calçada."""
        super().__init__()
        self.pos_x: float = float(coluna * TILE)
        self.pos_y: float = float(HUD_ALTURA + linha * TILE)
        self.tempo_passo: float = 0.0
        self.olhando_esquerda: bool = False
        self.andando: bool = False
        self.correndo: bool = False
        self.modo_alto_contraste: bool = modo_alto_contraste
        self.fonte_grande: bool = fonte_grande

        self.grupo_solidos: pygame.sprite.Group = (
            grupo_solidos if grupo_solidos is not None else pygame.sprite.Group()
        )
        self.movimento_habilitado: bool = True

        self._img_dir: pygame.Surface = self._carregar_sprite()
        self._img_esq: pygame.Surface = pygame.transform.flip(self._img_dir, True, False)
        self._img_alto_contraste: pygame.Surface = self._criar_sprite_alto_contraste(
            fonte_grande
        )
        self.image: pygame.Surface = self._img_dir
        self.rect: pygame.Rect = self.image.get_rect(
            topleft=(round(self.pos_x), round(self.pos_y))
        )
        self.atualizar_visual(modo_alto_contraste, fonte_grande)

    def _carregar_sprite(self) -> pygame.Surface:
        """Carrega player.png a partir de data/ usando caminho_arquivo()."""
        superficie = pygame.image.load(caminho_arquivo(ARQUIVO_IMG_PLAYER))
        if pygame.display.get_surface() is not None:
            superficie = superficie.convert_alpha()
        if superficie.get_size() != (TILE, TILE):
            superficie = pygame.transform.smoothscale(superficie, (TILE, TILE))
        return superficie

    def _criar_sprite_alto_contraste(self, fonte_grande: bool) -> pygame.Surface:
        """Gera em cache o sprite circular de alto contraste com a sigla 'A'."""
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
            4,
        )
        escala = FONTES_GRANDE if fonte_grande else FONTES_NORMAL
        fonte = pygame.font.SysFont(FONTE_FAMILIA, escala["sigla"], bold=True)
        sigla = fonte.render("A", True, CORES_ALTO_CONTRASTE["destaque_e_texto"])
        superficie.blit(sigla, sigla.get_rect(center=(TILE // 2, TILE // 2)))
        return superficie

    def definir_grupo_solidos(self, grupo_solidos: pygame.sprite.Group) -> None:
        """Vincula o grupo de obstáculos sólidos da fase atual para colisão."""
        self.grupo_solidos = grupo_solidos

    def atualizar_visual(
        self,
        modo_alto_contraste: bool,
        fonte_grande: bool = False,
    ) -> None:
        """Alterna o visual de Alex entre sprite cartoon e modo alto contraste."""
        self.modo_alto_contraste = modo_alto_contraste
        if fonte_grande != self.fonte_grande:
            self.fonte_grande = fonte_grande
            self._img_alto_contraste = self._criar_sprite_alto_contraste(fonte_grande)

        if modo_alto_contraste:
            self.image = self._img_alto_contraste
        else:
            self.image = self._img_esq if self.olhando_esquerda else self._img_dir

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def _limites_y(self) -> tuple[float, float]:
        """Retorna os limites verticais da calçada (entre o canteiro superior e a rua)."""
        y_min = float(HUD_ALTURA + TILE)
        y_max = float(ALTURA - 2 * TILE)
        return y_min, y_max

    def _obter_hitbox(self, pos_x: float, pos_y: float) -> pygame.Rect:
        """Retorna a hitbox reduzida (24x24) centralizada dentro do sprite 48x48."""
        margem = HITBOX_JOGADOR_MARGEM
        return pygame.Rect(
            round(pos_x) + margem,
            round(pos_y) + margem,
            TILE - 2 * margem,
            TILE - 2 * margem,
        )

    def _colide_com_solidos(self, pos_x: float, pos_y: float) -> bool:
        """Verifica colisão com grupo_solidos usando pygame.sprite.spritecollide()."""
        hitbox = self._obter_hitbox(pos_x, pos_y)
        colisoes = pygame.sprite.spritecollide(
            self,
            self.grupo_solidos,
            False,
            collided=lambda _jogador, solido: hitbox.colliderect(solido.rect),
        )
        return len(colisoes) > 0

    def _mover_com_deslizamento_quina(self, dx: float, dy: float) -> None:
        """Move Alex nos eixos X e Y com deslizamento rápido em quinas."""
        y_min, y_max = self._limites_y()

        if dx != 0.0:
            alvo_x = max(0.0, min(float(LARGURA - TILE), self.pos_x + dx))
            if not self._colide_com_solidos(alvo_x, self.pos_y):
                self.pos_x = alvo_x
            elif dy == 0.0:
                for ajuste in (4, 8, 12, CORNER_NUDGE_MAX):
                    y_cima = max(y_min, self.pos_y - ajuste)
                    if not self._colide_com_solidos(alvo_x, y_cima):
                        self.pos_y = max(y_min, self.pos_y - abs(dx))
                        break
                    y_baixo = min(y_max, self.pos_y + ajuste)
                    if not self._colide_com_solidos(alvo_x, y_baixo):
                        self.pos_y = min(y_max, self.pos_y + abs(dx))
                        break

        if dy != 0.0:
            alvo_y = max(y_min, min(y_max, self.pos_y + dy))
            if not self._colide_com_solidos(self.pos_x, alvo_y):
                self.pos_y = alvo_y
            elif dx == 0.0:
                for ajuste in (4, 8, 12, CORNER_NUDGE_MAX):
                    x_esq = max(0.0, self.pos_x - ajuste)
                    if not self._colide_com_solidos(x_esq, alvo_y):
                        self.pos_x = max(0.0, self.pos_x - abs(dy))
                        break
                    x_dir = min(float(LARGURA - TILE), self.pos_x + ajuste)
                    if not self._colide_com_solidos(x_dir, alvo_y):
                        self.pos_x = min(float(LARGURA - TILE), self.pos_x + abs(dy))
                        break

    def update(self, dt: float) -> None:
        """Atualiza Alex com resposta imediata em 8 direções e corrida via SHIFT."""
        if not self.movimento_habilitado:
            self.andando = False
            self.correndo = False
            self.rect.topleft = (round(self.pos_x), round(self.pos_y))
            return

        teclas = pygame.key.get_pressed()
        dir_x = float(
            (teclas[pygame.K_d] or teclas[pygame.K_RIGHT])
            - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        )
        dir_y = float(
            (teclas[pygame.K_s] or teclas[pygame.K_DOWN])
            - (teclas[pygame.K_w] or teclas[pygame.K_UP])
        )

        self.andando = dir_x != 0.0 or dir_y != 0.0
        sprint_ativo = bool(teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT])
        self.correndo = self.andando and sprint_ativo

        if self.andando:
            if dir_x != 0.0 and dir_y != 0.0:
                fator = 0.70710678
                dir_x *= fator
                dir_y *= fator
            if dir_x < 0.0:
                self.olhando_esquerda = True
            elif dir_x > 0.0:
                self.olhando_esquerda = False

            vel = VELOCIDADE_SPRINT if self.correndo else VELOCIDADE_JOGADOR
            self._mover_com_deslizamento_quina(dir_x * vel * dt, dir_y * vel * dt)
            self.tempo_passo += dt * (15.0 if self.correndo else 11.0)
            deslocamento_bob = round(math.sin(self.tempo_passo) * 2.0)
        else:
            self.tempo_passo = 0.0
            deslocamento_bob = 0

        if not self.modo_alto_contraste:
            self.image = self._img_esq if self.olhando_esquerda else self._img_dir

        self.rect.topleft = (round(self.pos_x), round(self.pos_y) + deslocamento_bob)

    def obter_barreira_proxima(
        self,
        grupo_barreiras: Iterable[Barreira],
    ) -> Optional[Barreira]:
        """Retorna a barreira alterável mais próxima dentro de RAIO_INTERACAO."""
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
        """Posiciona Alex imediatamente na célula (coluna, linha) da grade."""
        self.pos_x = float(coluna * TILE)
        self.pos_y = float(HUD_ALTURA + linha * TILE)
        self.tempo_passo = 0.0
        self.andando = False
        self.correndo = False
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))
