"""Controlador principal e máquina de estados do jogo educativo 'Rota Acessível'.

Implementa a classe JogoRotaAcessivel seguindo rigorosamente:
- Inicialização segura do mixer de áudio (try/except);
- Arquitetura de grupos com grupo_desenho único para update(dt) e draw();
- Game loop estrito a 60 FPS com dt limitado a DT_MAXIMO (0.05 s);
- Máquina de estados: MENU, INSTRUCOES, JOGANDO, PAUSA, TRANSICAO e FIM.
"""

from typing import Dict, Optional

import pygame

from config import (
    ALTURA,
    ARQUIVO_MUSICA_FUNDO,
    ARQUIVO_SOM_ACAO,
    ARQUIVO_SOM_CLIQUE,
    ARQUIVO_SOM_ERRO,
    ARQUIVO_SOM_VITORIA,
    AUDIO_VOLUME_EFEITOS,
    AUDIO_VOLUME_MUSICA,
    DT_MAXIMO,
    DURACAO_FEEDBACK,
    ESTADO_FIM,
    ESTADO_INSTRUCOES,
    ESTADO_JOGANDO,
    ESTADO_MENU,
    ESTADO_PAUSA,
    ESTADO_TRANSICAO,
    FPS,
    LARGURA,
    PENALIDADE_ERRO,
    TITULO_JOGO,
    caminho_arquivo,
)
from fase import GerenciadorFases
from hud import HUD
from morador import Morador
from particulas import SistemaParticulas
from player import Jogador
from save_manager import GerenciadorSave


class JogoRotaAcessivel:
    """Orquestra o ciclo de vida, os grupos de sprites e os estados do jogo."""

    def __init__(self) -> None:
        """Inicializa pygame, janela, áudio seguro, entidades e grupos."""
        pygame.init()
        self.tela: pygame.Surface = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption(TITULO_JOGO)
        self.relogio: pygame.time.Clock = pygame.time.Clock()

        self.executando: bool = True
        self.estado: str = ESTADO_MENU
        self.save: GerenciadorSave = GerenciadorSave()
        prefs = self.save.obter_preferencias()
        self.modo_alto_contraste: bool = prefs["alto_contraste"]
        self.fonte_grande: bool = prefs["fonte_grande"]
        self.audio_ativo: bool = prefs["som_ativo"]
        self.musica_ativa: bool = prefs["musica_ativa"]
        self.vitoria_campanha: bool = False

        self.sons: Dict[str, Optional[pygame.mixer.Sound]] = self._carregar_sons()
        self._iniciar_musica_fundo()
        self.hud: HUD = HUD()
        self.hud.atualizar_fontes(self.fonte_grande)
        self.particulas: SistemaParticulas = SistemaParticulas()
        self.fases: GerenciadorFases = GerenciadorFases()
        self.fases.carregar_fase(0, self.modo_alto_contraste, self.fonte_grande)

        self.jogador: Jogador = Jogador(
            self.fases.inicio_jogador[0],
            self.fases.inicio_jogador[1],
            self.fases.grupo_solidos,
            self.modo_alto_contraste,
            self.fonte_grande,
        )
        self.morador: Morador = Morador(
            self.fases.inicio_morador[0],
            self.fases.inicio_morador[1],
            self.modo_alto_contraste,
            self.fonte_grande,
        )

        # Único grupo que executa update(dt) e draw(tela) a cada frame
        self.grupo_desenho: pygame.sprite.Group = pygame.sprite.Group()
        self._reconstruir_grupo_desenho()
        self.ultimo_resumo_fase: Dict[str, object] = {}

    def _carregar_sons(self) -> Dict[str, Optional[pygame.mixer.Sound]]:
        """Carrega os efeitos WAV via caminho_arquivo() com proteção contra falhas.

        Returns:
            Dicionário mapeando nomes lógicos aos objetos Sound (ou None).
        """
        mapa_arquivos = {
            "acao": ARQUIVO_SOM_ACAO,
            "erro": ARQUIVO_SOM_ERRO,
            "vitoria": ARQUIVO_SOM_VITORIA,
            "clique": ARQUIVO_SOM_CLIQUE,
        }
        sons: Dict[str, Optional[pygame.mixer.Sound]] = {k: None for k in mapa_arquivos}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for chave, nome_arquivo in mapa_arquivos.items():
                som = pygame.mixer.Sound(caminho_arquivo(nome_arquivo))
                som.set_volume(AUDIO_VOLUME_EFEITOS)
                sons[chave] = som
        except pygame.error:
            return sons
        return sons

    def _iniciar_musica_fundo(self) -> None:
        """Carrega e inicia a trilha sonora calma em loop via pygame.mixer.music."""
        try:
            if not pygame.mixer.get_init():
                return
            pygame.mixer.music.load(caminho_arquivo(ARQUIVO_MUSICA_FUNDO))
            pygame.mixer.music.set_volume(
                AUDIO_VOLUME_MUSICA if (self.audio_ativo and self.musica_ativa) else 0.0
            )
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _atualizar_volume_musica(self) -> None:
        """Sincroniza o volume da trilha de fundo com audio_ativo e musica_ativa."""
        try:
            if pygame.mixer.get_init():
                volume = (
                    AUDIO_VOLUME_MUSICA
                    if (self.audio_ativo and self.musica_ativa)
                    else 0.0
                )
                pygame.mixer.music.set_volume(volume)
        except pygame.error:
            pass

    def _tocar_som(self, chave: str) -> None:
        """Reproduz o efeito sonoro informado se o áudio estiver ativo.

        Args:
            chave: Identificador do efeito ('acao', 'erro', 'vitoria', 'clique').
        """
        if not self.audio_ativo:
            return
        som = self.sons.get(chave)
        if som is not None:
            som.play()

    def _reconstruir_grupo_desenho(self) -> None:
        """Sincroniza grupo_desenho mantendo barreiras abaixo dos personagens."""
        self.grupo_desenho.empty()
        for barreira in self.fases.grupo_barreiras:
            self.grupo_desenho.add(barreira)
        self.grupo_desenho.add(self.morador, self.jogador)

    def _sincronizar_fase_atual(self) -> None:
        """Vincula entidades e grupos de colisão à fase recém-carregada."""
        self.jogador.definir_grupo_solidos(self.fases.grupo_solidos)
        self.jogador.reposicionar(*self.fases.inicio_jogador)
        self.jogador.movimento_habilitado = True
        self.morador.cancelar_teste()
        self.morador.reposicionar(*self.fases.inicio_morador)
        self._reconstruir_grupo_desenho()
        self.particulas.limpar()
        self.hud.limpar_feedback()

    def _salvar_preferencias(self) -> None:
        """Persiste as preferências atuais de acessibilidade em progresso.json."""
        self.save.atualizar_preferencias(
            self.modo_alto_contraste,
            self.fonte_grande,
            self.audio_ativo,
            self.musica_ativa,
        )

    def _alternar_contraste(self) -> None:
        """Alterna o Modo Alto Contraste em tempo real em qualquer tela."""
        self.modo_alto_contraste = not self.modo_alto_contraste
        self.fases.atualizar_visual_barreiras(
            self.modo_alto_contraste, self.fonte_grande
        )
        self.jogador.atualizar_visual(self.modo_alto_contraste, self.fonte_grande)
        self.morador.atualizar_visual(self.modo_alto_contraste, self.fonte_grande)
        self._salvar_preferencias()
        self._tocar_som("clique")

    def _alternar_fonte(self) -> None:
        """Alterna o tamanho da fonte (Normal / Grande) em tempo real."""
        self.fonte_grande = not self.fonte_grande
        self.hud.atualizar_fontes(self.fonte_grande)
        self.fases.atualizar_visual_barreiras(
            self.modo_alto_contraste, self.fonte_grande
        )
        self.jogador.atualizar_visual(self.modo_alto_contraste, self.fonte_grande)
        self.morador.atualizar_visual(self.modo_alto_contraste, self.fonte_grande)
        self._salvar_preferencias()
        self._tocar_som("clique")

    def _alternar_audio(self) -> None:
        """Ativa ou silencia todos os efeitos sonoros e a trilha de fundo."""
        self.audio_ativo = not self.audio_ativo
        self._atualizar_volume_musica()
        self._salvar_preferencias()
        if self.audio_ativo:
            self._tocar_som("clique")

    def _alternar_musica(self) -> None:
        """Ativa ou silencia exclusivamente a trilha sonora de fundo."""
        self.musica_ativa = not self.musica_ativa
        self._atualizar_volume_musica()
        self._salvar_preferencias()
        self._tocar_som("clique")

    def _iniciar_nova_campanha(self) -> None:
        """Inicia uma nova campanha a partir da Fase 1."""
        self.vitoria_campanha = False
        self.fases.reiniciar_campanha(self.modo_alto_contraste, self.fonte_grande)
        self._sincronizar_fase_atual()
        self.estado = ESTADO_JOGANDO
        self.hud.definir_feedback(
            str(self.fases.metadados_atual["descricao"]),
            "OK",
            DURACAO_FEEDBACK,
        )

    def _reiniciar_fase_atual(self) -> None:
        """Reinicia integralmente a fase atual e retorna ao estado JOGANDO."""
        self.fases.reiniciar_fase(self.modo_alto_contraste, self.fonte_grande)
        self._sincronizar_fase_atual()
        self.estado = ESTADO_JOGANDO
        self._tocar_som("clique")
        self.hud.definir_feedback(
            f"Fase reiniciada — {self.fases.metadados_atual['descricao']}",
            "OK",
            DURACAO_FEEDBACK,
        )

    def _aplicar_intervencao(self) -> None:
        """Aplica a intervenção de acessibilidade na barreira próxima a Alex."""
        if self.morador.em_movimento:
            return

        barreira = self.jogador.obter_barreira_proxima(self.fases.grupo_interativos)
        if barreira is None:
            return

        if barreira.custo > self.fases.recursos:
            self._tocar_som("erro")
            self.hud.definir_feedback(
                "Sem recursos suficientes! Pressione [R] para reiniciar a fase e replanejar.",
                "ERRO",
                DURACAO_FEEDBACK,
            )
            return

        centro_barreira = barreira.centro()
        cor_particula = self.hud.paleta(self.modo_alto_contraste)["sucesso_borda"]
        resolvida, mensagem = barreira.resolver(
            self.modo_alto_contraste, self.fonte_grande
        )
        if resolvida:
            self.fases.recursos -= barreira.custo
            self.fases.intervencoes_fase += 1
            if not barreira.alteravel and barreira in self.fases.grupo_interativos:
                self.fases.grupo_interativos.remove(barreira)
            self.particulas.emitir_intervencao(
                centro_barreira[0], centro_barreira[1], cor_particula[:3]
            )
            self._tocar_som("acao")

            # Caso de borda: alertar se o orçamento zerou com a rota ainda bloqueada
            if self.fases.recursos == 0:
                sucesso_previa, _, _ = self.morador.calcular_rota(
                    self.fases.obter_grade_barreiras(),
                    self.fases.inicio_morador,
                    self.fases.destino,
                )
                if not sucesso_previa:
                    mensagem = (
                        f"{mensagem} Orçamento zerado — se ainda houver bloqueio "
                        "pago, pressione [R] para reiniciar a fase."
                    )

            self.hud.definir_feedback(mensagem, "OK", DURACAO_FEEDBACK)

    def _iniciar_validacao_rota(self) -> None:
        """Aciona o BFS no Morador para validar a continuidade da faixa livre."""
        if self.morador.em_movimento:
            return

        self.fases.tentativas_teste_fase += 1
        grade = self.fases.obter_grade_barreiras()
        sucesso, caminho, barreira_bloqueio = self.morador.calcular_rota(
            grade,
            self.fases.inicio_morador,
            self.fases.destino,
        )
        self.jogador.movimento_habilitado = False
        self.morador.iniciar_teste(caminho, sucesso, barreira_bloqueio)
        self._tocar_som("clique")

    def _tratar_fim_por_tempo(self) -> None:
        """Encerra a fase atual quando o cronômetro atinge zero."""
        self.morador.cancelar_teste()
        self.jogador.movimento_habilitado = True
        self.fases.tempo_restante = 0.0
        self.fases.registrar_metricas_fase(concluida=False)
        self.vitoria_campanha = False
        self._tocar_som("erro")
        self.estado = ESTADO_FIM

    def _processar_eventos(self) -> None:
        """Processa os eventos do Pygame conforme o estado atual."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.executando = False
                return

            if evento.type != pygame.KEYDOWN:
                continue

            tecla = evento.key
            if tecla == pygame.K_c:
                self._alternar_contraste()
                continue
            if tecla == pygame.K_f:
                self._alternar_fonte()
                continue
            if tecla == pygame.K_m:
                self._alternar_audio()
                continue
            if tecla == pygame.K_n:
                self._alternar_musica()
                continue

            if self.estado == ESTADO_MENU:
                self._evento_menu(tecla)
            elif self.estado == ESTADO_INSTRUCOES:
                self._evento_instrucoes(tecla)
            elif self.estado == ESTADO_JOGANDO:
                self._evento_jogando(tecla)
            elif self.estado == ESTADO_PAUSA:
                self._evento_pausa(tecla)
            elif self.estado == ESTADO_TRANSICAO:
                self._evento_transicao(tecla)
            elif self.estado == ESTADO_FIM:
                self._evento_fim(tecla)

    def _evento_menu(self, tecla: int) -> None:
        """Trata comandos de teclado no estado MENU."""
        if tecla in (pygame.K_RETURN, pygame.K_SPACE):
            self._tocar_som("clique")
            self._iniciar_nova_campanha()
        elif tecla == pygame.K_i:
            self._tocar_som("clique")
            self.estado = ESTADO_INSTRUCOES
        elif tecla == pygame.K_ESCAPE:
            self.executando = False

    def _evento_instrucoes(self, tecla: int) -> None:
        """Trata comandos de teclado no estado INSTRUCOES."""
        if tecla in (pygame.K_RETURN, pygame.K_SPACE):
            self._tocar_som("clique")
            self._iniciar_nova_campanha()
        elif tecla in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self._tocar_som("clique")
            self.estado = ESTADO_MENU

    def _evento_jogando(self, tecla: int) -> None:
        """Trata comandos discretos de teclado no estado JOGANDO."""
        if tecla in (pygame.K_p, pygame.K_ESCAPE):
            self._tocar_som("clique")
            self.estado = ESTADO_PAUSA
        elif tecla == pygame.K_r:
            self._reiniciar_fase_atual()
        elif tecla == pygame.K_e:
            self._aplicar_intervencao()
        elif tecla in (pygame.K_SPACE, pygame.K_RETURN):
            self._iniciar_validacao_rota()

    def _evento_pausa(self, tecla: int) -> None:
        """Trata comandos de teclado no estado PAUSA."""
        if tecla in (pygame.K_p, pygame.K_ESCAPE):
            self._tocar_som("clique")
            self.estado = ESTADO_JOGANDO
        elif tecla == pygame.K_r:
            self._reiniciar_fase_atual()
        elif tecla == pygame.K_q:
            self._tocar_som("clique")
            self.estado = ESTADO_MENU

    def _evento_transicao(self, tecla: int) -> None:
        """Trata comandos de teclado no estado TRANSICAO."""
        if tecla in (pygame.K_RETURN, pygame.K_SPACE):
            self._tocar_som("clique")
            if self.fases.avancar_fase(self.modo_alto_contraste, self.fonte_grande):
                self._sincronizar_fase_atual()
                self.estado = ESTADO_JOGANDO
                self.hud.definir_feedback(
                    str(self.fases.metadados_atual["descricao"]),
                    "OK",
                    DURACAO_FEEDBACK,
                )
            else:
                self.vitoria_campanha = True
                self.estado = ESTADO_FIM

    def _evento_fim(self, tecla: int) -> None:
        """Trata comandos de teclado no estado FIM."""
        if tecla == pygame.K_r:
            if self.vitoria_campanha:
                self._tocar_som("clique")
                self._iniciar_nova_campanha()
            else:
                self._reiniciar_fase_atual()
        elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
            self._tocar_som("clique")
            self.estado = ESTADO_MENU
        elif tecla == pygame.K_ESCAPE:
            self.executando = False

    def _atualizar(self, dt: float) -> None:
        """Atualiza o cronômetro, o HUD e todos os sprites via grupo_desenho."""
        if self.estado != ESTADO_JOGANDO:
            return

        self.hud.atualizar(dt)
        self.particulas.atualizar(dt)
        self.fases.tempo_restante -= dt
        self.grupo_desenho.update(dt)

    def _validar_regras(self) -> None:
        """Valida regras da partida: tempo esgotado e resultado do teste de rota."""
        if self.estado != ESTADO_JOGANDO:
            return

        if self.fases.tempo_restante <= 0.0:
            self._tratar_fim_por_tempo()
            return

        resultado_teste = self.morador.consumir_resultado()
        if resultado_teste == "VITORIA":
            self.jogador.movimento_habilitado = True
            cores_paleta = self.hud.paleta(self.modo_alto_contraste)
            self.particulas.emitir_vitoria(
                self.morador.rect.centerx,
                self.morador.rect.centery,
                (
                    cores_paleta["sucesso_borda"][:3],
                    cores_paleta["destaque_e"][:3],
                    cores_paleta["rota_preview"][:3],
                ),
            )
            self._tocar_som("vitoria")
            self.ultimo_resumo_fase = self.fases.registrar_metricas_fase(concluida=True)
            self.save.registrar_conclusao_fase(
                int(self.ultimo_resumo_fase["numero"]),
                self.fases.total_fases,
                str(self.ultimo_resumo_fase["nivel_autonomia"]),
                int(self.ultimo_resumo_fase["selos"]),
                int(self.ultimo_resumo_fase["erros_rota"]),
            )
            if self.fases.indice_atual + 1 < self.fases.total_fases:
                self.estado = ESTADO_TRANSICAO
            else:
                self.vitoria_campanha = True
                self.estado = ESTADO_FIM

        elif resultado_teste == "BLOQUEADO":
            self.jogador.movimento_habilitado = True
            self.fases.erros_rota_fase += 1
            self._tocar_som("erro")
            self.fases.tempo_restante = max(
                0.0, self.fases.tempo_restante - PENALIDADE_ERRO
            )

            barreira = self.morador.barreira_bloqueadora
            explicacao = (
                barreira.mensagem_erro
                if barreira is not None and barreira.mensagem_erro
                else "Rota bloqueada! Remova obstáculos ou desvie de postes fixos."
            )
            dica_reinicio = (
                " Sem recursos: pressione [R] para reiniciar a fase."
                if self.fases.recursos == 0
                else ""
            )
            self.hud.definir_feedback(
                f"{explicacao} (-{int(PENALIDADE_ERRO)}s){dica_reinicio}",
                "ERRO",
                DURACAO_FEEDBACK,
            )

            if self.fases.tempo_restante <= 0.0:
                self._tratar_fim_por_tempo()

    def _desenhar_cena_jogo(self) -> None:
        """Desenha a calçada, rastro do Morador, sprites, partículas e HUD."""
        self.hud.desenhar_grade_calcada(self.tela, self.modo_alto_contraste)
        self.hud.desenhar_rastro_morador(
            self.tela,
            self.morador.celulas_percorridas,
            self.morador.rota_sucesso,
            self.modo_alto_contraste,
        )
        self.grupo_desenho.draw(self.tela)
        self.hud.desenhar_marcadores_rota(
            self.tela,
            self.fases.inicio_morador,
            self.fases.destino,
            self.modo_alto_contraste,
        )
        self.particulas.desenhar(self.tela)

        if not self.morador.em_movimento:
            barreira_proxima = self.jogador.obter_barreira_proxima(
                self.fases.grupo_interativos
            )
            self.hud.desenhar_destaque_interacao(
                self.tela, barreira_proxima, self.modo_alto_contraste
            )

        meta = self.fases.metadados_atual
        self.hud.desenhar_barra_superior(
            self.tela,
            int(meta["numero"]),
            self.fases.total_fases,
            str(meta["nome"]),
            self.fases.tempo_restante,
            self.fases.recursos,
            self.modo_alto_contraste,
            self.audio_ativo,
            self.morador.em_movimento,
            self.musica_ativa,
        )
        self.hud.desenhar_feedback_inferior(self.tela, self.modo_alto_contraste)

    def _desenhar(self) -> None:
        """Desenha a tela correspondente ao estado ativo da máquina de estados."""
        if self.estado == ESTADO_MENU:
            self.hud.desenhar_menu(
                self.tela,
                self.modo_alto_contraste,
                self.audio_ativo,
                self.musica_ativa,
            )
        elif self.estado == ESTADO_INSTRUCOES:
            self.hud.desenhar_instrucoes(self.tela, self.modo_alto_contraste)
        elif self.estado == ESTADO_JOGANDO:
            self._desenhar_cena_jogo()
        elif self.estado == ESTADO_PAUSA:
            self._desenhar_cena_jogo()
            self.hud.desenhar_pausa(
                self.tela,
                self.modo_alto_contraste,
                self.audio_ativo,
                self.musica_ativa,
            )
        elif self.estado == ESTADO_TRANSICAO:
            self.hud.desenhar_transicao(
                self.tela,
                self.ultimo_resumo_fase,
                str(self.fases.metadados_atual["aprendizado"]),
                self.modo_alto_contraste,
            )
        elif self.estado == ESTADO_FIM:
            self.hud.desenhar_fim(
                self.tela,
                self.vitoria_campanha,
                self.fases.metricas_fases,
                self.modo_alto_contraste,
            )

    def executar(self) -> None:
        """Executa o Game Loop estrito: dt -> Eventos -> Update -> Regras -> Draw -> Flip."""
        while self.executando:
            dt = min(self.relogio.tick(FPS) / 1000.0, DT_MAXIMO)
            self._processar_eventos()
            self._atualizar(dt)
            self._validar_regras()
            self._desenhar()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    jogo = JogoRotaAcessivel()
    jogo.executar()
