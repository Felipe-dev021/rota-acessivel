"""Módulo da entidade Barreira para o jogo educativo 'Rota Acessível'.

Encapsula em uma única classe (herdeira de pygame.sprite.Sprite) todas as
regras de negócio dos obstáculos e elementos da calçada: custos, solidez para
o jogador, bloqueio para o morador, mensagens educativas (ABNT NBR 9050),
intervenção de acessibilidade e renderização em modo normal ou alto contraste.
"""

from typing import Dict, Optional, Tuple

import pygame

from config import (
    ARQUIVO_IMG_BURACO,
    ARQUIVO_IMG_DEGRAU,
    ARQUIVO_IMG_DESTINO,
    ARQUIVO_IMG_LIXEIRA,
    ARQUIVO_IMG_PISO_OK,
    ARQUIVO_IMG_POSTE,
    ARQUIVO_IMG_RAMPA,
    CORES_ALTO_CONTRASTE,
    CUSTO_BURACO,
    CUSTO_DEGRAU,
    CUSTO_LIXEIRA,
    FONTE_FAMILIA,
    FONTES_GRANDE,
    FONTES_NORMAL,
    HUD_ALTURA,
    TILE,
    TIPO_BURACO,
    TIPO_DEGRAU,
    TIPO_DESTINO,
    TIPO_LIXEIRA,
    TIPO_PISO_OK,
    TIPO_POSTE,
    TIPO_RAMPA,
    caminho_arquivo,
)


class Barreira(pygame.sprite.Sprite):
    """Representa uma barreira urbana ou elemento especial posicionado na grade.

    Todas as regras de negócio do obstáculo (custo, solidez, bloqueio do
    morador, transição ao resolver e textos educativos) residem nesta classe,
    evitando cadeias condicionais espalhadas pelo loop principal.
    """

    TABELA_TIPOS: Dict[str, Dict[str, object]] = {
        TIPO_LIXEIRA: {
            "custo": CUSTO_LIXEIRA,
            "eh_solida": False,
            "bloqueia_morador": True,
            "alteravel": True,
            "tipo_resolvido": None,  # Removida com self.kill()
            "sprite": ARQUIVO_IMG_LIXEIRA,
            "sigla": "L",
            "rotulo_acao": "Deslocar Lixeira",
            "mensagem_sucesso": (
                "Lixeira deslocada para a faixa de serviço! A faixa livre "
                "agora está desobstruída (custo: 0 recursos)."
            ),
            "mensagem_erro": (
                "Lixeira bloqueando a faixa livre! Mobiliário solto na área "
                "de circulação impede a passagem segura de cadeiras de rodas."
            ),
        },
        TIPO_DEGRAU: {
            "custo": CUSTO_DEGRAU,
            "eh_solida": False,
            "bloqueia_morador": True,
            "alteravel": True,
            "tipo_resolvido": TIPO_RAMPA,
            "sprite": ARQUIVO_IMG_DEGRAU,
            "sigla": "D",
            "rotulo_acao": "Instalar Rampa",
            "mensagem_sucesso": (
                "Rampa acessível instalada no desnível! Agora pessoas em "
                "cadeira de rodas podem cruzar com autonomia (custo: 1 rec)."
            ),
            "mensagem_erro": (
                "Degrau sem rebaixamento! Desníveis acima de 2 cm bloqueiam "
                "cadeiras de rodas e exigem rampa segura (ABNT NBR 9050)."
            ),
        },
        TIPO_BURACO: {
            "custo": CUSTO_BURACO,
            "eh_solida": False,
            "bloqueia_morador": True,
            "alteravel": True,
            "tipo_resolvido": TIPO_PISO_OK,
            "sprite": ARQUIVO_IMG_BURACO,
            "sigla": "B",
            "rotulo_acao": "Nivelar Piso",
            "mensagem_sucesso": (
                "Pavimento nivelado e regularizado! O risco de travamento de "
                "rodas dianteiras foi eliminado (custo: 1 rec)."
            ),
            "mensagem_erro": (
                "Buraco no pavimento! Pisos danificados travam as rodas "
                "dianteiras da cadeira de rodas e causam risco de tombamento."
            ),
        },
        TIPO_POSTE: {
            "custo": 0,
            "eh_solida": True,
            "bloqueia_morador": True,
            "alteravel": False,
            "tipo_resolvido": None,
            "sprite": ARQUIVO_IMG_POSTE,
            "sigla": "P",
            "rotulo_acao": "Poste Fixo",
            "mensagem_sucesso": "",
            "mensagem_erro": (
                "Poste fixo no trajeto! Estruturas permanentes não podem ser "
                "removidas — planeje uma rota contínua desviando deste ponto."
            ),
        },
        TIPO_RAMPA: {
            "custo": 0,
            "eh_solida": False,
            "bloqueia_morador": False,
            "alteravel": False,
            "tipo_resolvido": None,
            "sprite": ARQUIVO_IMG_RAMPA,
            "sigla": "R",
            "rotulo_acao": "Rampa Acessível",
            "mensagem_sucesso": "",
            "mensagem_erro": "",
        },
        TIPO_PISO_OK: {
            "custo": 0,
            "eh_solida": False,
            "bloqueia_morador": False,
            "alteravel": False,
            "tipo_resolvido": None,
            "sprite": ARQUIVO_IMG_PISO_OK,
            "sigla": "OK",
            "rotulo_acao": "Piso Nivelado",
            "mensagem_sucesso": "",
            "mensagem_erro": "",
        },
        TIPO_DESTINO: {
            "custo": 0,
            "eh_solida": False,
            "bloqueia_morador": False,
            "alteravel": False,
            "tipo_resolvido": None,
            "sprite": ARQUIVO_IMG_DESTINO,
            "sigla": "FIM",
            "rotulo_acao": "Destino",
            "mensagem_sucesso": "",
            "mensagem_erro": "",
        },
    }

    _cache_imagens: Dict[str, pygame.Surface] = {}
    _cache_fontes_sigla: Dict[bool, pygame.font.Font] = {}

    def __init__(
        self,
        coluna: int,
        linha: int,
        tipo: str,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Inicializa a barreira na célula (coluna, linha) da grade urbana.

        Args:
            coluna: Índice horizontal do tile (0 a COLS - 1).
            linha: Índice vertical do tile (0 a ROWS - 1).
            tipo: Tipo inicial cadastrado em TABELA_TIPOS.
            modo_alto_contraste: Ativa renderização com borda grossa e sigla.
            fonte_grande: Usa fonte ampliada para a sigla em alto contraste.
        """
        super().__init__()
        self.coluna: int = coluna
        self.linha: int = linha
        self.tipo: str = tipo
        self.pos_x: float = float(coluna * TILE)
        self.pos_y: float = float(HUD_ALTURA + linha * TILE)

        self.custo: int = 0
        self.eh_solida: bool = False
        self.bloqueia_morador: bool = False
        self.alteravel: bool = False
        self.tipo_resolvido: Optional[str] = None
        self.sprite_arquivo: str = ""
        self.sigla: str = ""
        self.rotulo_acao: str = ""
        self.mensagem_sucesso: str = ""
        self.mensagem_erro: str = ""

        self._carregar_atributos_tipo(tipo)

        self.image: pygame.Surface = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        self.rect: pygame.Rect = self.image.get_rect(
            topleft=(round(self.pos_x), round(self.pos_y))
        )
        self.atualizar_visual(modo_alto_contraste, fonte_grande)

    def _carregar_atributos_tipo(self, tipo: str) -> None:
        """Popula todos os atributos de regra de negócio a partir de TABELA_TIPOS.

        Args:
            tipo: Chave do tipo de obstáculo/elemento em TABELA_TIPOS.
        """
        dados = self.TABELA_TIPOS[tipo]
        self.tipo = tipo
        self.custo = int(dados["custo"])
        self.eh_solida = bool(dados["eh_solida"])
        self.bloqueia_morador = bool(dados["bloqueia_morador"])
        self.alteravel = bool(dados["alteravel"])
        resolvido = dados["tipo_resolvido"]
        self.tipo_resolvido = str(resolvido) if resolvido is not None else None
        self.sprite_arquivo = str(dados["sprite"])
        self.sigla = str(dados["sigla"])
        self.rotulo_acao = str(dados["rotulo_acao"])
        self.mensagem_sucesso = str(dados["mensagem_sucesso"])
        self.mensagem_erro = str(dados["mensagem_erro"])

    @classmethod
    def _carregar_imagem_normal(cls, nome_arquivo: str) -> pygame.Surface:
        """Carrega e armazena em cache o sprite PNG usando caminho_arquivo().

        Args:
            nome_arquivo: Nome do arquivo PNG dentro de data/.

        Returns:
            Superfície pygame no tamanho TILE x TILE.
        """
        if nome_arquivo not in cls._cache_imagens:
            superficie = pygame.image.load(caminho_arquivo(nome_arquivo))
            if pygame.display.get_surface() is not None:
                superficie = superficie.convert_alpha()
            if superficie.get_size() != (TILE, TILE):
                superficie = pygame.transform.smoothscale(superficie, (TILE, TILE))
            cls._cache_imagens[nome_arquivo] = superficie
        return cls._cache_imagens[nome_arquivo]

    @classmethod
    def _obter_fonte_sigla(cls, fonte_grande: bool) -> pygame.font.Font:
        """Retorna a fonte em negrito usada para desenhar siglas em alto contraste.

        Args:
            fonte_grande: True usa o tamanho ampliado; False usa o tamanho padrão.

        Returns:
            Instância de pygame.font.Font em cache.
        """
        if fonte_grande not in cls._cache_fontes_sigla:
            escala = FONTES_GRANDE if fonte_grande else FONTES_NORMAL
            cls._cache_fontes_sigla[fonte_grande] = pygame.font.SysFont(
                FONTE_FAMILIA, escala["sigla"], bold=True
            )
        return cls._cache_fontes_sigla[fonte_grande]

    def atualizar_visual(
        self,
        modo_alto_contraste: bool,
        fonte_grande: bool = False,
    ) -> None:
        """Atualiza o sprite da barreira para modo normal ou alto contraste.

        Args:
            modo_alto_contraste: True desenha tile de alto contraste com borda
                espessa e sigla identificadora; False usa o PNG padrão.
            fonte_grande: True amplia a sigla desenhada no modo alto contraste.
        """
        if not modo_alto_contraste:
            self.image = self._carregar_imagem_normal(self.sprite_arquivo).copy()
        else:
            superficie = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            chave_cor = f"tile_{self.tipo}"
            cor_fundo = CORES_ALTO_CONTRASTE[chave_cor]
            cor_borda = CORES_ALTO_CONTRASTE["tile_borda"]
            cor_sigla = CORES_ALTO_CONTRASTE["tile_sigla"]

            pygame.draw.rect(
                superficie, cor_fundo, (2, 2, TILE - 4, TILE - 4), border_radius=5
            )
            pygame.draw.rect(
                superficie, cor_borda, (2, 2, TILE - 4, TILE - 4), 3, border_radius=5
            )

            fonte = self._obter_fonte_sigla(fonte_grande)
            texto = fonte.render(self.sigla, True, cor_sigla)
            superficie.blit(texto, texto.get_rect(center=(TILE // 2, TILE // 2)))
            self.image = superficie

        self.rect.topleft = (round(self.pos_x), round(self.pos_y))

    def texto_prompt_interacao(self) -> str:
        """Retorna o texto descritivo para a moldura de destaque '[E]'.

        Returns:
            String formatada com ação e custo (ex.: '[E] Instalar Rampa (1 rec)').
        """
        if self.custo == 0:
            return f"[E] {self.rotulo_acao} (0 rec)"
        return f"[E] {self.rotulo_acao} ({self.custo} rec)"

    def resolver(
        self,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> Tuple[bool, str]:
        """Executa a intervenção de acessibilidade definida para esta barreira.

        Args:
            modo_alto_contraste: Mantém o padrão visual ativo após a conversão.
            fonte_grande: Mantém a escala de fonte ativa após a conversão.

        Returns:
            Tupla (resolvida, mensagem) indicando se a intervenção foi aplicada
            e o texto educativo correspondente.
        """
        if not self.alteravel:
            return False, self.mensagem_erro

        mensagem = self.mensagem_sucesso

        if self.tipo_resolvido is None:
            # Obstáculo móvel (ex.: lixeira) removido da faixa livre
            self.bloqueia_morador = False
            self.alteravel = False
            self.kill()
            return True, mensagem

        self._carregar_atributos_tipo(self.tipo_resolvido)
        self.atualizar_visual(modo_alto_contraste, fonte_grande)
        return True, mensagem

    def centro(self) -> Tuple[float, float]:
        """Retorna as coordenadas (x, y) em float do centro da barreira."""
        return (self.pos_x + TILE / 2.0, self.pos_y + TILE / 2.0)

    def update(self, dt: float = 0.0) -> None:
        """Mantém compatibilidade com o grupo_desenho único do jogo.

        Args:
            dt: Delta time em segundos do frame atual.
        """
        _ = dt
        self.rect.topleft = (round(self.pos_x), round(self.pos_y))
