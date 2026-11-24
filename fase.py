"""Gerenciador das 4 fases progressivas, mapas 20x11 e avaliação de autonomia.

Implementa a classe GerenciadorFases com dificuldade crescente em 4 cenários
urbanos reais, validação de grupos de sprites e classificação qualitativa de
desempenho (Rota Segura, Rota Eficiente, Rota Exemplar — 1 a 3 Selos de
Acessibilidade) baseada em aprendizado observável (sem "só PBL").
"""

from typing import Dict, List, Tuple

import pygame

from barreira import Barreira
from config import (
    COLS,
    CUSTO_OTIMO_FASE_1,
    CUSTO_OTIMO_FASE_2,
    CUSTO_OTIMO_FASE_3,
    CUSTO_OTIMO_FASE_4,
    NIVEL_AUTONOMIA_BLOQUEADA,
    NIVEL_AUTONOMIA_EFICIENTE,
    NIVEL_AUTONOMIA_EXEMPLAR,
    NIVEL_AUTONOMIA_SEGURA,
    RECURSOS_FASE_1,
    RECURSOS_FASE_2,
    RECURSOS_FASE_3,
    RECURSOS_FASE_4,
    ROWS,
    TEMPO_FASE_1,
    TEMPO_FASE_2,
    TEMPO_FASE_3,
    TEMPO_FASE_4,
    TIPO_AVISO_SONORO,
    TIPO_BURACO,
    TIPO_DEGRAU,
    TIPO_DESTINO,
    TIPO_LIXEIRA,
    TIPO_POSTE,
    TIPO_SEM_PISO_TATIL,
)

Celula = Tuple[int, int]


class GerenciadorFases:
    """Controla as 4 fases progressivas, grupos de colisão e avaliação qualitativa."""

    # Legenda dos mapas 20x11:
    # '.' = faixa livre     | 'I' = início do Morador | 'J' = início de Alex
    # 'F' = destino         | 'P' = poste fixo        | 'L' = lixeira (0 rec)
    # 'D' = degrau (1 rec)  | 'B' = buraco (1 rec)    | 'T' = sem piso tátil (1)
    # 'S' = aviso sonoro (1)
    FASES_CAMPANHA: List[Dict[str, object]] = [
        {
            "numero": 1,
            "nome": "Calçada do Bairro",
            "perfil_morador": "Morador em cadeira de rodas",
            "tempo": TEMPO_FASE_1,
            "recursos": RECURSOS_FASE_1,
            "custo_otimo": CUSTO_OTIMO_FASE_1,
            "descricao": (
                "Morador cadeirante: desloque lixeiras (0 rec) e instale uma "
                "rampa no degrau para liberar uma faixa livre contínua."
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Faixa Livre: toda calçada deve manter faixa "
                "livre contínua de no mínimo 1,20 m sem mobiliário solto e "
                "com desníveis rebaixados para circulação autônoma."
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
            "perfil_morador": "Estudante em cadeira de rodas",
            "tempo": TEMPO_FASE_2,
            "recursos": RECURSOS_FASE_2,
            "custo_otimo": CUSTO_OTIMO_FASE_2,
            "descricao": (
                "Estudante cadeirante: contorne postes fixos em gargalos "
                "estreitos e resolva lixeiras, degraus e buraco no piso."
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Rota Acessível Contínua: postes pertencem à "
                "faixa de serviço. Em passagens estreitas, qualquer degrau ou "
                "buraco sem correção bloqueia o acesso à educação."
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
            "nome": "Praça Comunitária",
            "perfil_morador": "Morador surdo (acessibilidade comunicacional)",
            "tempo": TEMPO_FASE_3,
            "recursos": RECURSOS_FASE_3,
            "custo_otimo": CUSTO_OTIMO_FASE_3,
            "descricao": (
                "Morador surdo: elimine barreiras físicas e substitua avisos "
                "exclusivamente sonoros por painéis visuais acessíveis."
            ),
            "aprendizado": (
                "Lei nº 13.146/2015 (LBI) — Acessibilidade Comunicacional: "
                "alertas exclusivamente sonoros excluem pessoas surdas. Toda "
                "informação urbana essencial precisa combinar som e imagem."
            ),
            "mapa": [
                "PPPPPPPPPPPPPPPPPPPP",
                "P....P...P...P..P.PP",
                "P....L...P...P..P.PP",
                "P....P...P...P..P.PP",
                "I.J..P...P...D..P.PP",
                "P....P...P...P..S.LF",
                "P....P...P...P..P.PP",
                "P....P...S...P..P.PP",
                "P....P...P...P..P.PP",
                "P....P...P...P..P.PP",
                "PPPPPPPPPPPPPPPPPPPP",
            ],
        },
        {
            "numero": 4,
            "nome": "Caminho ao Posto de Saúde",
            "perfil_morador": "Morador com baixa visão / cadeirante",
            "tempo": TEMPO_FASE_4,
            "recursos": RECURSOS_FASE_4,
            "custo_otimo": CUSTO_OTIMO_FASE_4,
            "descricao": (
                "Orçamento contado (5 rec): inspecione o mapa antes de agir! "
                "O corredor superior termina fechado por postes fixos."
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Desenho Universal e Planejamento: combinar "
                "piso tátil direcional, rampas e pavimento nivelado com "
                "diagnóstico prévio da rota evita desperdício de orçamento."
            ),
            "mapa": [
                "PPPPPPPPPPPPPPPPPPPP",
                "P....P....P....P.P.P",
                "P....D....B....P.P.P",
                "P....P....P....P.P.P",
                "P..PPPPPPPPPPPPP.P.P",
                "I.JL..P..P..P..P.T.F",
                "P..P..D..P..T..P.P.P",
                "P..P..P..B..P..D.P.P",
                "P..P..P..P..P..P.P.P",
                "P..P..P..P..P..P.P.P",
                "PPPPPPPPPPPPPPPPPPPP",
            ],
        },
    ]

    _MAPA_SIMBOLOS: Dict[str, str] = {
        "L": TIPO_LIXEIRA,
        "D": TIPO_DEGRAU,
        "B": TIPO_BURACO,
        "T": TIPO_SEM_PISO_TATIL,
        "S": TIPO_AVISO_SONORO,
        "P": TIPO_POSTE,
        "F": TIPO_DESTINO,
    }

    def __init__(self) -> None:
        """Inicializa o gerenciador na Fase 1 com os grupos de sprites vazios."""
        self.indice_atual: int = 0
        self.tempo_restante: float = 0.0
        self.recursos: int = 0
        self.recursos_iniciais: int = 0
        self.intervencoes_fase: int = 0
        self.tentativas_teste_fase: int = 0
        self.erros_rota_fase: int = 0

        self.inicio_morador: Celula = (0, 5)
        self.inicio_jogador: Celula = (2, 5)
        self.destino: Celula = (COLS - 1, 5)

        self.grupo_barreiras: pygame.sprite.Group = pygame.sprite.Group()
        self.grupo_solidos: pygame.sprite.Group = pygame.sprite.Group()
        self.grupo_interativos: pygame.sprite.Group = pygame.sprite.Group()

        self.metricas_fases: List[Dict[str, object]] = []

    @property
    def total_fases(self) -> int:
        """Retorna a quantidade total de fases da campanha (4 fases)."""
        return len(self.FASES_CAMPANHA)

    @property
    def metadados_atual(self) -> Dict[str, object]:
        """Retorna o dicionário de metadados da fase atual."""
        return self.FASES_CAMPANHA[self.indice_atual]

    def reiniciar_campanha(
        self,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Reinicia a campanha desde a Fase 1 limpando as métricas da sessão.

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
        """Carrega o mapa 20x11, tempo, orçamento e grupos da fase informada.

        Args:
            indice: Índice da fase baseado em zero (0 a 3).
            modo_alto_contraste: Ativa renderização de alto contraste nos tiles.
            fonte_grande: Usa fonte ampliada nas siglas de alto contraste.
        """
        self.indice_atual = indice
        dados_fase = self.FASES_CAMPANHA[indice]
        self.tempo_restante = float(dados_fase["tempo"])
        self.recursos = int(dados_fase["recursos"])
        self.recursos_iniciais = self.recursos
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

    def classificar_autonomia(self, concluida: bool) -> Tuple[str, int]:
        """Classifica qualitativamente o desempenho na fase em Selos de Acessibilidade.

        Avalia autonomia observável (erros de rota evitados e eficiência no uso
        do orçamento limitado), evitando pontuação genérica sem significado:
        - 3 Selos ('Rota Exemplar'): 0 erros de rota e gasto dentro do custo ótimo.
        - 2 Selos ('Rota Eficiente'): até 1 erro de rota ou eficiência parcial.
        - 1 Selo ('Rota Segura'): rota contínua concluída com múltiplos ajustes.
        - 0 Selos ('Rota Bloqueada'): tempo esgotado antes de liberar a rota.

        Args:
            concluida: True se o Morador chegou ao destino; False caso contrário.

        Returns:
            Tupla (nome_nivel_autonomia, quantidade_selos).
        """
        if not concluida:
            return NIVEL_AUTONOMIA_BLOQUEADA, 0

        recursos_gastos = self.recursos_iniciais - self.recursos
        custo_otimo = int(self.metadados_atual["custo_otimo"])

        if self.erros_rota_fase == 0 and recursos_gastos <= custo_otimo:
            return NIVEL_AUTONOMIA_EXEMPLAR, 3
        if self.erros_rota_fase <= 1 and recursos_gastos <= custo_otimo + 1:
            return NIVEL_AUTONOMIA_EFICIENTE, 2
        return NIVEL_AUTONOMIA_SEGURA, 1

    def registrar_metricas_fase(self, concluida: bool) -> Dict[str, object]:
        """Registra as métricas de aprendizado e nível de autonomia da fase atual.

        Args:
            concluida: True se a fase foi concluída; False em tempo esgotado.

        Returns:
            Dicionário com o resumo completo da fase registrada.
        """
        meta = self.metadados_atual
        nivel_autonomia, selos = self.classificar_autonomia(concluida)
        recursos_gastos = self.recursos_iniciais - self.recursos

        registro: Dict[str, object] = {
            "numero": int(meta["numero"]),
            "nome": str(meta["nome"]),
            "perfil_morador": str(meta["perfil_morador"]),
            "intervencoes": self.intervencoes_fase,
            "recursos_gastos": recursos_gastos,
            "tentativas_teste": self.tentativas_teste_fase,
            "erros_rota": self.erros_rota_fase,
            "tempo_restante": round(max(0.0, self.tempo_restante), 1),
            "recursos_restantes": self.recursos,
            "autonomia_alcancada": f"{nivel_autonomia} ({selos}/3)",
            "nivel_autonomia": nivel_autonomia,
            "selos": selos,
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
        """Avança para a próxima fase caso ainda haja fases restantes.

        Args:
            modo_alto_contraste: Estado atual do modo de alto contraste.
            fonte_grande: Estado atual da escala de fonte.

        Returns:
            True se carregou a próxima fase; False se concluiu todas as 4 fases.
        """
        if self.indice_atual + 1 < self.total_fases:
            self.carregar_fase(self.indice_atual + 1, modo_alto_contraste, fonte_grande)
            return True
        return False

    def obter_grade_barreiras(self) -> Dict[Celula, Barreira]:
        """Constrói o dicionário {(col, lin): Barreira} para o algoritmo BFS.

        Returns:
            Mapa de todas as células atualmente ocupadas por sprites Barreira.
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
