"""Módulo reescrito do zero para movimentação fluida de Alex em 'Rota Acessível'.

Implementa colisão top-down compacta nos pés do personagem (20x16 px dentro de
48x48 px, estilo Stardew Valley/Zelda), encaixe exato (wall-snap) sem frestas,
deslizamento automático em quinas mesmo em diagonais, corrida ágil via SHIFT e
suporte opcional a caminhada guiada por clique/arraste do mouse.
"""

import math
from typing import Iterable, List, Optional, Tuple

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
    HITBOX_JOGADOR_ALTURA,
    HITBOX_JOGADOR_LARGURA,
    HUD_ALTURA,
    LARGURA,
    RAIO_INTERACAO,
    TILE,
    VELOCIDADE_JOGADOR,
    VELOCIDADE_SPRINT,
    caminho_arquivo,
)


class Jogador(pygame.sprite.Sprite):
    """Controla Alex com movimentação top-down super responsiva e sem travamentos."""

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
        # Posição real em float representa o canto superior esquerdo do sprite 48x48
        self.pos_x: float = float(coluna * TILE)
        self.pos_y: float = float(HUD_ALTURA + linha * TILE)
        self.render_x: float = self.pos_x
        self.render_y: float = self.pos_y
        self.tempo_passo: float = 0.0
        self.bob_atual: float = 0.0
        self.olhando_esquerda: bool = False
        self.andando: bool = False
        self.correndo: bool = False
        self.modo_alto_contraste: bool = modo_alto_contraste
        self.fonte_grande: bool = fonte_grande
        self.destino_mouse: Optional[Tuple[float, float]] = None

        self.grupo_solidos: pygame.sprite.Group = (
            grupo_solidos if grupo_solidos is not None else pygame.sprite.Group()
        )
        self._rects_solidos: List[pygame.Rect] = [s.rect for s in self.grupo_solidos]
        self.movimento_habilitado: bool = True

        self._img_dir: pygame.Surface = self._carregar_sprite()
        self._img_esq: pygame.Surface = pygame.transform.flip(self._img_dir, True, False)
        self._img_alto_contraste: pygame.Surface = self._criar_sprite_alto_contraste(
            fonte_grande
        )
        self.image: pygame.Surface = self._img_dir
        self.rect: pygame.Rect = pygame.Rect(
            round(self.pos_x), round(self.pos_y), TILE, TILE
        )
        self.atualizar_visual(modo_alto_contraste, fonte_grande)

    def _carregar_sprite(self) -> pygame.Surface:
        """Carrega player.png (48x64 2.5D) a partir de data/ via caminho_arquivo()."""
        superficie = pygame.image.load(caminho_arquivo(ARQUIVO_IMG_PLAYER))
        if pygame.display.get_surface() is not None:
            superficie = superficie.convert_alpha()
        if superficie.get_width() != TILE:
            nova_altura = max(TILE, round(superficie.get_height() * (TILE / superficie.get_width())))
            superficie = pygame.transform.smoothscale(superficie, (TILE, nova_altura))
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
        """Vincula o grupo de obstáculos sólidos da fase e pré-extrai seus rects."""
        self.grupo_solidos = grupo_solidos
        self._rects_solidos = [s.rect for s in grupo_solidos]

    def definir_destino_mouse(self, pos_x: float, pos_y: float) -> None:
        """Define um destino de caminhada ao clicar na calçada com o mouse."""
        self.destino_mouse = (pos_x - TILE / 2.0, pos_y - TILE / 2.0)

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

    def _hitbox_pes(self, pos_x: float, pos_y: float) -> pygame.Rect:
        """Retorna a hitbox compacta (20x16) nos pés de Alex para movimento fluido."""
        off_x = (TILE - HITBOX_JOGADOR_LARGURA) // 2
        off_y = TILE - HITBOX_JOGADOR_ALTURA - 4
        return pygame.Rect(
            round(pos_x) + off_x,
            round(pos_y) + off_y,
            HITBOX_JOGADOR_LARGURA,
            HITBOX_JOGADOR_ALTURA,
        )

    def _colisoes_em(self, pos_x: float, pos_y: float) -> List[pygame.Rect]:
        """Retorna os rects sólidos colidindo com a hitbox dos pés (via C collidelistall)."""
        hitbox = self._hitbox_pes(pos_x, pos_y)
        indices = hitbox.collidelistall(self._rects_solidos)
        return [self._rects_solidos[i] for i in indices]

    def _limites_calcada(self) -> Tuple[float, float, float, float]:
        """Retorna (x_min, x_max, y_min, y_max) da calçada jogável."""
        return (
            0.0,
            float(LARGURA - TILE),
            float(HUD_ALTURA + TILE - 12),
            float(ALTURA - 2 * TILE),
        )

    def _mover_eixo_x(self, dx: float) -> None:
        """Move Alex no eixo X com wall-snap preciso e deslizamento em quinas."""
        if dx == 0.0:
            return
        x_min, x_max, y_min, y_max = self._limites_calcada()
        alvo_x = max(x_min, min(x_max, self.pos_x + dx))
        colisoes = self._colisoes_em(alvo_x, self.pos_y)

        if not colisoes:
            self.pos_x = alvo_x
            return

        # Tenta deslizar suavemente ao redor da quina do canteiro/poste
        if len(colisoes) == 1:
            solido = colisoes[0]
            hb = self._hitbox_pes(alvo_x, self.pos_y)
            sobreposicao_topo = hb.bottom - solido.top
            sobreposicao_base = solido.bottom - hb.top

            if 0 < sobreposicao_topo <= CORNER_NUDGE_MAX:
                nova_y = max(y_min, self.pos_y - abs(dx))
                if not self._colisoes_em(self.pos_x, nova_y):
                    self.pos_y = nova_y
                    return
            elif 0 < sobreposicao_base <= CORNER_NUDGE_MAX:
                nova_y = min(y_max, self.pos_y + abs(dx))
                if not self._colisoes_em(self.pos_x, nova_y):
                    self.pos_y = nova_y
                    return

        # Encaixe exato rente à borda do obstáculo (wall-snap sem frestas)
        off_x = (TILE - HITBOX_JOGADOR_LARGURA) // 2
        solido = colisoes[0]
        if dx > 0.0:
            self.pos_x = max(x_min, float(solido.left - off_x - HITBOX_JOGADOR_LARGURA))
        else:
            self.pos_x = min(x_max, float(solido.right - off_x))

    def _mover_eixo_y(self, dy: float) -> None:
        """Move Alex no eixo Y com wall-snap preciso e deslizamento em quinas."""
        if dy == 0.0:
            return
        x_min, x_max, y_min, y_max = self._limites_calcada()
        alvo_y = max(y_min, min(y_max, self.pos_y + dy))
        colisoes = self._colisoes_em(self.pos_x, alvo_y)

        if not colisoes:
            self.pos_y = alvo_y
            return

        if len(colisoes) == 1:
            solido = colisoes[0]
            hb = self._hitbox_pes(self.pos_x, alvo_y)
            sobreposicao_esq = hb.right - solido.left
            sobreposicao_dir = solido.right - hb.left

            if 0 < sobreposicao_esq <= CORNER_NUDGE_MAX:
                nova_x = max(x_min, self.pos_x - abs(dy))
                if not self._colisoes_em(nova_x, self.pos_y):
                    self.pos_x = nova_x
                    return
            elif 0 < sobreposicao_dir <= CORNER_NUDGE_MAX:
                nova_x = min(x_max, self.pos_x + abs(dy))
                if not self._colisoes_em(nova_x, self.pos_y):
                    self.pos_x = nova_x
                    return

        off_y = TILE - HITBOX_JOGADOR_ALTURA - 4
        solido = colisoes[0]
        if dy > 0.0:
            self.pos_y = max(y_min, float(solido.top - off_y - HITBOX_JOGADOR_ALTURA))
        else:
            self.pos_y = min(y_max, float(solido.bottom - off_y))

    def update(self, dt: float) -> None:
        """Atualiza Alex via teclado (WASD/Setas + SHIFT) ou clique na calçada."""
        if not self.movimento_habilitado:
            self.andando = False
            self.correndo = False
            self.destino_mouse = None
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

        # Teclado sempre cancela caminhada automática por mouse
        if dir_x != 0.0 or dir_y != 0.0:
            self.destino_mouse = None
        elif self.destino_mouse is not None:
            mx, my = self.destino_mouse
            vx = mx - self.pos_x
            vy = my - self.pos_y
            dist = math.hypot(vx, vy)
            if dist <= 6.0:
                self.destino_mouse = None
            else:
                dir_x = vx / dist
                dir_y = vy / dist

        self.andando = dir_x != 0.0 or dir_y != 0.0
        sprint_ativo = bool(teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT])
        self.correndo = self.andando and sprint_ativo

        if self.andando:
            norma = math.hypot(dir_x, dir_y)
            if norma > 1.0:
                dir_x /= norma
                dir_y /= norma

            if dir_x < -0.1:
                self.olhando_esquerda = True
            elif dir_x > 0.1:
                self.olhando_esquerda = False

            vel = VELOCIDADE_SPRINT if self.correndo else VELOCIDADE_JOGADOR
            self._mover_eixo_x(dir_x * vel * dt)
            self._mover_eixo_y(dir_y * vel * dt)

            self.tempo_passo += dt * (14.0 if self.correndo else 10.5)
            bob_alvo = math.sin(self.tempo_passo) * (2.6 if self.correndo else 2.0)
        else:
            self.tempo_passo += dt * 3.0
            bob_alvo = math.sin(self.tempo_passo) * 0.6

        # Interpolação visual ultra-suave (elimina qualquer salto ao deslizar em quinas)
        suavizacao = min(1.0, 26.0 * dt)
        self.render_x += (self.pos_x - self.render_x) * suavizacao
        self.render_y += (self.pos_y - self.render_y) * suavizacao
        self.bob_atual += (bob_alvo - self.bob_atual) * min(1.0, 16.0 * dt)

        if not self.modo_alto_contraste:
            self.image = self._img_esq if self.olhando_esquerda else self._img_dir

        self.rect.topleft = (round(self.render_x), round(self.render_y + self.bob_atual))

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
        self.render_x = self.pos_x
        self.render_y = self.pos_y
        self.tempo_passo = 0.0
        self.bob_atual = 0.0
        self.andando = False
        self.correndo = False
        self.destino_mouse = None
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))
