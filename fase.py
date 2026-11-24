"""Gerenciador de fases, mapas em grade 20x11 e métricas de aprendizado.

Implementa a classe GerenciadorFases, responsável por instanciar os grupos de
sprites (grupo_barreiras, grupo_solidos e grupo_interativos) a partir de mapas
em matriz de caracteres, gerenciar tempo e orçamento de recursos, reiniciar
fases e registrar métricas observáveis de evolução do jogador.
"""

from typing import Dict, List, Tuple

import pygame

from barreira import Barreira
from config import (
    COLS,
    ROWS,
    TIPO_BURACO,
    TIPO_DEGRAU,
    TIPO_DESTINO,
    TIPO_LIXEIRA,
    TIPO_POSTE,
)

Celula = Tuple[int, int]


class GerenciadorFases:
    """Controla a progressão de fases, os grupos de sprites e as métricas."""

    # Legenda dos mapas 20x11:
    # '.' = faixa livre | 'I' = início do Morador | 'J' = início de Alex
    # 'F' = destino     | 'P' = poste fixo        | 'L' = lixeira (0 rec)
    # 'D' = degrau (1)  | 'B' = buraco (1)
    FASES_INICIAIS: List[Dict[str, object]] = [
        {
            "numero": 1,
            "nome": "Calçada do Bairro",
            "tempo": 90.0,
            "recursos": 3,
            "descricao": (
                "Remova as lixeiras sem custo e instale uma rampa no degrau "
                "para garantir uma faixa livre contínua."
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Faixa Livre: toda calçada deve manter uma "
                "faixa livre contínua de no mínimo 1,20 m sem obstáculos "
                "soltos e com desníveis devidamente rebaixados."
            ),
            "mapa": [
                "PPPPPPPPPPPPPPPPPPPP",
                "PPPPPPPPPPPPPPPPPPPP",
                "P.....P.....P...P..P",
                "P.....P.....P...P..P",
                "P.....L.....P...P..P",
                "I..J..L.....D...L..F",
                "P.....P.....P...L..P",
                "P.....P.....P...P..P",
                "P.....P.....P...P..P",
                "PPPPPPPPPPPPPPPPPPPP",
                "PPPPPPPPPPPPPPPPPPPP",
            ],
        },
        {
            "numero": 2,
            "nome": "Entrada da Escola",
            "tempo": 80.0,
            "recursos": 4,
            "descricao": (
                "Contorne os postes fixos em gargalos estreitos, remova as "
                "lixeiras e adapte degraus e buraco."
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Rota Acessível Contínua: postes devem ficar "
                "na faixa de serviço. Em gargalos estreitos, qualquer degrau "
                "ou buraco sem correção interrompe toda a autonomia."
            ),
            "mapa": [
                "PPPPPPPPPPPPPPPPPPPP",
                "P....P..P...P..P.P.P",
                "P....L..P...P..P.P.P",
                "P....P..PP..P..P.P.P",
                "I.J..P..P...D..P.P.P",
                "P....P..P...P..P.B.F",
                "P....P..L...P..D.P.P",
                "P....P..P...P..P.P.P",
                "P....P..P...P..P.P.P",
                "P....P..P...P..P.P.P",
                "PPPPPPPPPPPPPPPPPPPP",
            ],
        },
        {
            "numero": 3,
            "nome": "Caminho ao Posto de Saúde",
            "tempo": 70.0,
            "recursos": 4,
            "descricao": (
                "Observe todo o mapa antes de gastar recursos — cuidado com "
                "o corredor superior fechado por postes fixos!"
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Planejamento Urbano: diagnosticar a rota "
                "completa evita investir orçamento limitado em corredores sem "
                "saída e garante acesso digno a serviços essenciais."
            ),
            "mapa": [
                "PPPPPPPPPPPPPPPPPPPP",
                "P.....P....P...P.P.P",
                "P.....D....B...P.P.P",
                "P.....P....P...P.P.P",
                "P...PPPPPPPPPPPP.P.P",
                "I.J.L...P...P..P.D.F",
                "P...P...D...P..B.P.P",
                "P...P...P...B..P.P.P",
                "P...P...P...P..P.P.P",
                "P...P...P...P..P.P.P",
                "PPPPPPPPPPPPPPPPPPPP",
            ],
        },
    ]

    _MAPA_SIMBOLOS: Dict[str, str] = {
        "L": TIPO_LIXEIRA,
        "D": TIPO_DEGRAU,
        "B": TIPO_BURACO,
        "P": TIPO_POSTE,
        "F": TIPO_DESTINO,
    }

    def __init__(self) -> None:
        """Inicializa o gerenciador na primeira fase e cria os grupos de sprites."""
        self.indice_atual: int = 0
        self.tempo_restante: float = 0.0
        self.recursos: int = 0
        self.intervencoes_fase: int = 0
        self.tentativas_teste_fase: int = 0
        self.erros_rota_fase: int = 0

        self.inicio_morador: Celula = (0, 5)
        self.inicio_jogador: Celula = (2, 5)
        self.destino: Celula = (COLS - 1, 5)

        # Grupos separados exclusivamente para consulta e colisão
        self.grupo_barreiras: pygame.sprite.Group = pygame.sprite.Group()
        self.grupo_solidos: pygame.sprite.Group = pygame.sprite.Group()
        self.grupo_interativos: pygame.sprite.Group = pygame.sprite.Group()

        self.metricas_fases: List[Dict[str, object]] = []

    @property
    def total_fases(self) -> int:
        """Retorna a quantidade total de fases cadastradas."""
        return len(self.FASES_INICIAIS)

    @property
    def metadados_atual(self) -> Dict[str, object]:
        """Retorna o dicionário completo de metadados da fase atual."""
        return self.FASES_INICIAIS[self.indice_atual]

    def reiniciar_campanha(
        self,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Reinicia o jogo desde a Fase 1 limpando o histórico de métricas.

        Args:
            modo_alto_contraste: Estado atual do modo de alto contraste.
            fonte_grande: Estado atual da escala de fonte.
        """
        self.indice_atual = 0
        self.metricas_fases = []
        self.carregar_fase(0, modo_alto_contraste, fonte_grande)

    def carregar_fase(
        self,
        indice: int,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Instancia os grupos de sprites e recursos a partir da matriz 20x11.

        Args:
            indice: Índice da fase baseado em zero (0 a total_fases - 1).
            modo_alto_contraste: Ativa renderização de alto contraste nos tiles.
            fonte_grande: Usa fonte ampliada nas siglas de alto contraste.
        """
        self.indice_atual = indice
        dados_fase = self.FASES_INICIAIS[indice]
        self.tempo_restante = float(dados_fase["tempo"])
        self.recursos = int(dados_fase["recursos"])
        self.intervencoes_fase = 0
        self.tentativas_teste_fase = 0
        self.erros_rota_fase = 0

        self.grupo_barreiras.empty()
        self.grupo_solidos.empty()
        self.grupo_interativos.empty()

        mapa = dados_fase["mapa"]
        if not isinstance(mapa, list) or len(mapa) != ROWS:
            raise ValueError(f"Mapa da fase {indice + 1} deve ter exatamente {ROWS} linhas.")

        for linha_idx, linha_texto in enumerate(mapa):
            if len(linha_texto) != COLS:
                raise ValueError(
                    f"Linha {linha_idx} da fase {indice + 1} deve ter {COLS} colunas."
                )
            for col_idx, simbolo in enumerate(linha_texto):
                if simbolo == "I":
                    self.inicio_morador = (col_idx, linha_idx)
                elif simbolo == "J":
                    self.inicio_jogador = (col_idx, linha_idx)
                elif simbolo in self._MAPA_SIMBOLOS:
                    tipo = self._MAPA_SIMBOLOS[simbolo]
                    barreira = Barreira(
                        col_idx,
                        linha_idx,
                        tipo,
                        modo_alto_contraste,
                        fonte_grande,
                    )
                    self.grupo_barreiras.add(barreira)
                    if barreira.eh_solida:
                        self.grupo_solidos.add(barreira)
                    if barreira.alteravel:
                        self.grupo_interativos.add(barreira)
                    if simbolo == "F":
                        self.destino = (col_idx, linha_idx)

    def reiniciar_fase(
        self,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Restaura integralmente o mapa, cronômetro e orçamento da fase atual.

        Args:
            modo_alto_contraste: Estado atual do modo de alto contraste.
            fonte_grande: Estado atual da escala de fonte.
        """
        self.carregar_fase(self.indice_atual, modo_alto_contraste, fonte_grande)

    def registrar_metricas_fase(self, concluida: bool) -> Dict[str, object]:
        """Registra as métricas de aprendizado observável da fase atual.

        Args:
            concluida: True se o Morador alcançou o destino; False se o tempo zerou.

        Returns:
            Dicionário com o resumo estruturado da fase registrada.
        """
        meta = self.metadados_atual
        autonomia = (
            "100% — Rota Contínua"
            if concluida and self.erros_rota_fase == 0
            else ("Alcançada com Ajustes" if concluida else "Bloqueada (Tempo Esgotado)")
        )

        registro: Dict[str, object] = {
            "numero": int(meta["numero"]),
            "nome": str(meta["nome"]),
            "intervencoes": self.intervencoes_fase,
            "tentativas_teste": self.tentativas_teste_fase,
            "erros_rota": self.erros_rota_fase,
            "tempo_restante": round(max(0.0, self.tempo_restante), 1),
            "recursos_restantes": self.recursos,
            "autonomia_alcancada": autonomia,
            "concluida": concluida,
        }

        for idx, existente in enumerate(self.metricas_fases):
            if existente["numero"] == registro["numero"]:
                self.metricas_fases[idx] = registro
                return registro

        self.metricas_fases.append(registro)
        return registro

    def avancar_fase(
        self,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> bool:
        """Carrega a próxima fase se houver.

        Args:
            modo_alto_contraste: Estado atual do modo de alto contraste.
            fonte_grande: Estado atual da escala de fonte.

        Returns:
            True se uma nova fase foi carregada; False ao fim da campanha.
        """
        if self.indice_atual + 1 < self.total_fases:
            self.carregar_fase(self.indice_atual + 1, modo_alto_contraste, fonte_grande)
            return True
        return False

    def obter_grade_barreiras(self) -> Dict[Celula, Barreira]:
        """Retorna um dicionário {(col, lin): Barreira} para consulta pelo BFS.

        Returns:
            Mapa associando cada célula ocupada à sua instância Barreira.
        """
        grade: Dict[Celula, Barreira] = {}
        for sprite in self.grupo_barreiras:
            if isinstance(sprite, Barreira):
                grade[(sprite.coluna, sprite.linha)] = sprite
        return grade

    def atualizar_visual_barreiras(
        self,
        modo_alto_contraste: bool,
        fonte_grande: bool = False,
    ) -> None:
        """Atualiza o visual de todos os tiles ao alternar contraste ou fonte.

        Args:
            modo_alto_contraste: True para alto contraste; False para padrão.
            fonte_grande: True para siglas ampliadas no alto contraste.
        """
        for sprite in self.grupo_barreiras:
            if isinstance(sprite, Barreira):
                sprite.atualizar_visual(modo_alto_contraste, fonte_grande)
