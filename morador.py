"""Módulo da entidade Morador e algoritmo de validação de rota acessível (BFS).

Implementa a classe Morador (herdeira de pygame.sprite.Sprite) com suporte aos
3 perfis reais de moradores das fases (cadeirante, pessoa surda e pessoa com
baixa visão/bengala branca), garantindo coerência visual e educativa com as
barreiras de cada cenário, além da Busca em Largura (BFS) em 4 direções.
"""

from collections import deque
from typing import Dict, List, Optional, Tuple

import pygame

from barreira import Barreira
from config import (
    ARQUIVO_IMG_MORADOR,
    ARQUIVO_IMG_MORADOR_BAIXA_VISAO,
    ARQUIVO_IMG_MORADOR_SURDO,
    BORDA_ALTO_CONTRASTE,
    COLS,
    CORES_ALTO_CONTRASTE,
    FONTE_FAMILIA,
    FONTES_GRANDE,
    FONTES_NORMAL,
    HUD_ALTURA,
    PERFIL_BAIXA_VISAO,
    PERFIL_CADEIRANTE,
    PERFIL_SURDO,
    ROWS,
    TILE,
    TIPO_POSTE,
    VELOCIDADE_MORADOR,
    caminho_arquivo,
)

Celula = Tuple[int, int]
GradeBarreiras = Dict[Celula, Barreira]


class Morador(pygame.sprite.Sprite):
    """Representa o Morador da fase que valida a continuidade acessível da rota."""

    _DIRECOES: Tuple[Celula, ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))
    _SPRITES_POR_PERFIL: Dict[str, str] = {
        PERFIL_CADEIRANTE: ARQUIVO_IMG_MORADOR,
        PERFIL_SURDO: ARQUIVO_IMG_MORADOR_SURDO,
        PERFIL_BAIXA_VISAO: ARQUIVO_IMG_MORADOR_BAIXA_VISAO,
    }

    def __init__(
        self,
        coluna: int,
        linha: int,
        perfil: str = PERFIL_CADEIRANTE,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Inicializa o Morador na célula inicial à esquerda do mapa.

        Args:
            coluna: Coluna inicial na grade (0 a COLS - 1).
            linha: Linha inicial na grade (0 a ROWS - 1).
            perfil: Identificador do perfil ('cadeirante', 'surdo', 'baixa_visao').
            modo_alto_contraste: Define o modo visual inicial.
            fonte_grande: Define a escala de fonte da sigla no alto contraste.
        """
        super().__init__()
        self.inicio_coluna: int = coluna
        self.inicio_linha: int = linha
        self.pos_x: float = float(coluna * TILE)
        self.pos_y: float = float(HUD_ALTURA + linha * TILE)
        self.perfil: str = perfil
        self.modo_alto_contraste: bool = modo_alto_contraste
        self.fonte_grande: bool = fonte_grande

        self._sprites_cache: Dict[str, pygame.Surface] = {}
        self._carregar_todos_sprites()

        self.image: pygame.Surface = self._sprites_cache[PERFIL_CADEIRANTE]
        self.rect: pygame.Rect = self.image.get_rect(
            topleft=(round(self.pos_x), round(self.pos_y))
        )

        self.caminho: List[Celula] = []
        self.celulas_percorridas: List[Celula] = []
        self.indice_passo: int = 0
        self.em_movimento: bool = False
        self.rota_sucesso: bool = False
        self.barreira_bloqueadora: Optional[Barreira] = None
        self.resultado_pendente: Optional[str] = None

        self.atualizar_visual(modo_alto_contraste, fonte_grande)

    def _carregar_todos_sprites(self) -> None:
        """Carrega em cache os 3 sprites de moradores via caminho_arquivo()."""
        for chave_perfil, nome_arquivo in self._SPRITES_POR_PERFIL.items():
            superficie = pygame.image.load(caminho_arquivo(nome_arquivo))
            if pygame.display.get_surface() is not None:
                superficie = superficie.convert_alpha()
            if superficie.get_size() != (TILE, TILE):
                superficie = pygame.transform.smoothscale(superficie, (TILE, TILE))
            self._sprites_cache[chave_perfil] = superficie

    def definir_perfil(self, perfil: str) -> None:
        """Altera o perfil visual do Morador conforme a fase carregada.

        Args:
            perfil: Um dos perfis definidos em config.py.
        """
        if perfil in self._sprites_cache:
            self.perfil = perfil
            self.atualizar_visual(self.modo_alto_contraste, self.fonte_grande)

    def obter_retrato(self, tamanho: int = 40) -> pygame.Surface:
        """Retorna uma miniatura do sprite do Morador atual para uso no HUD."""
        base = self._sprites_cache.get(self.perfil, self._sprites_cache[PERFIL_CADEIRANTE])
        return pygame.transform.smoothscale(base, (tamanho, tamanho))

    def atualizar_visual(
        self,
        modo_alto_contraste: bool,
        fonte_grande: bool = False,
    ) -> None:
        """Atualiza o sprite do Morador entre modo cartoon e alto contraste."""
        self.modo_alto_contraste = modo_alto_contraste
        self.fonte_grande = fonte_grande

        if not modo_alto_contraste:
            self.image = self._sprites_cache.get(
                self.perfil, self._sprites_cache[PERFIL_CADEIRANTE]
            )
        else:
            superficie = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.rect(
                superficie,
                CORES_ALTO_CONTRASTE["rota_preview"],
                (4, 4, TILE - 8, TILE - 8),
                border_radius=10,
            )
            pygame.draw.rect(
                superficie,
                CORES_ALTO_CONTRASTE["tile_borda"],
                (4, 4, TILE - 8, TILE - 8),
                BORDA_ALTO_CONTRASTE,
                border_radius=10,
            )
            escala = FONTES_GRANDE if fonte_grande else FONTES_NORMAL
            fonte = pygame.font.SysFont(FONTE_FAMILIA, escala["sigla"], bold=True)
            sigla = fonte.render("M", True, CORES_ALTO_CONTRASTE["destaque_e_texto"])
            superficie.blit(sigla, sigla.get_rect(center=(TILE // 2, TILE // 2)))
            self.image = superficie

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def _dentro_grade(self, coluna: int, linha: int) -> bool:
        """Verifica se a célula (coluna, linha) está na faixa jogável da calçada (linhas 1 a 9)."""
        return 0 <= coluna < COLS and 1 <= linha < ROWS - 1

    def _eh_transitavel(self, celula: Celula, grade_barreiras: GradeBarreiras) -> bool:
        """Retorna True se a célula estiver livre para a passagem do Morador."""
        barreira = grade_barreiras.get(celula)
        return barreira is None or not barreira.bloqueia_morador

    def _distancias_reversas_ao_destino(
        self,
        grade_barreiras: GradeBarreiras,
        destino: Celula,
        ignorar_postes: bool,
    ) -> Dict[Celula, int]:
        """Calcula via BFS a menor distância em passos de cada célula ao destino."""
        distancias: Dict[Celula, int] = {destino: 0}
        fila: deque[Celula] = deque([destino])

        while fila:
            col, lin = fila.popleft()
            dist_atual = distancias[(col, lin)]
            for dc, dl in self._DIRECOES:
                nc, nl = col + dc, lin + dl
                vizinha = (nc, nl)
                if not self._dentro_grade(nc, nl) or vizinha in distancias:
                    continue
                barreira = grade_barreiras.get(vizinha)
                if not ignorar_postes and barreira is not None and barreira.tipo == TIPO_POSTE:
                    continue
                distancias[vizinha] = dist_atual + 1
                fila.append(vizinha)

        return distancias

    def _reconstruir_caminho(
        self,
        pais: Dict[Celula, Optional[Celula]],
        alvo: Celula,
    ) -> List[Celula]:
        """Reconstrói a sequência ordenada de células do início até o alvo."""
        caminho: List[Celula] = []
        atual: Optional[Celula] = alvo
        while atual is not None:
            caminho.append(atual)
            atual = pais[atual]
        caminho.reverse()
        return caminho

    def calcular_rota(
        self,
        grade_barreiras: GradeBarreiras,
        inicio: Celula,
        destino: Celula,
    ) -> Tuple[bool, List[Celula], Optional[Barreira]]:
        """Executa BFS em 4 direções sobre a grade 20x11 do início ao destino.

        Returns:
            Tupla (sucesso, caminho, barreira_bloqueadora).
        """
        pais: Dict[Celula, Optional[Celula]] = {inicio: None}
        dist_inicio: Dict[Celula, int] = {inicio: 0}
        fila: deque[Celula] = deque([inicio])

        while fila:
            col, lin = fila.popleft()
            if (col, lin) == destino:
                return True, self._reconstruir_caminho(pais, destino), None

            for dc, dl in self._DIRECOES:
                nc, nl = col + dc, lin + dl
                vizinha = (nc, nl)
                if not self._dentro_grade(nc, nl) or vizinha in pais:
                    continue
                if self._eh_transitavel(vizinha, grade_barreiras):
                    pais[vizinha] = (col, lin)
                    dist_inicio[vizinha] = dist_inicio[(col, lin)] + 1
                    fila.append(vizinha)

        dist_sem_poste = self._distancias_reversas_ao_destino(
            grade_barreiras, destino, ignorar_postes=False
        )
        dist_qualquer = self._distancias_reversas_ao_destino(
            grade_barreiras, destino, ignorar_postes=True
        )

        melhor_candidato: Optional[Tuple[int, int, int, Celula, Barreira]] = None

        for celula_livre in pais:
            col, lin = celula_livre
            for dc, dl in self._DIRECOES:
                vizinha = (col + dc, lin + dl)
                barreira = grade_barreiras.get(vizinha)
                if barreira is None or not barreira.bloqueia_morador:
                    continue

                if vizinha in dist_sem_poste:
                    prioridade = 0
                    dist_dest = dist_sem_poste[vizinha]
                else:
                    prioridade = 1
                    dist_dest = dist_qualquer.get(vizinha, 9999)

                custo_total = dist_dest + dist_inicio[celula_livre]
                candidato = (
                    prioridade,
                    custo_total,
                    dist_dest,
                    celula_livre,
                    barreira,
                )
                if melhor_candidato is None or candidato[:3] < melhor_candidato[:3]:
                    melhor_candidato = candidato

        if melhor_candidato is not None:
            _, _, _, tile_anterior, barreira_bloqueio = melhor_candidato
            caminho_parcial = self._reconstruir_caminho(pais, tile_anterior)
            return False, caminho_parcial, barreira_bloqueio

        return False, [inicio], None

    def iniciar_teste(
        self,
        caminho: List[Celula],
        rota_sucesso: bool,
        barreira_bloqueadora: Optional[Barreira],
    ) -> None:
        """Inicia o deslocamento do Morador ao longo do trajeto retornado pelo BFS."""
        self.reposicionar(self.inicio_coluna, self.inicio_linha)
        self.caminho = list(caminho)
        self.celulas_percorridas = [self.caminho[0]] if self.caminho else []
        self.indice_passo = 1 if len(self.caminho) > 1 else len(self.caminho)
        self.rota_sucesso = rota_sucesso
        self.barreira_bloqueadora = barreira_bloqueadora
        self.resultado_pendente = None
        self.em_movimento = True

    def cancelar_teste(self) -> None:
        """Interrompe imediatamente o teste em curso e reposiciona no início."""
        self.em_movimento = False
        self.caminho = []
        self.celulas_percorridas = []
        self.indice_passo = 0
        self.barreira_bloqueadora = None
        self.resultado_pendente = None
        self.reposicionar(self.inicio_coluna, self.inicio_linha)

    def consumir_resultado(self) -> Optional[str]:
        """Retorna e limpa o resultado final ('VITORIA' ou 'BLOQUEADO') quando pronto."""
        resultado = self.resultado_pendente
        self.resultado_pendente = None
        return resultado

    def reposicionar(self, coluna: int, linha: int) -> None:
        """Define a célula inicial e atual do Morador na grade."""
        self.inicio_coluna = coluna
        self.inicio_linha = linha
        self.pos_x = float(coluna * TILE)
        self.pos_y = float(HUD_ALTURA + linha * TILE)
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def update(self, dt: float) -> None:
        """Move o Morador suavemente tile a tile usando VELOCIDADE_MORADOR * dt."""
        if not self.em_movimento:
            return

        if self.indice_passo >= len(self.caminho):
            self.em_movimento = False
            self.resultado_pendente = "VITORIA" if self.rota_sucesso else "BLOQUEADO"
            return

        alvo_col, alvo_lin = self.caminho[self.indice_passo]
        alvo_x = float(alvo_col * TILE)
        alvo_y = float(HUD_ALTURA + alvo_lin * TILE)

        dx = alvo_x - self.pos_x
        dy = alvo_y - self.pos_y
        distancia = (dx * dx + dy * dy) ** 0.5
        passo = VELOCIDADE_MORADOR * dt

        if distancia <= passo:
            self.pos_x = alvo_x
            self.pos_y = alvo_y
            self.celulas_percorridas.append((alvo_col, alvo_lin))
            self.indice_passo += 1
        elif distancia > 0.0:
            self.pos_x += (dx / distancia) * passo
            self.pos_y += (dy / distancia) * passo

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

        if self.indice_passo >= len(self.caminho):
            self.em_movimento = False
            self.resultado_pendente = "VITORIA" if self.rota_sucesso else "BLOQUEADO"
