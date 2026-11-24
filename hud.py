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
    DURACAO_POPUP,
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
        self._cache_luz_solar: Optional[pygame.Surface] = None
        self._cache_feedback_chave: Optional[Tuple[str, str, bool, bool]] = None
        self._cache_feedback_surf: Optional[pygame.Surface] = None
        self._cache_atalhos_chave: Optional[Tuple[bool, bool, bool, bool, bool]] = None
        self._cache_atalhos_surf: Optional[pygame.Surface] = None
        self._popups: List[Dict[str, object]] = []
        self._miniaturas_legenda: Dict[str, pygame.Surface] = {}
        self._carregar_miniaturas_legenda()

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
        """Remove imediatamente qualquer mensagem de feedback ou popup ativo."""
        self.mensagem_feedback = ""
        self.tempo_feedback = 0.0
        self._cache_feedback_chave = None
        self._cache_feedback_surf = None
        self._popups.clear()

    def adicionar_popup(
        self,
        centro_x: float,
        centro_y: float,
        texto: str,
        cor_fundo: Tuple[int, ...],
        cor_texto: Tuple[int, ...],
    ) -> None:
        """Cria um texto flutuante pré-renderizado que sobe suavemente após uma ação."""
        render = self.fonte_pequena.render(texto, True, cor_texto)
        largura = render.get_width() + 14
        altura = render.get_height() + 8
        surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(surf, cor_fundo[:3], (0, 0, largura, altura), border_radius=6)
        pygame.draw.rect(surf, cor_texto[:3], (0, 0, largura, altura), 2, border_radius=6)
        surf.blit(render, (7, 4))
        self._popups.append(
            {
                "surf": surf,
                "x": centro_x - largura / 2.0,
                "y": centro_y - altura,
                "vida": DURACAO_POPUP,
            }
        )

    def atualizar(self, dt: float) -> None:
        """Atualiza feedback, popups flutuantes e relógio de animações."""
        self.tempo_animacao += dt
        if self.tempo_feedback > 0.0:
            self.tempo_feedback = max(0.0, self.tempo_feedback - dt)
            if self.tempo_feedback == 0.0:
                self.mensagem_feedback = ""
                self._cache_feedback_chave = None
                self._cache_feedback_surf = None

        vivos: List[Dict[str, object]] = []
        for popup in self._popups:
            vida = float(popup["vida"]) - dt
            if vida > 0.0:
                popup["vida"] = vida
                popup["y"] = float(popup["y"]) - 36.0 * dt
                vivos.append(popup)
        self._popups = vivos

    def desenhar_popups(self, tela: pygame.Surface) -> None:
        """Desenha todos os popups flutuantes pré-renderizados na tela."""
        for popup in self._popups:
            surf = popup["surf"]
            if isinstance(surf, pygame.Surface):
                tela.blit(surf, (round(float(popup["x"])), round(float(popup["y"]))))

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

    def _desenhar_vermelhinho(
        self,
        surf: pygame.Surface,
        x: int,
        y: int,
        cores: Dict[str, Tuple[int, ...]],
    ) -> None:
        """Desenha o ônibus Vermelhinho 2.5D (Tarifa Zero) de Maricá/RJ com sombra."""
        pygame.draw.ellipse(surf, (24, 28, 34), (x + 4, y + 26, 86, 12))
        pygame.draw.rect(surf, cores["vermelhinho"], (x, y, 88, 32), border_radius=6)
        pygame.draw.rect(surf, (240, 74, 74), (x + 2, y + 2, 84, 7), border_radius=4)
        pygame.draw.rect(surf, (230, 236, 242), (x + 26, y - 3, 28, 6), border_radius=2)
        pygame.draw.rect(surf, (250, 248, 244), (x + 2, y + 20, 84, 4))
        for jx in (x + 8, x + 26, x + 44, x + 64):
            larg = 14 if jx < x + 60 else 18
            pygame.draw.rect(surf, (186, 230, 253), (jx, y + 8, larg, 10), border_radius=2)
        pygame.draw.circle(surf, (22, 26, 34), (x + 18, y + 32), 6)
        pygame.draw.circle(surf, (22, 26, 34), (x + 70, y + 32), 6)
        pygame.draw.circle(surf, (254, 240, 138), (x + 85, y + 24), 3)
        pygame.draw.rect(surf, cores["tile_borda"], (x, y, 88, 32), 2, border_radius=6)

    def _criar_fundo_fase(
        self,
        numero_fase: int,
        modo_alto_contraste: bool,
    ) -> pygame.Surface:
        """Pré-renderiza o cenário 2.5D de Maricá/RJ da fase em cache (1 blit/frame)."""
        altura_mapa = ROWS * TILE
        surf = pygame.Surface((LARGURA, altura_mapa))
        cores = self.paleta(modo_alto_contraste)

        for lin in range(ROWS):
            for col in range(COLS):
                ret = pygame.Rect(col * TILE, lin * TILE, TILE, TILE)
                if lin == 0:
                    cor = (
                        cores["lagoa_azul"]
                        if numero_fase in (1, 4)
                        else cores["faixa_servico"]
                    )
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
                    if not modo_alto_contraste:
                        pygame.draw.line(
                            surf, (246, 241, 230), (ret.left + 1, ret.top + 1), (ret.right - 2, ret.top + 1), 1
                        )
                        pygame.draw.line(
                            surf, (246, 241, 230), (ret.left + 1, ret.top + 1), (ret.left + 1, ret.bottom - 2), 1
                        )
                        pygame.draw.line(
                            surf, (196, 186, 170), (ret.left + 2, ret.bottom - 2), (ret.right - 2, ret.bottom - 2), 1
                        )

        if not modo_alto_contraste and numero_fase in (1, 4):
            pygame.draw.rect(surf, cores["ciclovia_vermelha"], (0, TILE, LARGURA, 12))
            for x_traco in range(12, LARGURA, 40):
                pygame.draw.rect(surf, (250, 246, 238), (x_traco, TILE + 5, 18, 2))

        pygame.draw.rect(surf, cores["meio_fio"], (0, TILE - 6, LARGURA, 6))
        pygame.draw.rect(surf, cores["meio_fio"], (0, (ROWS - 1) * TILE - 4, LARGURA, 6))
        if not modo_alto_contraste:
            pygame.draw.rect(surf, (132, 122, 108), (0, (ROWS - 1) * TILE + 2, LARGURA, 6))
            pygame.draw.rect(surf, (52, 58, 68), (0, (ROWS - 1) * TILE + 8, LARGURA, 4))

        for x_faixa in range(24, LARGURA - 120, 72):
            pygame.draw.rect(
                surf,
                cores["faixa_rua"],
                (x_faixa, (ROWS - 1) * TILE + 20, 38, 10),
                border_radius=3,
            )

        if not modo_alto_contraste:
            if numero_fase == 1:
                pygame.draw.rect(surf, (148, 104, 62), (0, TILE - 12, LARGURA, 7))
                for x_p in range(0, LARGURA, 24):
                    pygame.draw.line(surf, (108, 72, 42), (x_p, TILE - 12), (x_p, TILE - 5), 2)
                for x_coq in (84, 276, 486, 696, 864):
                    pygame.draw.ellipse(surf, (54, 88, 62), (x_coq + 8, 30, 28, 10))
                    pygame.draw.circle(surf, (44, 122, 54), (x_coq, 24), 17)
                    pygame.draw.circle(surf, (88, 174, 84), (x_coq - 5, 18), 11)
                self._desenhar_vermelhinho(surf, LARGURA - 110, (ROWS - 1) * TILE + 8, cores)

            elif numero_fase == 2:
                pygame.draw.rect(surf, (238, 220, 188), (600, 14, 340, 28), border_radius=4)
                pygame.draw.rect(surf, (198, 86, 44), (596, 2, 348, 16), border_radius=5)
                pygame.draw.rect(surf, (226, 114, 64), (600, 3, 340, 6), border_radius=3)
                for jx in range(622, 920, 44):
                    pygame.draw.rect(surf, (110, 152, 184), (jx, 20, 24, 16), border_radius=2)
                    pygame.draw.rect(surf, (196, 234, 255), (jx + 2, 22, 20, 10), border_radius=1)
                for x_arv in (64, 196, 336, 488):
                    pygame.draw.ellipse(surf, (56, 108, 56), (x_arv - 10, 30, 32, 10))
                    pygame.draw.circle(surf, (56, 132, 62), (x_arv, 20), 17)
                    pygame.draw.circle(surf, (104, 178, 92), (x_arv - 4, 16), 11)

            elif numero_fase == 3:
                pygame.draw.ellipse(surf, (58, 104, 54), (452, 28, 62, 16))
                pygame.draw.circle(surf, (236, 226, 208), (480, 22), 21)
                pygame.draw.circle(surf, (186, 56, 48), (480, 19), 15)
                pygame.draw.circle(surf, (226, 86, 72), (476, 15), 9)
                for x_ipe in (72, 212, 344, 616, 756, 888):
                    pygame.draw.ellipse(surf, (56, 104, 54), (x_ipe - 8, 30, 30, 10))
                    pygame.draw.circle(surf, (218, 160, 8), (x_ipe, 22), 16)
                    pygame.draw.circle(surf, (254, 232, 118), (x_ipe - 4, 17), 10)
                    pygame.draw.circle(surf, (250, 204, 21), (x_ipe + 10, TILE + 18), 3)
                    pygame.draw.circle(surf, (254, 240, 138), (x_ipe - 12, TILE + 30), 2)

            elif numero_fase == 4:
                pygame.draw.rect(surf, (236, 242, 248), (648, 12, 294, 30), border_radius=5)
                pygame.draw.rect(surf, (206, 216, 228), (644, 2, 302, 12), border_radius=4)
                pygame.draw.rect(surf, (214, 48, 48), (784, 18, 26, 8))
                pygame.draw.rect(surf, (214, 48, 48), (793, 10, 8, 24))
                self._desenhar_vermelhinho(surf, 36, (ROWS - 1) * TILE + 8, cores)

        if pygame.display.get_surface() is not None:
            surf = surf.convert()
        return surf

    def desenhar_iluminacao_25d(
        self,
        tela: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Aplica um brilho solar litorâneo quente em cache (desligado no alto contraste)."""
        if modo_alto_contraste:
            return
        if self._cache_luz_solar is None:
            luz = pygame.Surface((LARGURA, ROWS * TILE), pygame.SRCALPHA)
            pygame.draw.polygon(
                luz, (255, 244, 200, 20), [(0, 0), (340, 0), (140, ROWS * TILE), (0, ROWS * TILE)]
            )
            pygame.draw.polygon(
                luz, (255, 244, 200, 14), [(420, 0), (660, 0), (460, ROWS * TILE), (240, ROWS * TILE)]
            )
            self._cache_luz_solar = luz
        tela.blit(self._cache_luz_solar, (0, HUD_ALTURA))

    def desenhar_ambiente_vivo(
        self,
        tela: pygame.Surface,
        numero_fase: int,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha animação ambiental super leve (brilho na lagoa / pétalas de ipê)."""
        if modo_alto_contraste:
            return
        cores = self.paleta(False)
        t = self.tempo_animacao
        if numero_fase in (1, 4):
            limite_x = LARGURA - 40 if numero_fase == 1 else 620
            for idx, base_x in enumerate(range(30, limite_x, 96)):
                desl = round(math.sin(t * 2.2 + idx) * 8)
                y_onda = HUD_ALTURA + 16 + (idx % 2) * 10
                pygame.draw.line(
                    tela, cores["lagoa_brilho"], (base_x + desl, y_onda), (base_x + desl + 26, y_onda), 2
                )
        elif numero_fase == 3:
            for idx in range(5):
                px = int((idx * 195 + t * 18) % LARGURA)
                py = HUD_ALTURA + 28 + int(math.sin(t * 1.8 + idx) * 14) + idx * 4
                pygame.draw.circle(tela, (254, 226, 98), (px, py), 3)

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

    def desenhar_visao_barreiras(
        self,
        tela: pygame.Surface,
        grupo_interativos: pygame.sprite.Group,
        barreira_erro: Optional[Barreira],
        modo_raio_x: bool,
        modo_alto_contraste: bool,
    ) -> None:
        """Destaca barreiras pendentes no modo Raio-X [TAB] e o último bloqueio em vermelho."""
        cores = self.paleta(modo_alto_contraste)
        pulso = round(2 + 3 * (0.5 + 0.5 * math.sin(self.tempo_animacao * 6.0)))

        if modo_raio_x:
            for sprite in grupo_interativos:
                if isinstance(sprite, Barreira) and sprite.alteravel:
                    ret = sprite.rect.inflate(pulso, pulso)
                    pygame.draw.rect(tela, cores["rota_preview"], ret, 3, border_radius=8)

        if barreira_erro is not None and barreira_erro.alive() and barreira_erro.bloqueia_morador:
            ret_erro = barreira_erro.rect.inflate(pulso + 2, pulso + 2)
            pygame.draw.rect(tela, cores["erro_borda"], ret_erro, 4, border_radius=8)

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

        self.botao_testar_hud = pygame.Rect(790, 8, 160, 50)
        cor_btn = cores["rota_preview"] if testando_rota else cores["destaque_e"]
        pygame.draw.rect(tela, cor_btn, self.botao_testar_hud, border_radius=8)
        pygame.draw.rect(
            tela, cores["destaque_e_texto"], self.botao_testar_hud, 2, border_radius=8
        )
        rotulo_btn = "TESTANDO..." if testando_rota else "TESTAR [ESPAÇO]"
        txt_btn = self.fonte_pequena.render(rotulo_btn, True, cores["destaque_e_texto"])
        tela.blit(txt_btn, txt_btn.get_rect(center=self.botao_testar_hud.center))

        chave_at = (
            modo_alto_contraste,
            self.fonte_grande,
            audio_ativo,
            musica_ativa,
            False,
        )
        if self._cache_atalhos_chave != chave_at or self._cache_atalhos_surf is None:
            contraste_txt = "ALTO" if modo_alto_contraste else "NORM"
            fonte_txt = "G" if self.fonte_grande else "N"
            som_txt = "ON" if audio_ativo else "OFF"
            mus_txt = "ON" if (audio_ativo and musica_ativa) else "OFF"
            atalhos = (
                f"[WASD] Mover  [SHIFT] Correr  [E/Clique] Obra  [TAB] Raio-X  [R] Reiniciar  |  "
                f"[C]{contraste_txt} [F]{fonte_txt} [M]{som_txt} [N]{mus_txt}"
            )
            self._cache_atalhos_surf = self.fonte_pequena.render(
                atalhos, True, cores["texto_secundario"]
            )
            self._cache_atalhos_chave = chave_at
        tela.blit(self._cache_atalhos_surf, (14, 67))

    def desenhar_feedback_inferior(
        self,
        tela: pygame.Surface,
        retrato_morador: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha a caixa educativa inferior usando texto pré-renderizado em cache."""
        if not self.mensagem_feedback or self.tempo_feedback <= 0.0:
            return

        cores = self.paleta(modo_alto_contraste)
        eh_ok = self.tipo_feedback == "OK"
        cor_fundo = cores["sucesso_fundo"] if eh_ok else cores["erro_fundo"]
        cor_borda = cores["sucesso_borda"] if eh_ok else cores["erro_borda"]
        prefixo = "✓ " if eh_ok else "💬 "

        ret = pygame.Rect(16, ALTURA - ALTURA_FEEDBACK - 10, LARGURA - 32, ALTURA_FEEDBACK)
        pygame.draw.rect(tela, cor_fundo, ret, border_radius=10)
        pygame.draw.rect(tela, cor_borda, ret, 3, border_radius=10)

        tela.blit(retrato_morador, (ret.x + 12, ret.y + (ret.height - 40) // 2))

        chave = (self.mensagem_feedback, self.tipo_feedback, modo_alto_contraste, self.fonte_grande)
        if self._cache_feedback_chave != chave or self._cache_feedback_surf is None:
            larg_txt = ret.width - 78
            surf_txt = pygame.Surface((larg_txt, ret.height - 14), pygame.SRCALPHA)
            self._desenhar_texto_quebrado(
                surf_txt,
                prefixo + self.mensagem_feedback,
                self.fonte_normal,
                cores["texto_principal"],
                0,
                0,
                larg_txt,
                espacamento=2,
            )
            self._cache_feedback_surf = surf_txt
            self._cache_feedback_chave = chave

        tela.blit(self._cache_feedback_surf, (ret.x + 62, ret.y + 10))

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

        faixa_topo = pygame.Rect(painel.x, painel.y, painel.width, 118)
        pygame.draw.rect(
            tela,
            cores["hud_fundo"],
            faixa_topo,
            border_top_left_radius=16,
            border_top_right_radius=16,
        )
        titulo = self.fonte_titulo.render("ROTA ACESSÍVEL — MARICÁ/RJ", True, cores["destaque_e"])
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, painel.y + 44)))
        sub = self.fonte_media.render(
            "Orla de Araçatiba · Centro · Praça Orlando · Itaipuaçu (ABNT NBR 9050)",
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

    def desenhar_briefing(
        self,
        tela: pygame.Surface,
        metadados_fase: Dict[str, object],
        total_fases: int,
        retrato_grande: pygame.Surface,
        modo_alto_contraste: bool,
    ) -> None:
        """Desenha o popup amigável antes do início da fase com botão 'Ajudar'.

        O cronômetro permanece pausado até o jogador clicar em 'Ajudar' ou
        pressionar ENTER/ESPAÇO.

        Args:
            tela: Superfície principal do jogo.
            metadados_fase: Dicionário de dados da fase atual.
            total_fases: Total de fases da campanha.
            retrato_grande: Sprite 64x64 do morador da fase.
            modo_alto_contraste: Estado atual do modo de alto contraste.
        """
        self.botoes_ativos.clear()
        cores = self.paleta(modo_alto_contraste)
        if modo_alto_contraste not in self._cache_overlay:
            ov = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            ov.fill(cores["overlay"])
            self._cache_overlay[modo_alto_contraste] = ov
        tela.blit(self._cache_overlay[modo_alto_contraste], (0, 0))

        cartao = pygame.Rect(130, 88, LARGURA - 260, 444)
        pygame.draw.rect(tela, cores["painel_fundo"], cartao, border_radius=18)
        pygame.draw.rect(
            tela,
            cores["hud_borda"],
            cartao,
            BORDA_ALTO_CONTRASTE if modo_alto_contraste else 3,
            border_radius=18,
        )

        faixa = pygame.Rect(cartao.x, cartao.y, cartao.width, 76)
        pygame.draw.rect(
            tela,
            cores["hud_fundo"],
            faixa,
            border_top_left_radius=16,
            border_top_right_radius=16,
        )
        numero = int(metadados_fase["numero"])
        badge = self.fonte_pequena.render(
            f"FASE {numero} DE {total_fases}  ·  MARICÁ / RJ",
            True,
            cores["destaque_e"],
        )
        tela.blit(badge, (cartao.x + 26, cartao.y + 12))
        titulo = self.fonte_subtitulo.render(
            str(metadados_fase["nome"]), True, cores["texto_principal"]
        )
        tela.blit(titulo, (cartao.x + 26, cartao.y + 36))

        cx_av, cy_av = cartao.x + 68, cartao.y + 144
        pygame.draw.circle(tela, cores["botao_hover"], (cx_av, cy_av), 42)
        pygame.draw.circle(tela, cores["hud_borda"], (cx_av, cy_av), 42, 3)
        tela.blit(retrato_grande, retrato_grande.get_rect(center=(cx_av, cy_av)))

        nome_morador = str(metadados_fase["nome_morador"])
        tela.blit(
            self.fonte_subtitulo.render(nome_morador, True, cores["texto_escuro"]),
            (cartao.x + 126, cartao.y + 104),
        )
        tela.blit(
            self.fonte_pequena.render(
                str(metadados_fase["perfil_morador"]),
                True,
                cores["texto_suave_escuro"],
            ),
            (cartao.x + 126, cartao.y + 132),
        )

        balao = pygame.Rect(cartao.x + 126, cartao.y + 160, cartao.width - 156, 86)
        pygame.draw.rect(tela, cores["botao_hover"], balao, border_radius=12)
        pygame.draw.rect(tela, cores["painel_borda"], balao, 2, border_radius=12)
        self._desenhar_texto_quebrado(
            tela,
            str(metadados_fase["descricao"]),
            self.fonte_normal,
            cores["texto_escuro"],
            balao.x + 14,
            balao.y + 12,
            balao.width - 28,
            espacamento=4,
        )

        pilulas = [
            f"Orçamento: {metadados_fase['recursos']} obras",
            f"Tempo: {int(float(metadados_fase['tempo']))}s",
            f"Destino: {metadados_fase['local_destino']}",
        ]
        larg_p = (cartao.width - 72) // 3
        y_p = cartao.y + 266
        for idx, texto_p in enumerate(pilulas):
            ret_p = pygame.Rect(cartao.x + 26 + idx * (larg_p + 10), y_p, larg_p, 40)
            pygame.draw.rect(tela, cores["hud_fundo"], ret_p, border_radius=8)
            render_p = self.fonte_pequena.render(texto_p, True, cores["texto_principal"])
            tela.blit(render_p, render_p.get_rect(center=ret_p.center))

        dica = self.fonte_pequena.render(
            "Dica: Use WASD/Setas (+ SHIFT p/ correr) ou clique na calçada · [E] resolve barreiras · [ESPAÇO] testa a rota!",
            True,
            cores["texto_suave_escuro"],
        )
        tela.blit(dica, dica.get_rect(center=(LARGURA // 2, cartao.y + 334)))

        self._desenhar_botao(
            tela,
            "ajudar",
            pygame.Rect(cartao.centerx - 165, cartao.y + 362, 330, 52),
            f"Ajudar {nome_morador}!  [ENTER]",
            modo_alto_contraste,
            destaque=True,
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
            "MARICÁ MAIS ACESSÍVEL — CAMPANHA CONCLUÍDA!"
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
            "MAPA DE MARICÁ/RJ — SELECIONE UMA ROTA",
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
