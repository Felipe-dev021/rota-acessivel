"""Módulo de interface (HUD) e telas de estado do jogo 'Rota Acessível'.

Implementa a classe HUD responsável por desenhar a calçada urbana, a barra
superior (96 px), o feedback educativo inferior temporário ('[OK]' / '[!]'),
o destaque de interação '[E]' e as telas completas de MENU, INSTRUCOES, PAUSA,
TRANSICAO e FIM com suporte integral ao Modo Alto Contraste.
"""

import math
from typing import Dict, List, Optional, Tuple

import pygame

from barreira import Barreira
from config import (
    ALTURA,
    ALTURA_FEEDBACK,
    BORDA_ALTO_CONTRASTE,
    COLS,
    CORES_ALTO_CONTRASTE,
    CORES_NORMAL,
    FONTE_FAMILIA,
    FONTES_GRANDE,
    FONTES_NORMAL,
    HUD_ALTURA,
    LARGURA,
    ROWS,
    TEMPO_ALERTA_CRITICO,
    TILE,
    TIPO_AVISO_SONORO,
    TIPO_BURACO,
    TIPO_DEGRAU,
    TIPO_DESTINO,
    TIPO_LIXEIRA,
    TIPO_PISO_OK,
    TIPO_POSTE,
    TIPO_RAMPA,
    TIPO_SEM_PISO_TATIL,
    caminho_arquivo,
)


class HUD:
    """Gerencia a renderização da interface, grade da calçada e telas de estado."""

    def __init__(self) -> None:
        """Inicializa as fontes, o estado do feedback e as miniaturas de legenda."""
        self.fonte_grande: bool = False
        self.fonte_titulo: pygame.font.Font
        self.fonte_subtitulo: pygame.font.Font
        self.fonte_media: pygame.font.Font
        self.fonte_normal: pygame.font.Font
        self.fonte_pequena: pygame.font.Font
        self.atualizar_fontes(False)

        self.mensagem_feedback: str = ""
        self.tipo_feedback: str = "OK"
        self.tempo_feedback: float = 0.0
        self.tempo_animacao: float = 0.0

        self._miniaturas_legenda: Dict[str, pygame.Surface] = {}
        self._carregar_miniaturas_legenda()

    def atualizar_fontes(self, fonte_grande: bool) -> None:
        """Recria as fontes da interface na escala Normal ou Grande em tempo real.

        Args:
            fonte_grande: True aplica FONTES_GRANDE; False aplica FONTES_NORMAL.
        """
        self.fonte_grande = fonte_grande
        escala = FONTES_GRANDE if fonte_grande else FONTES_NORMAL
        self.fonte_titulo = pygame.font.SysFont(
            FONTE_FAMILIA, escala["titulo"], bold=True
        )
        self.fonte_subtitulo = pygame.font.SysFont(
            FONTE_FAMILIA, escala["subtitulo"], bold=True
        )
        self.fonte_media = pygame.font.SysFont(
            FONTE_FAMILIA, escala["media"], bold=True
        )
        self.fonte_normal = pygame.font.SysFont(FONTE_FAMILIA, escala["normal"])
        self.fonte_pequena = pygame.font.SysFont(
            FONTE_FAMILIA, escala["pequena"], bold=True
        )

    def _carregar_miniaturas_legenda(self) -> None:
        """Carrega os sprites PNG via caminho_arquivo() para a legenda visual."""
        tipos_legenda = (
            TIPO_LIXEIRA,
            TIPO_DEGRAU,
            TIPO_BURACO,
            TIPO_SEM_PISO_TATIL,
            TIPO_AVISO_SONORO,
            TIPO_POSTE,
            TIPO_RAMPA,
            TIPO_PISO_OK,
            TIPO_DESTINO,
        )
        for tipo in tipos_legenda:
            if tipo not in Barreira.TABELA_TIPOS:
                continue
            arquivo = str(Barreira.TABELA_TIPOS[tipo]["sprite"])
            imagem = pygame.image.load(caminho_arquivo(arquivo))
            if pygame.display.get_surface() is not None:
                imagem = imagem.convert_alpha()
            self._miniaturas_legenda[tipo] = pygame.transform.smoothscale(
                imagem, (30, 30)
            )

    def paleta(self, modo_alto_contraste: bool) -> Dict[str, Tuple[int, ...]]:
        """Retorna a paleta ativa conforme o modo de alto contraste.

        Args:
            modo_alto_contraste: True retorna CORES_ALTO_CONTRASTE; False retorna CORES_NORMAL.

        Returns:
            Dicionário de cores RGB/RGBA.
        """
        return CORES_ALTO_CONTRASTE if modo_alto_contraste else CORES_NORMAL

    def definir_feedback(self, mensagem: str, tipo: str, duracao: float) -> None:
        """Configura a mensagem educativa temporária da faixa inferior.

        Args:
            mensagem: Texto explicativo a ser exibido.
            tipo: 'OK' para sucesso/informação ou 'ERRO' para alerta/bloqueio.
            duracao: Tempo em segundos que a mensagem permanecerá visível.
        """
        self.mensagem_feedback = mensagem
        self.tipo_feedback = tipo
        self.tempo_feedback = duracao

    def limpar_feedback(self) -> None:
        """Limpa imediatamente qualquer mensagem educativa ativa."""
        self.mensagem_feedback = ""
        self.tempo_feedback = 0.0

    def atualizar(self, dt: float) -> None:
        """Atualiza o temporizador do feedback inferior e o relógio de animações.

        Args:
            dt: Tempo decorrido em segundos desde o frame anterior.
        """
        self.tempo_animacao += dt
        if self.tempo_feedback > 0.0:
            self.tempo_feedback = max(0.0, self.tempo_feedback - dt)
            if self.tempo_feedback == 0.0:
                self.mensagem_feedback = ""

    def _quebrar_texto(
        self,
        texto: str,
        fonte: pygame.font.Font,
        largura_max: int,
    ) -> List[str]:
        """Divide um texto longo em múltiplas linhas que respeitem largura_max."""
        palavras = texto.split()
        linhas: List[str] = []
        linha_atual = ""

        for palavra in palavras:
            candidata = f"{linha_atual} {palavra}".strip()
            if fonte.size(candidata)[0] <= largura_max:
                linha_atual = candidata
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    def _desenhar_texto_quebrado(
        self,
        tela: pygame.Surface,
        texto: str,
        fonte: pygame.font.Font,
        cor: Tuple[int, ...],
        x: int,
        y: int,
        largura_max: int,
        espacamento: int = 4,
    ) -> int:
        """Renderiza texto com quebra de linha automática e retorna o Y final."""
        y_atual = y
        for linha in self._quebrar_texto(texto, fonte, largura_max):
            superficie = fonte.render(linha, True, cor)
            tela.blit(superficie, (x, y_atual))
            y_atual += superficie.get_height() + espacamento
        return y_atual

    def desenhar_grade_calcada(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a via urbana 20x11 com faixa de serviço nas bordas e calçada central."""
        cores = self.paleta(modo_alto_contraste)
        for lin in range(ROWS):
            eh_borda_servico = lin == 0 or lin == ROWS - 1
            for col in range(COLS):
                if eh_borda_servico:
                    cor = cores["faixa_servico"]
                else:
                    cor = (
                        cores["calcada_clara"]
                        if (lin + col) % 2 == 0
                        else cores["calcada_escura"]
                    )
                ret = pygame.Rect(col * TILE, HUD_ALTURA + lin * TILE, TILE, TILE)
                pygame.draw.rect(tela, cor, ret)
                pygame.draw.rect(tela, cores["grade_linha"], ret, 1)

    def desenhar_marcadores_rota(
        self,
        tela: pygame.Surface,
        inicio_morador: Tuple[int, int],
        destino: Tuple[int, int],
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha marcações visuais nítidas de PARTIDA e DESTINO sobre a calçada.

        Args:
            tela: Superfície principal do jogo.
            inicio_morador: Célula (col, lin) de partida do Morador.
            destino: Célula (col, lin) do destino da fase.
            modo_alto_contraste: Estado atual do modo de alto contraste.
        """
        cores = self.paleta(modo_alto_contraste)
        marcadores = (
            (inicio_morador, "PARTIDA", cores["partida_marcador"]),
            (destino, "DESTINO", cores["destino_marcador"]),
        )
        for (col, lin), rotulo, cor_fundo in marcadores:
            cx = col * TILE + TILE // 2
            topo_tile = HUD_ALTURA + lin * TILE
            cor_texto = (
                cores["destaque_e_texto"]
                if modo_alto_contraste
                else cores["texto_principal"]
            )
            txt = self.fonte_pequena.render(rotulo, True, cor_texto)
            caixa = txt.get_rect(midbottom=(cx, max(HUD_ALTURA + 20, topo_tile - 2)))
            caixa.clamp_ip(
                pygame.Rect(4, HUD_ALTURA + 2, LARGURA - 8, ALTURA - HUD_ALTURA - 4)
            )
            fundo = caixa.inflate(8, 4)
            pygame.draw.rect(tela, cor_fundo, fundo, border_radius=4)
            pygame.draw.rect(tela, cores["tile_borda"], fundo, 1, border_radius=4)
            tela.blit(txt, caixa)

    def desenhar_rastro_morador(
        self,
        tela: pygame.Surface,
        celulas_percorridas: List[Tuple[int, int]],
        rota_sucesso: bool,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha um rastro pontilhado mostrando o trajeto percorrido pelo Morador.

        Args:
            tela: Superfície principal do jogo.
            celulas_percorridas: Lista de células (col, lin) já atravessadas.
            rota_sucesso: True destaca em verde de rota livre; False em azul-alerta.
            modo_alto_contraste: Estado atual do modo de alto contraste.
        """
        if len(celulas_percorridas) < 2:
            return
        cores = self.paleta(modo_alto_contraste)
        cor_rastro = cores["rota_livre"] if rota_sucesso else cores["rota_preview"]

        for indice in range(len(celulas_percorridas) - 1):
            c1, l1 = celulas_percorridas[indice]
            c2, l2 = celulas_percorridas[indice + 1]
            x1 = c1 * TILE + TILE // 2
            y1 = HUD_ALTURA + l1 * TILE + TILE // 2
            x2 = c2 * TILE + TILE // 2
            y2 = HUD_ALTURA + l2 * TILE + TILE // 2

            for passo in range(3):
                t = passo / 3.0
                px = round(x1 + (x2 - x1) * t)
                py = round(y1 + (y2 - y1) * t)
                pygame.draw.circle(tela, cor_rastro, (px, py), 5)
                pygame.draw.circle(tela, cores["tile_borda"], (px, py), 5, 1)

    def desenhar_destaque_interacao(
        self,
        tela: pygame.Surface,
        barreira: Optional[Barreira],
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha moldura pulsante senoidal '[E] + ação e custo' sobre a barreira próxima."""
        if barreira is None:
            return
        cores = self.paleta(modo_alto_contraste)
        pulso = 0.5 + 0.5 * math.sin(self.tempo_animacao * 5.0)
        expansao = round(2 + 4 * pulso)
        espessura = 3 + round(2 * pulso)
        ret_pulsante = barreira.rect.inflate(expansao, expansao)
        pygame.draw.rect(tela, cores["destaque_e"], ret_pulsante, espessura, border_radius=7)

        etiqueta = barreira.texto_prompt_interacao()
        texto = self.fonte_pequena.render(etiqueta, True, cores["destaque_e_texto"])
        caixa = texto.get_rect(
            midbottom=(
                barreira.rect.centerx,
                max(HUD_ALTURA + 24, ret_pulsante.top - 3),
            )
        )
        caixa.clamp_ip(pygame.Rect(8, HUD_ALTURA + 4, LARGURA - 16, ALTURA - HUD_ALTURA - 8))
        caixa_fundo = caixa.inflate(12, 6)
        pygame.draw.rect(tela, cores["destaque_e"], caixa_fundo, border_radius=5)
        pygame.draw.rect(tela, cores["destaque_e_texto"], caixa_fundo, 2, border_radius=5)
        tela.blit(texto, caixa)

    def desenhar_barra_superior(
        self,
        tela: pygame.Surface,
        numero_fase: int,
        total_fases: int,
        nome_fase: str,
        tempo_restante: float,
        recursos: int,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        testando_rota: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha o HUD superior (96 px) com fase, cronômetro, orçamento e acessibilidade."""
        cores = self.paleta(modo_alto_contraste)
        ret_hud = pygame.Rect(0, 0, LARGURA, HUD_ALTURA)
        pygame.draw.rect(tela, cores["hud_fundo"], ret_hud)
        borda = BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3
        pygame.draw.line(
            tela, cores["hud_borda"], (0, HUD_ALTURA - 2), (LARGURA, HUD_ALTURA - 2), borda
        )

        # Linha 1: Nome da fase, Cronômetro (alerta <= 15s) e Recursos
        titulo_fase = self.fonte_media.render(
            f"F{numero_fase}/{total_fases}: {nome_fase}",
            True,
            cores["texto_principal"],
        )
        tela.blit(titulo_fase, (14, 12))

        critico = tempo_restante <= TEMPO_ALERTA_CRITICO
        cor_tempo = cores["erro_borda"] if critico else cores["texto_principal"]
        prefixo_tempo = "[!] " if critico else ""
        txt_tempo = self.fonte_media.render(
            f"{prefixo_tempo}Tempo: {max(0.0, tempo_restante):04.1f}s",
            True,
            cor_tempo,
        )
        tela.blit(txt_tempo, (440, 12))

        cor_rec = cores["aviso"] if recursos == 0 else cores["texto_principal"]
        txt_rec = self.fonte_media.render(
            f"Recursos: {recursos}",
            True,
            cor_rec,
        )
        tela.blit(txt_rec, (670, 12))

        status_rota = "TESTANDO..." if testando_rota else "[ESPAÇO] Testar"
        txt_rota = self.fonte_pequena.render(status_rota, True, cores["destaque_e"])
        tela.blit(txt_rota, (LARGURA - txt_rota.get_width() - 14, 14))

        # Linha 2: Atalhos e indicadores completos de acessibilidade (C, F, M, N)
        contraste_txt = "ALTO" if modo_alto_contraste else "NORM"
        fonte_txt = "G" if self.fonte_grande else "N"
        som_txt = "ON" if audio_ativo else "OFF"
        mus_txt = "ON" if (audio_ativo and musica_ativa) else "OFF"

        linha_ctrl = (
            f"[WASD] Mover  [E] Intervir  [R] Reiniciar  [P] Pausa   |   "
            f"[C] Contr:{contraste_txt}  [F] Fonte:{fonte_txt}  [M] Som:{som_txt}  [N] Mus:{mus_txt}"
        )
        txt_ctrl = self.fonte_pequena.render(linha_ctrl, True, cores["texto_secundario"])
        tela.blit(txt_ctrl, (14, 58))

    def desenhar_feedback_inferior(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a faixa educativa inferior temporária com prefixo '[OK]' ou '[!]'."""
        if not self.mensagem_feedback or self.tempo_feedback <= 0.0:
            return

        cores = self.paleta(modo_alto_contraste)
        eh_ok = self.tipo_feedback == "OK"
        cor_fundo = cores["sucesso_fundo"] if eh_ok else cores["erro_fundo"]
        cor_borda = cores["sucesso_borda"] if eh_ok else cores["erro_borda"]
        prefixo = "[OK] " if eh_ok else "[!] "

        ret = pygame.Rect(16, ALTURA - ALTURA_FEEDBACK - 10, LARGURA - 32, ALTURA_FEEDBACK)
        pygame.draw.rect(tela, cor_fundo, ret, border_radius=8)
        pygame.draw.rect(tela, cor_borda, ret, 3, border_radius=8)

        self._desenhar_texto_quebrado(
            tela,
            prefixo + self.mensagem_feedback,
            self.fonte_normal,
            cores["texto_principal"],
            ret.x + 14,
            ret.y + 8,
            ret.width - 28,
            espacamento=2,
        )

    def desenhar_menu(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha a tela inicial (MENU) com opções legíveis e acessíveis."""
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(84, 42, LARGURA - 168, ALTURA - 84)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=14)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            painel,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=14,
        )

        titulo = self.fonte_titulo.render("ROTA ACESSÍVEL", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 98)))

        subtitulo = self.fonte_subtitulo.render(
            "Tema 07 — Acessibilidade e Inclusão Urbana (ABNT NBR 9050)",
            True,
            cores["texto_principal"],
        )
        tela.blit(subtitulo, subtitulo.get_rect(center=(LARGURA // 2, 142)))

        self._desenhar_texto_quebrado(
            tela,
            (
                "Ajude Alex a remover barreiras físicas, visuais e comunicacionais "
                "com orçamento limitado para garantir autonomia real até o destino."
            ),
            self.fonte_normal,
            cores["texto_secundario"],
            painel.x + 48,
            176,
            painel.width - 96,
            espacamento=4,
        )

        opcoes = [
            "[ENTER / ESPAÇO]  Iniciar Campanha (4 Fases)",
            "[I]  Instruções e Legenda Visual",
            f"[C]  Alto Contraste: {'ATIVADO' if modo_alto_contraste else 'DESATIVADO'}   |   [F]  Fonte: {'GRANDE' if self.fonte_grande else 'NORMAL'}",
            f"[M]  Áudio: {'LIGADO' if audio_ativo else 'MUDO'}   |   [N]  Música: {'LIGADA' if (audio_ativo and musica_ativa) else 'MUDA'}",
            "[ESC]  Sair do Jogo",
        ]
        y = 266
        for texto in opcoes:
            caixa = pygame.Rect(150, y, LARGURA - 300, 44)
            pygame.draw.rect(tela, cores["botao_fundo"], caixa, border_radius=8)
            pygame.draw.rect(tela, cores["botao_borda"], caixa, 2, border_radius=8)
            render = self.fonte_media.render(texto, True, cores["texto_principal"])
            tela.blit(render, render.get_rect(center=caixa.center))
            y += 54

    def desenhar_instrucoes(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a tela INSTRUCOES com legenda visual de obstáculos e controles."""
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(34, 24, LARGURA - 68, ALTURA - 48)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=12)
        pygame.draw.rect(tela, cores["painel_borda"], painel, 3, border_radius=12)

        titulo = self.fonte_subtitulo.render(
            "INSTRUÇÕES E LEGENDA DE OBSTÁCULOS",
            True,
            cores["destaque_e"],
        )
        tela.blit(titulo, (58, 42))

        legenda_itens = [
            (TIPO_LIXEIRA, "Lixeira (L): deslocar da faixa livre — 0 rec"),
            (TIPO_DEGRAU, "Degrau (D): instalar rampa acessível — 1 rec"),
            (TIPO_BURACO, "Buraco (B): nivelar pavimento — 1 rec"),
            (TIPO_SEM_PISO_TATIL, "Sem Piso Tátil (T): instalar piso tátil — 1 rec"),
            (TIPO_AVISO_SONORO, "Aviso Sonoro (S): instalar painel visual — 1 rec"),
            (TIPO_POSTE, "Poste fixo (P): intransponível — exige desvio"),
            (TIPO_RAMPA, "Rampa (R) / Piso OK: passagem livre"),
            (TIPO_DESTINO, "Destino (FIM): ponto de chegada"),
        ]

        y = 84
        for tipo, descricao in legenda_itens:
            if modo_alto_contraste:
                quad = pygame.Rect(52, y, 30, 30)
                pygame.draw.rect(tela, cores[f"tile_{tipo}"], quad, border_radius=4)
                pygame.draw.rect(tela, cores["tile_borda"], quad, 2, border_radius=4)
                sigla = str(Barreira.TABELA_TIPOS[tipo]["sigla"])
                txt_s = self.fonte_pequena.render(sigla, True, cores["tile_sigla"])
                tela.blit(txt_s, txt_s.get_rect(center=quad.center))
            elif tipo in self._miniaturas_legenda:
                tela.blit(self._miniaturas_legenda[tipo], (52, y))

            txt_desc = self.fonte_normal.render(descricao, True, cores["texto_principal"])
            tela.blit(txt_desc, (92, y + 5))
            y += 46

        x_dir = 528
        sec_ctrl = self.fonte_media.render("CONTROLES E ACESSIBILIDADE", True, cores["destaque_e"])
        tela.blit(sec_ctrl, (x_dir, 84))

        controles = [
            "WASD ou Setas: mover Alex",
            "E: intervir na barreira [E]",
            "ESPAÇO / ENTER: testar rota (BFS)",
            "R: reiniciar a fase atual",
            "P / ESC: pausar sem limite de tempo",
            "C: alternar Modo Alto Contraste",
            "F: alternar Fonte (Normal / Grande)",
            "M: silenciar áudio | N: silenciar música",
        ]
        y_ctrl = 116
        for item in controles:
            render = self.fonte_normal.render(f"• {item}", True, cores["texto_principal"])
            tela.blit(render, (x_dir, y_ctrl))
            y_ctrl += 28

        sec_obj = self.fonte_media.render("OBJETIVO DO SERIOUS GAME", True, cores["destaque_e"])
        tela.blit(sec_obj, (x_dir, 354))
        self._desenhar_texto_quebrado(
            tela,
            (
                "Garanta uma faixa livre contínua até o Destino gerenciando "
                "o orçamento limitado. Cada bloqueio explica o impacto real "
                "na autonomia e desconta 5s."
            ),
            self.fonte_normal,
            cores["texto_secundario"],
            x_dir,
            382,
            378,
            espacamento=4,
        )

        rodape = self.fonte_media.render(
            "[ENTER / ESPAÇO] Começar     |     [ESC / BACKSPACE] Voltar ao Menu",
            True,
            cores["destaque_e"],
        )
        tela.blit(rodape, rodape.get_rect(center=(LARGURA // 2, ALTURA - 54)))

    def desenhar_pausa(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha o overlay de PAUSA preservando a visualização do mapa ao fundo."""
        cores = self.paleta(modo_alto_contraste)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill(cores["overlay"])
        tela.blit(overlay, (0, 0))

        caixa = pygame.Rect(205, 118, LARGURA - 410, 388)
        pygame.draw.rect(tela, cores["painel_fundo"], caixa, border_radius=12)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            caixa,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=12,
        )

        titulo = self.fonte_titulo.render("JOGO PAUSADO", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 168)))

        opcoes = [
            "[P / ESC]  Continuar Fase",
            "[R]  Reiniciar Fase Atual",
            f"[C]  Alto Contraste: {'ALTO' if modo_alto_contraste else 'NORMAL'}",
            f"[F]  Fonte: {'GRANDE' if self.fonte_grande else 'NORMAL'}",
            f"[M]  Áudio: {'ON' if audio_ativo else 'OFF'}   |   [N]  Música: {'ON' if (audio_ativo and musica_ativa) else 'OFF'}",
            "[Q]  Voltar ao Menu Principal",
        ]
        y = 224
        for opcao in opcoes:
            txt = self.fonte_media.render(opcao, True, cores["texto_principal"])
            tela.blit(txt, txt.get_rect(center=(LARGURA // 2, y)))
            y += 42

    def desenhar_transicao(
        self,
        tela: pygame.Surface,
        resumo_fase: Dict[str, object],
        aprendizado_abnt: str,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a tela de TRANSICAO com métricas da fase e princípio da ABNT NBR 9050."""
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(84, 58, LARGURA - 168, ALTURA - 116)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=14)
        pygame.draw.rect(tela, cores["sucesso_borda"], painel, 3, border_radius=14)

        titulo = self.fonte_titulo.render(
            f"FASE {resumo_fase['numero']} CONCLUÍDA!",
            True,
            cores["sucesso_borda"],
        )
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 114)))

        sub = self.fonte_subtitulo.render(
            str(resumo_fase["nome"]),
            True,
            cores["texto_principal"],
        )
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 158)))

        estatisticas = (
            f"Intervenções: {resumo_fase['intervencoes']}   |   "
            f"Erros de Rota: {resumo_fase['erros_rota']}   |   "
            f"Tempo Restante: {resumo_fase['tempo_restante']}s"
        )
        txt_est = self.fonte_media.render(estatisticas, True, cores["destaque_e"])
        tela.blit(txt_est, txt_est.get_rect(center=(LARGURA // 2, 208)))

        box_abnt = pygame.Rect(124, 248, LARGURA - 248, 190)
        pygame.draw.rect(tela, cores["hud_fundo"], box_abnt, border_radius=10)
        pygame.draw.rect(tela, cores["hud_borda"], box_abnt, 2, border_radius=10)

        cabecalho = self.fonte_media.render(
            "PRINCÍPIO DE ACESSIBILIDADE — ABNT NBR 9050",
            True,
            cores["destaque_e"],
        )
        tela.blit(cabecalho, (box_abnt.x + 20, box_abnt.y + 18))

        self._desenhar_texto_quebrado(
            tela,
            aprendizado_abnt,
            self.fonte_normal,
            cores["texto_principal"],
            box_abnt.x + 20,
            box_abnt.y + 54,
            box_abnt.width - 40,
            espacamento=6,
        )

        rodape = self.fonte_media.render(
            "[ENTER / ESPAÇO]  Avançar para a Próxima Fase",
            True,
            cores["destaque_e"],
        )
        tela.blit(rodape, rodape.get_rect(center=(LARGURA // 2, ALTURA - 96)))

    def desenhar_fim(
        self,
        tela: pygame.Surface,
        vitoria: bool,
        metricas_fases: List[Dict[str, object]],
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha o relatório final (FIM) de impacto e evolução por fase."""
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        cor_destaque = cores["sucesso_borda"] if vitoria else cores["erro_borda"]
        painel = pygame.Rect(52, 42, LARGURA - 104, ALTURA - 84)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=14)
        pygame.draw.rect(tela, cor_destaque, painel, 3, border_radius=14)

        titulo_texto = (
            "CAMPANHA CONCLUÍDA — AUTONOMIA GARANTIDA!"
            if vitoria
            else "TEMPO ESGOTADO — ROTA AINDA BLOQUEADA"
        )
        titulo = self.fonte_subtitulo.render(titulo_texto, True, cor_destaque)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 84)))

        sub_texto = (
            "Relatório de impacto: barreiras removidas e evolução da autonomia por fase."
            if vitoria
            else "Observe os obstáculos fixos antes de investir os recursos disponíveis."
        )
        sub = self.fonte_normal.render(sub_texto, True, cores["texto_secundario"])
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 120)))

        # Tabela de métricas observáveis
        cab_y = 166
        colunas_x = (76, 345, 550, 650, 745, 825)
        cabecalhos = ("Fase", "Autonomia", "Interv.", "Erros", "Testes", "Tempo")
        for x, texto in zip(colunas_x, cabecalhos):
            render = self.fonte_media.render(texto, True, cores["destaque_e"])
            tela.blit(render, (x, cab_y))

        pygame.draw.line(
            tela,
            cores["painel_borda"],
            (72, cab_y + 28),
            (LARGURA - 72, cab_y + 28),
            2,
        )

        y = cab_y + 42
        total_interv = 0
        total_erros = 0
        for metrica in metricas_fases:
            concluida = bool(metrica["concluida"])
            cor_status = cores["sucesso_borda"] if concluida else cores["erro_borda"]

            total_interv += int(metrica["intervencoes"])
            total_erros += int(metrica["erros_rota"])

            valores = (
                f"F{metrica['numero']} - {metrica['nome']}",
                str(metrica["autonomia_alcancada"]),
                str(metrica["intervencoes"]),
                str(metrica["erros_rota"]),
                str(metrica["tentativas_teste"]),
                f"{metrica['tempo_restante']}s",
            )
            for idx, (x, val) in enumerate(zip(colunas_x, valores)):
                cor_val = cor_status if idx == 1 else cores["texto_principal"]
                render = self.fonte_normal.render(val, True, cor_val)
                tela.blit(render, (x, y))
            y += 38

        resumo = self.fonte_media.render(
            f"Resumo Geral — Intervenções: {total_interv}   |   Erros de Rota: {total_erros}",
            True,
            cores["texto_principal"],
        )
        tela.blit(resumo, resumo.get_rect(center=(LARGURA // 2, 434)))

        acao_r = (
            "[R] Jogar Novamente" if vitoria else "[R] Reiniciar Fase Atual"
        )
        rodape = self.fonte_media.render(
            f"{acao_r}     |     [ENTER] Menu Principal     |     [ESC] Sair",
            True,
            cores["destaque_e"],
        )
        tela.blit(rodape, rodape.get_rect(center=(LARGURA // 2, ALTURA - 78)))
