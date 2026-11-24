"""Módulo de interface (HUD) e telas de estado do jogo 'Rota Acessível'.

Implementa a classe HUD responsável por desenhar a calçada urbana, a barra
superior (96 px), o feedback educativo inferior temporário ('[OK]' / '[!]'),
o destaque de interação '[E]' e as telas completas de MENU, INSTRUCOES, PAUSA,
TRANSICAO e FIM com suporte integral ao Modo Alto Contraste.
"""

from typing import Dict, List, Optional, Tuple

import pygame

from barreira import Barreira
from config import (
    ALTURA,
    ALTURA_FEEDBACK,
    COLS,
    CORES_ALTO_CONTRASTE,
    CORES_NORMAL,
    FONTE_FAMILIA,
    FONTES_NORMAL,
    HUD_ALTURA,
    LARGURA,
    ROWS,
    TEMPO_ALERTA_CRITICO,
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


class HUD:
    """Gerencia a renderização da interface, grade da calçada e telas de estado."""

    def __init__(self) -> None:
        """Inicializa as fontes, o estado do feedback e as miniaturas de legenda."""
        self.fonte_titulo = pygame.font.SysFont(
            FONTE_FAMILIA, FONTES_NORMAL["titulo"], bold=True
        )
        self.fonte_subtitulo = pygame.font.SysFont(
            FONTE_FAMILIA, FONTES_NORMAL["subtitulo"], bold=True
        )
        self.fonte_media = pygame.font.SysFont(
            FONTE_FAMILIA, FONTES_NORMAL["media"], bold=True
        )
        self.fonte_normal = pygame.font.SysFont(
            FONTE_FAMILIA, FONTES_NORMAL["normal"]
        )
        self.fonte_pequena = pygame.font.SysFont(
            FONTE_FAMILIA, FONTES_NORMAL["pequena"], bold=True
        )

        self.mensagem_feedback: str = ""
        self.tipo_feedback: str = "OK"
        self.tempo_feedback: float = 0.0

        self._miniaturas_legenda: Dict[str, pygame.Surface] = {}
        self._carregar_miniaturas_legenda()

    def _carregar_miniaturas_legenda(self) -> None:
        """Carrega os sprites PNG via caminho_arquivo() para a legenda visual."""
        tipos_legenda = (
            TIPO_LIXEIRA,
            TIPO_DEGRAU,
            TIPO_BURACO,
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
                imagem, (32, 32)
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
        """Decrementa o temporizador do feedback inferior usando dt.

        Args:
            dt: Tempo decorrido em segundos desde o frame anterior.
        """
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

    def desenhar_destaque_interacao(
        self,
        tela: pygame.Surface,
        barreira: Optional[Barreira],
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a moldura de destaque '[E] + ação e custo' sobre a barreira próxima."""
        if barreira is None:
            return
        cores = self.paleta(modo_alto_contraste)
        pygame.draw.rect(tela, cores["destaque_e"], barreira.rect, 4, border_radius=6)

        etiqueta = barreira.texto_prompt_interacao()
        texto = self.fonte_pequena.render(etiqueta, True, cores["destaque_e_texto"])
        caixa = texto.get_rect(
            midbottom=(
                barreira.rect.centerx,
                max(HUD_ALTURA + 24, barreira.rect.top - 3),
            )
        )
        # Mantém a etiqueta dentro dos limites horizontais da janela
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
    ) -> None:
        """Desenha o HUD superior (96 px) com fase, cronômetro, orçamento e atalhos."""
        cores = self.paleta(modo_alto_contraste)
        ret_hud = pygame.Rect(0, 0, LARGURA, HUD_ALTURA)
        pygame.draw.rect(tela, cores["hud_fundo"], ret_hud)
        pygame.draw.line(
            tela, cores["hud_borda"], (0, HUD_ALTURA - 2), (LARGURA, HUD_ALTURA - 2), 3
        )

        # Linha 1: Nome da fase, Cronômetro (alerta <= 15s) e Recursos
        titulo_fase = self.fonte_subtitulo.render(
            f"Fase {numero_fase}/{total_fases}: {nome_fase}",
            True,
            cores["texto_principal"],
        )
        tela.blit(titulo_fase, (16, 12))

        critico = tempo_restante <= TEMPO_ALERTA_CRITICO
        cor_tempo = cores["erro_borda"] if critico else cores["texto_principal"]
        prefixo_tempo = "[!] Tempo:" if critico else "Tempo:"
        txt_tempo = self.fonte_subtitulo.render(
            f"{prefixo_tempo} {max(0.0, tempo_restante):04.1f}s",
            True,
            cor_tempo,
        )
        tela.blit(txt_tempo, (475, 12))

        cor_rec = cores["aviso"] if recursos == 0 else cores["texto_principal"]
        txt_rec = self.fonte_subtitulo.render(
            f"Recursos: {recursos}",
            True,
            cor_rec,
        )
        tela.blit(txt_rec, (730, 12))

        # Linha 2: Atalhos curtos e estado dos recursos de acessibilidade
        status_rota = "TESTANDO ROTA..." if testando_rota else "[ESPAÇO] Testar Rota"
        txt_ctrl = self.fonte_pequena.render(
            f"[WASD/Setas] Mover   [E] Intervir   {status_rota}   [R] Reiniciar   [P] Pausa",
            True,
            cores["texto_secundario"],
        )
        tela.blit(txt_ctrl, (16, 58))

        contraste_txt = "ALTO" if modo_alto_contraste else "NORMAL"
        som_txt = "ON" if audio_ativo else "OFF"
        txt_acess = self.fonte_pequena.render(
            f"[C] Contraste: {contraste_txt}   [M] Som: {som_txt}",
            True,
            cores["destaque_e"],
        )
        tela.blit(txt_acess, (LARGURA - txt_acess.get_width() - 16, 58))

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
    ) -> None:
        """Desenha a tela inicial (MENU) com opções legíveis e acessíveis."""
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(100, 56, LARGURA - 200, ALTURA - 112)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=14)
        pygame.draw.rect(tela, cores["painel_borda"], painel, 3, border_radius=14)

        titulo = self.fonte_titulo.render("ROTA ACESSÍVEL", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 120)))

        subtitulo = self.fonte_subtitulo.render(
            "Tema 07 — Acessibilidade e Inclusão Urbana (ABNT NBR 9050)",
            True,
            cores["texto_principal"],
        )
        tela.blit(subtitulo, subtitulo.get_rect(center=(LARGURA // 2, 168)))

        self._desenhar_texto_quebrado(
            tela,
            (
                "Ajude Alex a remover barreiras urbanas e adaptar calçadas com "
                "orçamento limitado para garantir autonomia real até o destino."
            ),
            self.fonte_normal,
            cores["texto_secundario"],
            painel.x + 56,
            210,
            painel.width - 112,
            espacamento=6,
        )

        opcoes = [
            "[ENTER / ESPAÇO]  Iniciar Campanha",
            "[I]  Instruções e Legenda Visual",
            f"[C]  Modo Alto Contraste: {'ATIVADO' if modo_alto_contraste else 'DESATIVADO'}",
            f"[M]  Áudio: {'LIGADO' if audio_ativo else 'DESLIGADO'}",
            "[ESC]  Sair do Jogo",
        ]
        y = 308
        for texto in opcoes:
            caixa = pygame.Rect(205, y, LARGURA - 410, 40)
            pygame.draw.rect(tela, cores["botao_fundo"], caixa, border_radius=8)
            pygame.draw.rect(tela, cores["botao_borda"], caixa, 2, border_radius=8)
            render = self.fonte_media.render(texto, True, cores["texto_principal"])
            tela.blit(render, render.get_rect(center=caixa.center))
            y += 48

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
            (TIPO_LIXEIRA, "Lixeira (L): deslocar da faixa livre — custo 0"),
            (TIPO_DEGRAU, "Degrau (D): instalar rampa acessível — custo 1"),
            (TIPO_BURACO, "Buraco (B): nivelar pavimento — custo 1"),
            (TIPO_POSTE, "Poste fixo (P): intransponível — exige desvio"),
            (TIPO_RAMPA, "Rampa (R): passagem acessível liberada"),
            (TIPO_PISO_OK, "Piso nivelado (OK): passagem acessível liberada"),
            (TIPO_DESTINO, "Destino (FIM): ponto de chegada do Morador"),
        ]

        y = 92
        for tipo, descricao in legenda_itens:
            if modo_alto_contraste:
                quad = pygame.Rect(58, y, 32, 32)
                pygame.draw.rect(tela, cores[f"tile_{tipo}"], quad, border_radius=4)
                pygame.draw.rect(tela, cores["tile_borda"], quad, 2, border_radius=4)
                sigla = str(Barreira.TABELA_TIPOS[tipo]["sigla"])
                txt_s = self.fonte_pequena.render(sigla, True, cores["tile_sigla"])
                tela.blit(txt_s, txt_s.get_rect(center=quad.center))
            elif tipo in self._miniaturas_legenda:
                tela.blit(self._miniaturas_legenda[tipo], (58, y))

            txt_desc = self.fonte_normal.render(descricao, True, cores["texto_principal"])
            tela.blit(txt_desc, (102, y + 6))
            y += 45

        x_dir = 524
        sec_ctrl = self.fonte_media.render("CONTROLES", True, cores["destaque_e"])
        tela.blit(sec_ctrl, (x_dir, 92))

        controles = [
            "W, A, S, D ou Setas: mover Alex",
            "E: intervir na barreira destacada [E]",
            "ESPAÇO ou ENTER: testar rota (BFS)",
            "R: reiniciar a fase atual",
            "P ou ESC: pausar sem limite de tempo",
            "C: alternar Modo Alto Contraste",
            "M: ligar/desligar áudio",
        ]
        y_ctrl = 126
        for item in controles:
            render = self.fonte_normal.render(f"• {item}", True, cores["texto_principal"])
            tela.blit(render, (x_dir, y_ctrl))
            y_ctrl += 28

        sec_obj = self.fonte_media.render("OBJETIVO DO SERIOUS GAME", True, cores["destaque_e"])
        tela.blit(sec_obj, (x_dir, 344))
        self._desenhar_texto_quebrado(
            tela,
            (
                "Garanta uma faixa livre contínua da esquerda até o Destino "
                "gerenciando o orçamento limitado. Cada bloqueio explica o "
                "impacto real na autonomia e desconta 5s."
            ),
            self.fonte_normal,
            cores["texto_secundario"],
            x_dir,
            374,
            380,
            espacamento=5,
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
    ) -> None:
        """Desenha o overlay de PAUSA preservando a visualização do mapa ao fundo."""
        cores = self.paleta(modo_alto_contraste)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill(cores["overlay"])
        tela.blit(overlay, (0, 0))

        caixa = pygame.Rect(235, 145, LARGURA - 470, 325)
        pygame.draw.rect(tela, cores["painel_fundo"], caixa, border_radius=12)
        pygame.draw.rect(tela, cores["painel_borda"], caixa, 3, border_radius=12)

        titulo = self.fonte_titulo.render("JOGO PAUSADO", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 195)))

        opcoes = [
            "[P / ESC]  Continuar Fase",
            "[R]  Reiniciar Fase Atual",
            f"[C]  Alto Contraste: {'ALTO' if modo_alto_contraste else 'NORMAL'}",
            f"[M]  Áudio: {'ON' if audio_ativo else 'OFF'}",
            "[Q]  Voltar ao Menu Principal",
        ]
        y = 248
        for opcao in opcoes:
            txt = self.fonte_media.render(opcao, True, cores["texto_principal"])
            tela.blit(txt, txt.get_rect(center=(LARGURA // 2, y)))
            y += 38

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
