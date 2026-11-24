"""Módulo de interface (HUD), cenários urbanos em cache e telas interativas.

Implementa a classe HUD com:
- Pré-renderização em cache dos cenários cartoon 2D de cada fase (60 FPS estáveis);
- Barra superior moderna (96 px) com retrato do Morador, barra de tempo, orçamento
  visual e atalhos de acessibilidade ([C], [F], [M], [N]);
- Suporte completo a teclado e clique/hover do mouse em menus, mapa e botões;
- Telas acolhedoras para MENU, INSTRUCOES, MAPA, PAUSA, TRANSICAO, FIM e CREDITOS.
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
    """Gerencia cenários em cache, barra superior, feedback e telas clicáveis."""

    def __init__(self) -> None:
        """Inicializa fontes, caches de cenário/overlay, botões e miniaturas."""
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

        self._cache_fundos: Dict[Tuple[int, bool], pygame.Surface] = {}
        self._cache_overlay: Dict[bool, pygame.Surface] = {}
        self._miniaturas_legenda: Dict[str, pygame.Surface] = {}
        self._carregar_miniaturas_legenda()

        # Retângulos clicáveis atualizados a cada tela para suporte a mouse
        self.botoes_ativos: Dict[str, pygame.Rect] = {}
        self.botao_testar_hud: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def atualizar_fontes(self, fonte_grande: bool) -> None:
        """Recria as fontes da interface na escala Normal ou Grande em tempo real."""
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
        """Retorna a paleta ativa conforme o modo de alto contraste."""
        return CORES_ALTO_CONTRASTE if modo_alto_contraste else CORES_NORMAL

    def definir_feedback(self, mensagem: str, tipo: str, duracao: float) -> None:
        """Define uma mensagem educativa temporária na faixa inferior."""
        self.mensagem_feedback = mensagem
        self.tipo_feedback = tipo
        self.tempo_feedback = duracao

    def limpar_feedback(self) -> None:
        """Remove imediatamente qualquer mensagem de feedback ativa."""
        self.mensagem_feedback = ""
        self.tempo_feedback = 0.0

    def atualizar(self, dt: float) -> None:
        """Atualiza o temporizador do feedback inferior e o relógio de animações."""
        self.tempo_animacao += dt
        if self.tempo_feedback > 0.0:
            self.tempo_feedback = max(0.0, self.tempo_feedback - dt)
            if self.tempo_feedback == 0.0:
                self.mensagem_feedback = ""

    def obter_acao_clique(self, pos_mouse: Tuple[int, int]) -> Optional[str]:
        """Retorna a chave do botão clicado na tela atual ou None."""
        for acao, ret in self.botoes_ativos.items():
            if ret.collidepoint(pos_mouse):
                return acao
        return None

    def _quebrar_texto(
        self,
        texto: str,
        fonte: pygame.font.Font,
        largura_max: int,
    ) -> List[str]:
        """Quebra um texto longo em linhas que caibam em largura_max."""
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
        """Renderiza texto com quebra automática e retorna o Y final."""
        y_atual = y
        for linha in self._quebrar_texto(texto, fonte, largura_max):
            superficie = fonte.render(linha, True, cor)
            tela.blit(superficie, (x, y_atual))
            y_atual += superficie.get_height() + espacamento
        return y_atual

    def _desenhar_botao(
        self,
        tela: pygame.Surface,
        chave: str,
        ret: pygame.Rect,
        texto: str,
        modo_alto_contraste: bool,
        destaque: bool = False,
    ) -> None:
        """Desenha um botão arredondado com hover do mouse e o registra como clicável."""
        cores = self.paleta(modo_alto_contraste)
        self.botoes_ativos[chave] = ret
        mouse_sobre = ret.collidepoint(pygame.mouse.get_pos())

        if destaque:
            cor_fundo = cores["destaque_e"] if not mouse_sobre else cores["aviso"]
            cor_borda = cores["destaque_e_texto"]
            cor_texto = cores["destaque_e_texto"]
        else:
            cor_fundo = cores["botao_hover"] if mouse_sobre else cores["botao_fundo"]
            cor_borda = cores["destaque_e"] if mouse_sobre else cores["botao_borda"]
            cor_texto = cores["texto_escuro"]

        espessura = 3 if (mouse_sobre or modo_alto_contraste) else 2
        pygame.draw.rect(tela, cor_fundo, ret, border_radius=10)
        pygame.draw.rect(tela, cor_borda, ret, espessura, border_radius=10)

        render = self.fonte_media.render(texto, True, cor_texto)
        tela.blit(render, render.get_rect(center=ret.center))

    def _criar_fundo_fase(
        self,
        numero_fase: int,
        modo_alto_contraste: bool,
    ) -> pygame.Surface:
        """Pré-renderiza o cenário cartoon 2D da fase em uma única superfície em cache."""
        altura_mapa = ROWS * TILE
        surf = pygame.Surface((LARGURA, altura_mapa))
        cores = self.paleta(modo_alto_contraste)

        # 1. Calçada central (linhas 1 a 9) com lajotas acolhedoras
        for lin in range(ROWS):
            for col in range(COLS):
                ret = pygame.Rect(col * TILE, lin * TILE, TILE, TILE)
                if lin == 0:
                    cor = cores["faixa_servico"]
                elif lin == ROWS - 1:
                    cor = cores["asfalto"]
                else:
                    cor = (
                        cores["calcada_clara"]
                        if (lin + col) % 2 == 0
                        else cores["calcada_escura"]
                    )
                pygame.draw.rect(surf, cor, ret)
                if 1 <= lin <= ROWS - 2:
                    pygame.draw.rect(surf, cores["grade_linha"], ret, 1)

        # 2. Meio-fio superior e inferior
        pygame.draw.rect(surf, cores["meio_fio"], (0, TILE - 6, LARGURA, 6))
        pygame.draw.rect(surf, cores["meio_fio"], (0, (ROWS - 1) * TILE, LARGURA, 7))

        # 3. Faixas de pedestres / sinalização na rua (borda inferior)
        for x_faixa in range(28, LARGURA - 40, 72):
            pygame.draw.rect(
                surf,
                cores["faixa_rua"],
                (x_faixa, (ROWS - 1) * TILE + 18, 38, 10),
                border_radius=3,
            )

        # 4. Decoração temática leve no canteiro superior (sem atrapalhar leitura)
        if not modo_alto_contraste:
            cor_acento = cores.get(f"fase_{numero_fase}_acento", cores["fase_1_acento"])
            for x_dec in range(24, LARGURA - 24, 96):
                # Copas de árvores cartoon ou canteiros temáticos
                pygame.draw.circle(surf, (82, 138, 72), (x_dec + 16, 22), 15)
                pygame.draw.circle(surf, (108, 168, 92), (x_dec + 12, 18), 10)
                pygame.draw.circle(surf, cor_acento, (x_dec + 56, 22), 6)

        if pygame.display.get_surface() is not None:
            surf = surf.convert()
        return surf

    def desenhar_grade_calcada(
        self,
        tela: pygame.Surface,
        numero_fase: int,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha o cenário urbano da fase em 1 único blit usando cache (60 FPS)."""
        chave = (numero_fase, modo_alto_contraste)
        if chave not in self._cache_fundos:
            self._cache_fundos[chave] = self._criar_fundo_fase(
                numero_fase, modo_alto_contraste
            )
        tela.blit(self._cache_fundos[chave], (0, HUD_ALTURA))

    def desenhar_marcadores_rota(
        self,
        tela: pygame.Surface,
        inicio_morador: Tuple[int, int],
        destino: Tuple[int, int],
        nome_destino: str,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha etiquetas nítidas de PARTIDA e do DESTINO real da fase."""
        cores = self.paleta(modo_alto_contraste)
        marcadores = (
            (inicio_morador, "PARTIDA", cores["partida_marcador"]),
            (destino, nome_destino, cores["destino_marcador"]),
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
            fundo = caixa.inflate(10, 4)
            pygame.draw.rect(tela, cor_fundo, fundo, border_radius=5)
            pygame.draw.rect(tela, cores["tile_borda"], fundo, 1, border_radius=5)
            tela.blit(txt, caixa)

    def desenhar_rastro_morador(
        self,
        tela: pygame.Surface,
        celulas_percorridas: List[Tuple[int, int]],
        rota_sucesso: bool,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha um rastro pontilhado suave mostrando o trajeto do Morador."""
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
        """Desenha moldura pulsante senoidal '[E] + ação e custo' sobre a barreira."""
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
                max(HUD_ALTURA + 24, ret_pulsante.top - 4),
            )
        )
        caixa.clamp_ip(
            pygame.Rect(8, HUD_ALTURA + 4, LARGURA - 16, ALTURA - HUD_ALTURA - 8)
        )
        caixa_fundo = caixa.inflate(14, 6)
        pygame.draw.rect(tela, cores["destaque_e"], caixa_fundo, border_radius=6)
        pygame.draw.rect(tela, cores["destaque_e_texto"], caixa_fundo, 2, border_radius=6)
        tela.blit(texto, caixa)

    def desenhar_barra_superior(
        self,
        tela: pygame.Surface,
        numero_fase: int,
        total_fases: int,
        nome_fase: str,
        nome_morador: str,
        retrato_morador: pygame.Surface,
        tempo_restante: float,
        tempo_total: float,
        recursos: int,
        recursos_iniciais: int,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        testando_rota: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha o HUD superior moderno (96 px) com retrato, barra de tempo e ações."""
        cores = self.paleta(modo_alto_contraste)
        ret_hud = pygame.Rect(0, 0, LARGURA, HUD_ALTURA)
        pygame.draw.rect(tela, cores["hud_fundo"], ret_hud)
        borda = BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3
        pygame.draw.line(
            tela, cores["hud_borda"], (0, HUD_ALTURA - 2), (LARGURA, HUD_ALTURA - 2), borda
        )

        # Cartão esquerdo: Retrato do Morador + Fase
        cartao_esq = pygame.Rect(10, 8, 345, 50)
        pygame.draw.rect(tela, cores["hud_cartao"], cartao_esq, border_radius=8)
        tela.blit(retrato_morador, (16, 13))

        txt_fase = self.fonte_media.render(
            f"F{numero_fase}/{total_fases}: {nome_fase}",
            True,
            cores["texto_principal"],
        )
        tela.blit(txt_fase, (62, 11))
        txt_morador = self.fonte_pequena.render(
            f"Morador: {nome_morador}",
            True,
            cores["destaque_e"],
        )
        tela.blit(txt_morador, (62, 34))

        # Cartão central: Cronômetro com barra visual + Orçamento de recursos
        cartao_mid = pygame.Rect(365, 8, 415, 50)
        pygame.draw.rect(tela, cores["hud_cartao"], cartao_mid, border_radius=8)

        critico = tempo_restante <= TEMPO_ALERTA_CRITICO
        cor_tempo = cores["erro_borda"] if critico else cores["sucesso_borda"]
        prefixo_t = "[!] " if critico else ""
        txt_tempo = self.fonte_pequena.render(
            f"{prefixo_t}Tempo: {max(0.0, tempo_restante):04.1f}s",
            True,
            cores["texto_principal"],
        )
        tela.blit(txt_tempo, (377, 12))

        barra_bg = pygame.Rect(377, 36, 170, 12)
        pygame.draw.rect(tela, cores["hud_fundo"], barra_bg, border_radius=6)
        razao = max(0.0, min(1.0, tempo_restante / max(1.0, tempo_total)))
        largura_fill = max(0, round(barra_bg.width * razao))
        if largura_fill > 0:
            pygame.draw.rect(
                tela, cor_tempo, (barra_bg.x, barra_bg.y, largura_fill, barra_bg.height), border_radius=6
            )

        # Orçamento visual em fichas
        cor_rec = cores["aviso"] if recursos == 0 else cores["texto_principal"]
        txt_rec = self.fonte_pequena.render(
            f"Orçamento: {recursos}/{recursos_iniciais}",
            True,
            cor_rec,
        )
        tela.blit(txt_rec, (568, 12))
        for i in range(recursos_iniciais):
            cor_ficha = cores["destaque_e"] if i < recursos else cores["hud_fundo"]
            cx = 576 + i * 24
            pygame.draw.circle(tela, cor_ficha, (cx, 42), 7)
            pygame.draw.circle(tela, cores["texto_principal"], (cx, 42), 7, 1)

        # Botão clicável [Testar Rota] à direita
        self.botao_testar_hud = pygame.Rect(790, 8, 160, 50)
        cor_btn = cores["rota_preview"] if testando_rota else cores["destaque_e"]
        pygame.draw.rect(tela, cor_btn, self.botao_testar_hud, border_radius=8)
        pygame.draw.rect(
            tela, cores["destaque_e_texto"], self.botao_testar_hud, 2, border_radius=8
        )
        rotulo_btn = "TESTANDO..." if testando_rota else "TESTAR [ESPAÇO]"
        txt_btn = self.fonte_pequena.render(rotulo_btn, True, cores["destaque_e_texto"])
        tela.blit(txt_btn, txt_btn.get_rect(center=self.botao_testar_hud.center))

        # Linha inferior de atalhos rápidos + indicadores de acessibilidade
        contraste_txt = "ALTO" if modo_alto_contraste else "NORM"
        fonte_txt = "G" if self.fonte_grande else "N"
        som_txt = "ON" if audio_ativo else "OFF"
        mus_txt = "ON" if (audio_ativo and musica_ativa) else "OFF"
        atalhos = (
            f"[WASD/Setas] Mover   [E/Clique] Intervir   [R] Reiniciar   [P] Pausa   |   "
            f"[C] Contr:{contraste_txt}  [F] Fonte:{fonte_txt}  [M] Som:{som_txt}  [N] Mus:{mus_txt}"
        )
        txt_at = self.fonte_pequena.render(atalhos, True, cores["texto_secundario"])
        tela.blit(txt_at, (14, 67))

    def desenhar_feedback_inferior(
        self,
        tela: pygame.Surface,
        retrato_morador: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a caixa educativa inferior temporária com retrato do Morador."""
        if not self.mensagem_feedback or self.tempo_feedback <= 0.0:
            return

        cores = self.paleta(modo_alto_contraste)
        eh_ok = self.tipo_feedback == "OK"
        cor_fundo = cores["sucesso_fundo"] if eh_ok else cores["erro_fundo"]
        cor_borda = cores["sucesso_borda"] if eh_ok else cores["erro_borda"]
        prefixo = "[OK] " if eh_ok else "[!] "

        ret = pygame.Rect(16, ALTURA - ALTURA_FEEDBACK - 10, LARGURA - 32, ALTURA_FEEDBACK)
        pygame.draw.rect(tela, cor_fundo, ret, border_radius=10)
        pygame.draw.rect(tela, cor_borda, ret, 3, border_radius=10)

        tela.blit(retrato_morador, (ret.x + 12, ret.y + (ret.height - 40) // 2))
        self._desenhar_texto_quebrado(
            tela,
            prefixo + self.mensagem_feedback,
            self.fonte_normal,
            cores["texto_principal"],
            ret.x + 62,
            ret.y + 10,
            ret.width - 78,
            espacamento=2,
        )

    def desenhar_menu(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha a tela inicial (MENU) acolhedora com botões clicáveis e atalhos."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(80, 34, LARGURA - 160, ALTURA - 68)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=18)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            painel,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=18,
        )

        # Cabeçalho colorido de boas-vindas
        faixa_topo = pygame.Rect(painel.x, painel.y, painel.width, 118)
        pygame.draw.rect(
            tela,
            cores["hud_fundo"],
            faixa_topo,
            border_top_left_radius=16,
            border_top_right_radius=16,
        )
        titulo = self.fonte_titulo.render("ROTA ACESSÍVEL", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, painel.y + 44)))
        sub = self.fonte_media.render(
            "Vila Nova — Serious Game sobre Acessibilidade e Inclusão (ABNT NBR 9050)",
            True,
            cores["texto_principal"],
        )
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, painel.y + 88)))

        self._desenhar_texto_quebrado(
            tela,
            (
                "Explore 4 regiões urbanas com Alex, elimine barreiras físicas, "
                "visuais e comunicacionais dentro do orçamento e valide a rota "
                "contínua com cada morador da cidade."
            ),
            self.fonte_normal,
            cores["texto_escuro"],
            painel.x + 54,
            painel.y + 134,
            painel.width - 108,
            espacamento=4,
        )

        # Botões principais clicáveis (teclado ou mouse)
        self._desenhar_botao(
            tela,
            "jogar",
            pygame.Rect(210, 246, LARGURA - 420, 48),
            "[ENTER]  Iniciar Campanha (4 Fases)",
            modo_alto_contraste,
            destaque=True,
        )
        self._desenhar_botao(
            tela,
            "mapa",
            pygame.Rect(210, 306, LARGURA - 420, 44),
            "[S]  Mapa Urbano — Escolher Fase",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "instrucoes",
            pygame.Rect(210, 362, 260, 44),
            "[I]  Instruções",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "creditos",
            pygame.Rect(490, 362, 260, 44),
            "[A]  Créditos",
            modo_alto_contraste,
        )

        # Barra inferior de preferências de acessibilidade clicáveis
        self._desenhar_botao(
            tela,
            "contraste",
            pygame.Rect(118, 434, 174, 38),
            f"[C] Contraste: {'ALTO' if modo_alto_contraste else 'NORM'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "fonte",
            pygame.Rect(302, 434, 174, 38),
            f"[F] Fonte: {'GRANDE' if self.fonte_grande else 'NORM'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "audio",
            pygame.Rect(486, 434, 174, 38),
            f"[M] Som: {'ON' if audio_ativo else 'OFF'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "musica",
            pygame.Rect(670, 434, 174, 38),
            f"[N] Música: {'ON' if (audio_ativo and musica_ativa) else 'OFF'}",
            modo_alto_contraste,
        )

        self._desenhar_botao(
            tela,
            "sair",
            pygame.Rect(360, 494, 240, 38),
            "[ESC]  Sair do Jogo",
            modo_alto_contraste,
        )

    def desenhar_instrucoes(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a tela INSTRUCOES com legenda visual completa e botões clicáveis."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(30, 22, LARGURA - 60, ALTURA - 44)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=14)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            painel,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=14,
        )

        titulo = self.fonte_subtitulo.render(
            "INSTRUÇÕES E LEGENDA DE OBSTÁCULOS",
            True,
            cores["texto_escuro"],
        )
        tela.blit(titulo, (52, 38))

        legenda_itens = [
            (TIPO_LIXEIRA, "Lixeira (L): deslocar da faixa livre — 0 rec"),
            (TIPO_DEGRAU, "Degrau (D): instalar rampa acessível — 1 rec"),
            (TIPO_BURACO, "Buraco (B): nivelar pavimento — 1 rec"),
            (TIPO_SEM_PISO_TATIL, "Sem Piso Tátil (T): instalar piso tátil — 1 rec"),
            (TIPO_AVISO_SONORO, "Aviso Sonoro (S): instalar painel visual — 1 rec"),
            (TIPO_POSTE, "Poste fixo (P): intransponível — exige desvio"),
            (TIPO_RAMPA, "Rampa (R) / Piso OK: passagem liberada"),
            (TIPO_DESTINO, "Destino (FIM): ponto de chegada"),
        ]

        y = 82
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

            txt_desc = self.fonte_normal.render(descricao, True, cores["texto_escuro"])
            tela.blit(txt_desc, (92, y + 5))
            y += 46

        x_dir = 526
        tela.blit(
            self.fonte_media.render("CONTROLES E ACESSIBILIDADE", True, cores["texto_escuro"]),
            (x_dir, 82),
        )
        controles = [
            "WASD ou Setas: mover Alex suavemente",
            "E ou Clique no obstáculo: intervir [E]",
            "ESPAÇO / ENTER / Botão: testar rota (BFS)",
            "R: reiniciar a fase atual",
            "P / ESC: pausar sem limite de tempo",
            "C: Alto Contraste | F: Fonte Grande",
            "M: silenciar áudio | N: silenciar música",
        ]
        y_c = 116
        for item in controles:
            tela.blit(self.fonte_normal.render(f"• {item}", True, cores["texto_escuro"]), (x_dir, y_c))
            y_c += 30

        tela.blit(
            self.fonte_media.render("COMO FUNCIONA", True, cores["texto_escuro"]),
            (x_dir, 344),
        )
        self._desenhar_texto_quebrado(
            tela,
            (
                "Cada fase apresenta um morador real (Clara, Lucas, Sofia ou "
                "Mateus) e barreiras ligadas à sua necessidade. Libere uma rota "
                "contínua dentro do orçamento e chame o morador para testar!"
            ),
            self.fonte_normal,
            cores["texto_suave_escuro"],
            x_dir,
            374,
            380,
            espacamento=5,
        )

        self._desenhar_botao(
            tela,
            "jogar",
            pygame.Rect(220, ALTURA - 86, 240, 42),
            "[ENTER] Começar",
            modo_alto_contraste,
            destaque=True,
        )
        self._desenhar_botao(
            tela,
            "menu",
            pygame.Rect(500, ALTURA - 86, 240, 42),
            "[ESC] Voltar ao Menu",
            modo_alto_contraste,
        )

    def desenhar_pausa(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
        audio_ativo: bool,
        musica_ativa: bool = True,
    ) -> None:
        """Desenha o overlay em cache de PAUSA com botões clicáveis."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        if modo_alto_contraste not in self._cache_overlay:
            ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            ov.fill(cores["overlay"])
            self._cache_overlay[modo_alto_contraste] = ov
        tela.blit(self._cache_overlay[modo_alto_contraste], (0, 0))

        caixa = pygame.Rect(230, 108, LARGURA - 460, 408)
        pygame.draw.rect(tela, cores["painel_fundo"], caixa, border_radius=14)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            caixa,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=14,
        )

        titulo = self.fonte_subtitulo.render("JOGO PAUSADO", True, cores["texto_escuro"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 146)))

        self._desenhar_botao(
            tela,
            "continuar",
            pygame.Rect(280, 180, 400, 42),
            "[P / ESC]  Continuar Fase",
            modo_alto_contraste,
            destaque=True,
        )
        self._desenhar_botao(
            tela,
            "reiniciar",
            pygame.Rect(280, 232, 400, 40),
            "[R]  Reiniciar Fase Atual",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "contraste",
            pygame.Rect(280, 282, 195, 40),
            f"[C] Contraste: {'ALTO' if modo_alto_contraste else 'NORM'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "fonte",
            pygame.Rect(485, 282, 195, 40),
            f"[F] Fonte: {'G' if self.fonte_grande else 'N'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "audio",
            pygame.Rect(280, 332, 195, 40),
            f"[M] Som: {'ON' if audio_ativo else 'OFF'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "musica",
            pygame.Rect(485, 332, 195, 40),
            f"[N] Música: {'ON' if (audio_ativo and musica_ativa) else 'OFF'}",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "menu",
            pygame.Rect(280, 392, 400, 40),
            "[Q]  Voltar ao Menu Principal",
            modo_alto_contraste,
        )

    def desenhar_transicao(
        self,
        tela: pygame.Surface,
        resumo_fase: Dict[str, object],
        aprendizado_abnt: str,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a tela de TRANSICAO com autonomia alcançada e nota ABNT NBR 9050."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(80, 50, LARGURA - 160, ALTURA - 100)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=16)
        pygame.draw.rect(tela, cores["sucesso_borda"], painel, 4, border_radius=16)

        titulo = self.fonte_titulo.render(
            f"FASE {resumo_fase['numero']} CONCLUÍDA!",
            True,
            cores["sucesso_fundo"] if not modo_alto_contraste else cores["sucesso_borda"],
        )
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 106)))

        sub = self.fonte_subtitulo.render(
            f"{resumo_fase['nome']}  —  {resumo_fase['autonomia_alcancada']}",
            True,
            cores["texto_escuro"],
        )
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 152)))

        estatisticas = (
            f"Intervenções: {resumo_fase['intervencoes']}   |   "
            f"Erros de Rota: {resumo_fase['erros_rota']}   |   "
            f"Tempo Restante: {resumo_fase['tempo_restante']}s"
        )
        txt_est = self.fonte_media.render(estatisticas, True, cores["texto_suave_escuro"])
        tela.blit(txt_est, txt_est.get_rect(center=(LARGURA // 2, 198)))

        box_abnt = pygame.Rect(120, 236, LARGURA - 240, 196)
        pygame.draw.rect(tela, cores["hud_fundo"], box_abnt, border_radius=12)
        pygame.draw.rect(tela, cores["hud_borda"], box_abnt, 2, border_radius=12)

        cabecalho = self.fonte_media.render(
            "PRINCÍPIO DE ACESSIBILIDADE — ABNT NBR 9050 / LBI",
            True,
            cores["destaque_e"],
        )
        tela.blit(cabecalho, (box_abnt.x + 22, box_abnt.y + 18))

        self._desenhar_texto_quebrado(
            tela,
            aprendizado_abnt,
            self.fonte_normal,
            cores["texto_principal"],
            box_abnt.x + 22,
            box_abnt.y + 54,
            box_abnt.width - 44,
            espacamento=6,
        )

        self._desenhar_botao(
            tela,
            "avancar",
            pygame.Rect(270, ALTURA - 122, 420, 46),
            "[ENTER / ESPAÇO]  Avançar para a Próxima Fase",
            modo_alto_contraste,
            destaque=True,
        )

    def desenhar_fim(
        self,
        tela: pygame.Surface,
        vitoria: bool,
        metricas_fases: List[Dict[str, object]],
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha o relatório final (FIM) de impacto e evolução por fase."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        cor_borda = cores["sucesso_borda"] if vitoria else cores["erro_borda"]
        cor_titulo = (
            cores["sucesso_fundo"]
            if (vitoria and not modo_alto_contraste)
            else (cores["erro_fundo"] if (not vitoria and not modo_alto_contraste) else cor_borda)
        )

        painel = pygame.Rect(46, 36, LARGURA - 92, ALTURA - 72)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=16)
        pygame.draw.rect(tela, cor_borda, painel, 4, border_radius=16)

        titulo_texto = (
            "VILA NOVA MAIS ACESSÍVEL — CAMPANHA CONCLUÍDA!"
            if vitoria
            else "TEMPO ESGOTADO — ROTA AINDA BLOQUEADA"
        )
        titulo = self.fonte_subtitulo.render(titulo_texto, True, cor_titulo)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 78)))

        sub_texto = (
            "Relatório de impacto: barreiras removidas e evolução da autonomia por fase."
            if vitoria
            else "Observe os obstáculos fixos antes de investir os recursos disponíveis."
        )
        sub = self.fonte_normal.render(sub_texto, True, cores["texto_suave_escuro"])
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 114)))

        cab_y = 158
        colunas_x = (70, 338, 560, 660, 750, 830)
        cabecalhos = ("Fase", "Autonomia", "Interv.", "Erros", "Testes", "Tempo")
        for x, texto in zip(colunas_x, cabecalhos):
            render = self.fonte_media.render(texto, True, cores["texto_escuro"])
            tela.blit(render, (x, cab_y))

        pygame.draw.line(
            tela, cores["painel_borda"], (68, cab_y + 28), (LARGURA - 68, cab_y + 28), 2
        )

        y = cab_y + 42
        total_interv = 0
        total_erros = 0
        for metrica in metricas_fases:
            concluida = bool(metrica["concluida"])
            cor_status = (
                cores["sucesso_fundo"]
                if (concluida and not modo_alto_contraste)
                else (cores["erro_fundo"] if (not concluida and not modo_alto_contraste) else (cores["sucesso_borda"] if concluida else cores["erro_borda"]))
            )

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
                cor_val = cor_status if idx == 1 else cores["texto_escuro"]
                render = self.fonte_normal.render(val, True, cor_val)
                tela.blit(render, (x, y))
            y += 38

        resumo = self.fonte_media.render(
            f"Resumo Geral — Intervenções: {total_interv}   |   Erros de Rota: {total_erros}",
            True,
            cores["texto_escuro"],
        )
        tela.blit(resumo, resumo.get_rect(center=(LARGURA // 2, 430)))

        self._desenhar_botao(
            tela,
            "reiniciar",
            pygame.Rect(160, ALTURA - 116, 280, 44),
            "[R] Jogar Novamente" if vitoria else "[R] Reiniciar Fase",
            modo_alto_contraste,
            destaque=True,
        )
        self._desenhar_botao(
            tela,
            "menu",
            pygame.Rect(460, ALTURA - 116, 220, 44),
            "[ENTER] Menu",
            modo_alto_contraste,
        )
        self._desenhar_botao(
            tela,
            "sair",
            pygame.Rect(700, ALTURA - 116, 120, 44),
            "[ESC] Sair",
            modo_alto_contraste,
        )

    def desenhar_mapa_fases(
        self,
        tela: pygame.Surface,
        lista_fases: List[Dict[str, object]],
        fases_desbloqueadas: int,
        registros_salvos: Dict[int, Dict[str, object]],
        indice_selecionado: int,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha o estado MAPA com rota urbana estilizada e cartões clicáveis."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(34, 24, LARGURA - 68, ALTURA - 48)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=16)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            painel,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=16,
        )

        titulo = self.fonte_subtitulo.render(
            "MAPA DE VILA NOVA — SELECIONE UMA ROTA",
            True,
            cores["texto_escuro"],
        )
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 60)))

        sub = self.fonte_normal.render(
            "Clique em uma fase desbloqueada ou use Setas / WASD / teclas [1]–[4] + [ENTER].",
            True,
            cores["texto_suave_escuro"],
        )
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 92)))

        centros = [(265, 222), (695, 222), (265, 412), (695, 412)]
        pygame.draw.lines(tela, cores["hud_borda"], False, centros, 6)

        pos_mouse = pygame.mouse.get_pos()
        for idx, fase in enumerate(lista_fases):
            numero = int(fase["numero"])
            desbloqueada = numero <= fases_desbloqueadas
            registro = registros_salvos.get(numero, {})
            concluida = bool(registro.get("concluida", False))
            selos = int(registro.get("melhor_selos", 0))
            nivel = str(registro.get("melhor_nivel", ""))

            cx, cy = centros[idx]
            cartao = pygame.Rect(0, 0, 390, 150)
            cartao.center = (cx, cy)
            self.botoes_ativos[f"fase_{idx}"] = cartao

            hover = cartao.collidepoint(pos_mouse)
            selecionada = idx == indice_selecionado or hover

            cor_fundo = (
                cores["botao_hover"]
                if (desbloqueada and selecionada)
                else (cores["botao_fundo"] if desbloqueada else cores["calcada_escura"])
            )
            if selecionada:
                cor_borda = cores["destaque_e"] if modo_alto_contraste else cores["botao_borda"]
                espessura = 4
            elif concluida:
                cor_borda = cores["sucesso_borda"]
                espessura = 3
            else:
                cor_borda = cores["painel_borda"]
                espessura = 2

            pygame.draw.rect(tela, cor_fundo, cartao, border_radius=12)
            pygame.draw.rect(tela, cor_borda, cartao, espessura, border_radius=12)

            cab = f"[{numero}] {fase['nome']}"
            tela.blit(
                self.fonte_media.render(cab, True, cores["texto_escuro"]),
                (cartao.x + 16, cartao.y + 14),
            )
            tela.blit(
                self.fonte_pequena.render(
                    str(fase["perfil_morador"]), True, cores["texto_suave_escuro"]
                ),
                (cartao.x + 16, cartao.y + 44),
            )
            info_orc = f"Tempo: {int(float(fase['tempo']))}s   |   Orçamento: {fase['recursos']} rec"
            tela.blit(
                self.fonte_pequena.render(info_orc, True, cores["texto_escuro"]),
                (cartao.x + 16, cartao.y + 72),
            )

            if not desbloqueada:
                status_txt = "[BLOQUEADA] Conclua a fase anterior"
                cor_st = cores["erro_fundo"] if not modo_alto_contraste else cores["erro_borda"]
            elif concluida:
                selos_visuais = "★" * selos + "☆" * (3 - selos)
                status_txt = f"{nivel} ({selos}/3) {selos_visuais}"
                cor_st = cores["sucesso_fundo"] if not modo_alto_contraste else cores["sucesso_borda"]
            else:
                status_txt = "[DISPONÍVEL] Clique ou aperte ENTER"
                cor_st = cores["partida_marcador"]

            tela.blit(
                self.fonte_pequena.render(status_txt, True, cor_st),
                (cartao.x + 16, cartao.y + 106),
            )

        self._desenhar_botao(
            tela,
            "jogar_selecionada",
            pygame.Rect(210, ALTURA - 84, 270, 40),
            "[ENTER] Jogar Selecionada",
            modo_alto_contraste,
            destaque=True,
        )
        self._desenhar_botao(
            tela,
            "menu",
            pygame.Rect(500, ALTURA - 84, 250, 40),
            "[ESC] Voltar ao Menu",
            modo_alto_contraste,
        )

    def desenhar_creditos(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a tela CREDITOS com autores, acessibilidade e referências técnicas."""
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        tela.fill(cores["fundo_tela"])

        painel = pygame.Rect(44, 26, LARGURA - 88, ALTURA - 52)
        pygame.draw.rect(tela, cores["painel_fundo"], painel, border_radius=16)
        pygame.draw.rect(
            tela,
            cores["painel_borda"],
            painel,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=16,
        )

        titulo = self.fonte_subtitulo.render(
            "CRÉDITOS E REFERÊNCIAS — ROTA ACESSÍVEL",
            True,
            cores["texto_escuro"],
        )
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 64)))

        sub = self.fonte_normal.render(
            "Serious Game — Engenharia de Software (7º Período) | Tema 07: Acessibilidade e Inclusão",
            True,
            cores["texto_suave_escuro"],
        )
        tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 96)))

        x_esq = 76
        tela.blit(
            self.fonte_media.render("EQUIPE DO PROJETO (5 INTEGRANTES)", True, cores["texto_escuro"]),
            (x_esq, 138),
        )
        autores = [
            "• Felipe-dev021 — Arquitetura, Main Loop e Persistência",
            "• anacgsx — Assets, Barreiras e Trilha Sonora",
            "• lucas-marins-dev — Jogador, Juice e Acessibilidade",
            "• GuiMell0 — Algoritmo BFS, Fases e Autonomia",
            "• Gabriel-dev10 — HUD, Mapa Urbano, Créditos e Docs",
        ]
        y = 172
        for autor in autores:
            tela.blit(self.fonte_normal.render(autor, True, cores["texto_escuro"]), (x_esq, y))
            y += 28

        tela.blit(
            self.fonte_media.render("REFERÊNCIAS TÉCNICAS", True, cores["texto_escuro"]),
            (x_esq, 336),
        )
        referencias = [
            "• ABNT NBR 9050:2020 — Acessibilidade a edificações e vias",
            "• Lei nº 13.146/2015 — Lei Brasileira de Inclusão (LBI)",
            "• W3C WCAG 2.1 — Diretrizes de Acessibilidade de Conteúdo",
        ]
        y_ref = 370
        for ref in referencias:
            tela.blit(self.fonte_normal.render(ref, True, cores["texto_escuro"]), (x_esq, y_ref))
            y_ref += 28

        x_dir = 548
        tela.blit(
            self.fonte_media.render("ACESSIBILIDADE NO JOGO", True, cores["texto_escuro"]),
            (x_dir, 138),
        )
        acess = [
            "• [C] Modo Alto Contraste com siglas",
            "• [F] Alternância de Fonte (Normal/Grande)",
            "• [M] Silenciar áudio completo",
            "• [N] Silenciar apenas música de fundo",
            "• [P] Pausa sem limite de tempo",
            "• Sem flashes fortes ou tremor de tela",
            "• Suporte completo a teclado e mouse",
        ]
        y_ac = 172
        for item in acess:
            tela.blit(self.fonte_normal.render(item, True, cores["texto_escuro"]), (x_dir, y_ac))
            y_ac += 28

        self._desenhar_botao(
            tela,
            "menu",
            pygame.Rect(330, ALTURA - 96, 300, 42),
            "[ESC / ENTER]  Voltar ao Menu",
            modo_alto_contraste,
            destaque=True,
        )
