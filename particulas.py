"""Sistema de partículas geométricas suaves para feedback visual ('juice').

Implementa a classe SistemaParticulas sem flashes bruscos ou tremores de tela,
respeitando diretrizes de acessibilidade visual e atualização por delta time.
"""

import math
import random
from typing import List, Sequence, Tuple

import pygame

CorRGB = Tuple[int, int, int]


class Particula:
    """Representa uma partícula geométrica individual atualizada em float + dt."""

    def __init__(
        self,
        pos_x: float,
        pos_y: float,
        vel_x: float,
        vel_y: float,
        raio: float,
        cor: CorRGB,
        vida_max: float,
        forma: str = "circulo",
    ) -> None:
        """Inicializa uma partícula suave com posição, velocidade e tempo de vida.

        Args:
            pos_x: Coordenada X inicial em pixels (float).
            pos_y: Coordenada Y inicial em pixels (float).
            vel_x: Velocidade horizontal em pixels por segundo.
            vel_y: Velocidade vertical em pixels por segundo.
            raio: Raio ou meia-largura inicial em pixels.
            cor: Cor RGB da partícula.
            vida_max: Duração total de vida em segundos.
            forma: 'circulo' ou 'quadrado'.
        """
        self.pos_x: float = pos_x
        self.pos_y: float = pos_y
        self.vel_x: float = vel_x
        self.vel_y: float = vel_y
        self.raio: float = raio
        self.cor: CorRGB = cor
        self.vida_max: float = max(0.05, vida_max)
        self.vida: float = self.vida_max
        self.forma: str = forma

    def atualizar(self, dt: float) -> bool:
        """Atualiza posição com amortecimento suave e reduz o tempo de vida.

        Args:
            dt: Tempo decorrido em segundos desde o último frame.

        Returns:
            True enquanto a partícula ainda estiver ativa; False quando expirar.
        """
        self.vida -= dt
        if self.vida <= 0.0:
            return False

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        # Amortecimento leve para movimento orgânico e confortável
        fator_atrito = max(0.0, 1.0 - 2.6 * dt)
        self.vel_x *= fator_atrito
        self.vel_y *= fator_atrito
        return True

    def desenhar(self, tela: pygame.Surface) -> None:
        """Desenha a partícula com transparência proporcional à vida restante.

        Args:
            tela: Superfície principal de renderização.
        """
        progresso = max(0.0, min(1.0, self.vida / self.vida_max))
        raio_atual = max(1, round(self.raio * (0.45 + 0.55 * progresso)))
        alpha = int(200 * progresso)
        tamanho = raio_atual * 2 + 2

        superficie = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        cor_rgba = (self.cor[0], self.cor[1], self.cor[2], alpha)
        centro = tamanho // 2

        if self.forma == "quadrado":
            pygame.draw.rect(
                superficie,
                cor_rgba,
                (1, 1, raio_atual * 2, raio_atual * 2),
                border_radius=2,
            )
        else:
            pygame.draw.circle(superficie, cor_rgba, (centro, centro), raio_atual)

        tela.blit(superficie, (round(self.pos_x) - centro, round(self.pos_y) - centro))


class SistemaParticulas:
    """Gerencia a emissão, atualização por dt e desenho de partículas suaves."""

    def __init__(self) -> None:
        """Inicializa a lista vazia de partículas ativas."""
        self.particulas: List[Particula] = []

    def emitir_intervencao(
        self,
        centro_x: float,
        centro_y: float,
        cor: CorRGB,
        quantidade: int = 12,
    ) -> None:
        """Emite partículas geométricas suaves ao resolver uma barreira.

        Args:
            centro_x: Coordenada X central do tile resolvido.
            centro_y: Coordenada Y central do tile resolvido.
            cor: Cor principal relacionada à intervenção realizada.
            quantidade: Número de partículas geradas.
        """
        for indice in range(quantidade):
            angulo = (2.0 * math.pi * indice / max(1, quantidade)) + random.uniform(-0.2, 0.2)
            velocidade = random.uniform(35.0, 88.0)
            forma = "quadrado" if indice % 2 == 0 else "circulo"
            self.particulas.append(
                Particula(
                    pos_x=centro_x,
                    pos_y=centro_y,
                    vel_x=math.cos(angulo) * velocidade,
                    vel_y=math.sin(angulo) * velocidade,
                    raio=random.uniform(3.5, 5.5),
                    cor=cor,
                    vida_max=random.uniform(0.40, 0.65),
                    forma=forma,
                )
            )

    def emitir_vitoria(
        self,
        centro_x: float,
        centro_y: float,
        cores: Sequence[CorRGB],
        quantidade: int = 20,
    ) -> None:
        """Emite partículas comemorativas suaves ao concluir uma fase.

        Args:
            centro_x: Coordenada X do ponto de destino.
            centro_y: Coordenada Y do ponto de destino.
            cores: Sequência de cores RGB da paleta ativa.
            quantidade: Total de partículas a emitir.
        """
        if not cores:
            return
        for indice in range(quantidade):
            angulo = random.uniform(0.0, 2.0 * math.pi)
            velocidade = random.uniform(40.0, 115.0)
            cor = cores[indice % len(cores)]
            forma = "circulo" if indice % 2 == 0 else "quadrado"
            self.particulas.append(
                Particula(
                    pos_x=centro_x,
                    pos_y=centro_y,
                    vel_x=math.cos(angulo) * velocidade,
                    vel_y=math.sin(angulo) * velocidade,
                    raio=random.uniform(4.0, 6.5),
                    cor=cor,
                    vida_max=random.uniform(0.55, 0.90),
                    forma=forma,
                )
            )

    def limpar(self) -> None:
        """Remove todas as partículas ativas (usado ao trocar ou reiniciar fase)."""
        self.particulas.clear()

    def atualizar(self, dt: float) -> None:
        """Atualiza todas as partículas ativas e descarta as expiradas.

        Args:
            dt: Tempo decorrido em segundos desde o frame anterior.
        """
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]

    def desenhar(self, tela: pygame.Surface) -> None:
        """Desenha todas as partículas ativas na tela.

        Args:
            tela: Superfície principal do jogo.
        """
        for particula in self.particulas:
            particula.desenhar(tela)
