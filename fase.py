"""Gerenciador das 4 fases ambientadas em Maricá/RJ, mapas 20x11 e autonomia.

Cada fase representa um local real de Maricá/RJ (Orla de Araçatiba, Escola
Municipal do Centro, Praça Orlando de Barros Pimentel e Caminho ao Posto de
Saúde de Itaipuaçu) com calçadas amplas, bordas cênicas livres e moradores
100% coerentes com as barreiras do cenário.
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
    PERFIL_BAIXA_VISAO,
    PERFIL_CADEIRANTE,
    PERFIL_SURDO,
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
    """Controla as 4 fases de Maricá/RJ, grupos de colisão e avaliação qualitativa."""

    # Legenda dos mapas 20x11 (linhas 0 e 10 são faixas cênicas: lagoa/jardim e rua/Vermelhinho):
    # '.' = calçada livre   | 'I' = início do Morador | 'J' = início de Alex
    # 'F' = destino         | 'P' = canteiro/poste    | 'L' = lixeira (0 rec)
    # 'D' = degrau (1 rec)  | 'B' = buraco (1 rec)    | 'T' = sem piso tátil (1)
    # 'S' = aviso sonoro (1)
    FASES_CAMPANHA: List[Dict[str, object]] = [
        {
            "numero": 1,
            "nome": "Orla de Araçatiba",
            "local_destino": "PONTO VERMELHINHO",
            "perfil_id": PERFIL_CADEIRANTE,
            "nome_morador": "Clara",
            "perfil_morador": "Clara — Moradora em cadeira de rodas",
            "tempo": TEMPO_FASE_1,
            "recursos": RECURSOS_FASE_1,
            "custo_otimo": CUSTO_OTIMO_FASE_1,
            "descricao": (
                "Clara (Araçatiba): 'Preciso pegar o Vermelhinho, mas lixeiras "
                "e um degrau sem rampa bloqueiam o calçadão da lagoa!'"
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Faixa Livre na Orla: toda calçada precisa de "
                "faixa livre contínua de no mínimo 1,20 m, sem lixeiras soltas "
                "e com rampa acessível para garantir autonomia até o transporte."
            ),
            "mapa": [
                "....................",
                "......P.....P...P...",
                "......P.....P...P...",
                "......P.....P...P...",
                "......L.....P...P...",
                "I..J..L.....D...L..F",
                "......P.....P...L...",
                "......P.....P...P...",
                "......P.....P...P...",
                "......P.....P...P...",
                "....................",
            ],
        },
        {
            "numero": 2,
            "nome": "Escola no Centro de Maricá",
            "local_destino": "ESCOLA MUNICIPAL",
            "perfil_id": PERFIL_CADEIRANTE,
            "nome_morador": "Lucas",
            "perfil_morador": "Lucas — Estudante em cadeira de rodas",
            "tempo": TEMPO_FASE_2,
            "recursos": RECURSOS_FASE_2,
            "custo_otimo": CUSTO_OTIMO_FASE_2,
            "descricao": (
                "Lucas (Centro): 'Os canteiros estreitam a calçada e os degraus "
                "com buraco impedem minha entrada na escola!'"
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Rota Acessível Contínua: mobiliário fixo deve "
                "ficar na faixa de serviço. Em gargalos estreitos, qualquer "
                "degrau ou buraco sem correção bloqueia o acesso à educação."
            ),
            "mapa": [
                "....................",
                ".....P..P...P..P.P..",
                ".....L..P...P..P.P..",
                ".....L..P...P..P.P..",
                "I.J..P..P...D..P.P..",
                ".....P..P...P..P.B.F",
                ".....P..L...P..D.P..",
                ".....P..L...P..P.P..",
                ".....P..P...P..P.P..",
                ".....P..P...P..P.P..",
                "....................",
            ],
        },
        {
            "numero": 3,
            "nome": "Praça Orlando de Barros Pimentel",
            "local_destino": "PALCO DA PRAÇA",
            "perfil_id": PERFIL_SURDO,
            "nome_morador": "Sofia",
            "perfil_morador": "Sofia — Moradora surda (comunicação visual)",
            "tempo": TEMPO_FASE_3,
            "recursos": RECURSOS_FASE_3,
            "custo_otimo": CUSTO_OTIMO_FASE_3,
            "descricao": (
                "Sofia (Praça Central): 'Os avisos do evento são só por "
                "alto-falante! Instale painéis visuais para eu me orientar.'"
            ),
            "aprendizado": (
                "Lei nº 13.146/2015 (LBI) — Acessibilidade Comunicacional: "
                "avisos exclusivamente sonoros excluem pessoas surdas. Toda "
                "informação urbana essencial precisa combinar som e painel visual."
            ),
            "mapa": [
                "....................",
                ".....P...P...P..P...",
                ".....L...P...P..P...",
                ".....L...P...P..P...",
                "I.J..P...P...S..P...",
                ".....P...P...P..S.LF",
                ".....P...P...P..P...",
                ".....P...S...P..P...",
                ".....P...P...P..P...",
                ".....P...P...P..P...",
                "....................",
            ],
        },
        {
            "numero": 4,
            "nome": "Posto de Saúde — Itaipuaçu",
            "local_destino": "POSTO DE SAÚDE",
            "perfil_id": PERFIL_BAIXA_VISAO,
            "nome_morador": "Mateus",
            "perfil_morador": "Mateus — Baixa visão (bengala branca)",
            "tempo": TEMPO_FASE_4,
            "recursos": RECURSOS_FASE_4,
            "custo_otimo": CUSTO_OTIMO_FASE_4,
            "descricao": (
                "Mateus (Itaipuaçu): 'Preciso de piso tátil e piso sem buracos! "
                "Orçamento contado (5 rec): cheque o corredor de cima antes!'"
            ),
            "aprendizado": (
                "ABNT NBR 9050 — Orientação Tátil e Planejamento: piso tátil "
                "direcional e pavimento nivelado garantem autonomia com bengala "
                "branca; diagnosticar a rota evita gastar orçamento em becos."
            ),
            "mapa": [
                "....................",
                ".....P....P....P.P..",
                ".....T....B....P.P..",
                ".....P....P....P.P..",
                "...PPPPPPPPPPPPP.P..",
                "I.JL..P..P..P..P.T.F",
                "...P..T..P..T..P.P..",
                "...P..P..B..P..B.P..",
                "...P..P..P..P..P.P..",
                "...P..P..P..P..P.P..",
                "....................",
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
        """Reinicia a campanha desde a Fase 1 limpando as métricas da sessão."""
        self.indice_atual = 0
        self.metricas_fases = []
        self.carregar_fase(0, modo_alto_contraste, fonte_grande)

    def carregar_fase(
        self,
        indice: int,
        modo_alto_contraste: bool = False,
        fonte_grande: bool = False,
    ) -> None:
        """Carrega o mapa 20x11, tempo, orçamento e grupos da fase informada."""
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
        """Restaura integralmente o mapa, cronômetro e orçamento da fase atual."""
        self.carregar_fase(self.indice_atual, modo_alto_contraste, fonte_grande)

    def classificar_autonomia(self, concluida: bool) -> Tuple[str, int]:
        """Classifica qualitativamente o desempenho na fase em Selos de Acessibilidade."""
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
        """Registra as métricas de aprendizado e nível de autonomia da fase atual."""
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
        """Avança para a próxima fase caso ainda haja fases restantes."""
        if self.indice_atual + 1 < self.total_fases:
            self.carregar_fase(self.indice_atual + 1, modo_alto_contraste, fonte_grande)
            return True
        return False

    def obter_lista_fases(self) -> List[Dict[str, object]]:
        """Retorna resumo das fases da campanha para seleção no Mapa de Maricá."""
        return [
            {
                "numero": int(fase["numero"]),
                "nome": str(fase["nome"]),
                "perfil_morador": str(fase["perfil_morador"]),
                "tempo": float(fase["tempo"]),
                "recursos": int(fase["recursos"]),
            }
            for fase in self.FASES_CAMPANHA
        ]

    def obter_grade_barreiras(self) -> Dict[Celula, Barreira]:
        """Constrói o dicionário {(col, lin): Barreira} para o algoritmo BFS."""
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
        """Atualiza o visual de todos os tiles ao alternar contraste ou fonte."""
        for sprite in self.grupo_barreiras:
            if isinstance(sprite, Barreira):
                sprite.atualizar_visual(modo_alto_contraste, fonte_grande)
