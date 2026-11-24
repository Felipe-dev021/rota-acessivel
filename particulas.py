"""Sistema de partículas geométricas leves e otimizadas para 60 FPS estáveis.

Desenha diretamente sobre a superfície da janela sem alocar novas superfícies
por frame, garantindo desempenho fluido sem flashes bruscos ou tremores.
"""

import math
import random
from typing import List, Sequence, Tuple

import pygame

CorRGB = Tuple[int, int, int]


class Particula:
    """Representa uma partícula geométrica suave atualizada com float + dt."""

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
        """Inicializa a partícula com posição, velocidade, cor e duração."""
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
        """Atualiza posição com amortecimento suave e decrementa vida restante."""
        self.vida -= dt
        if self.vida <= 0.0:
            return False

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        fator_atrito = max(0.0, 1.0 - 3.0 * dt)
        self.vel_x *= fator_atrito
        self.vel_y *= fator_atrito
        return True

    def desenhar(self, tela: pygame.Surface) -> None:
        """Desenha a partícula diretamente na tela com encolhimento suave."""
        progresso = max(0.0, min(1.0, self.vida / self.vida_max))
        raio_atual = max(1, round(self.raio * progresso))
        px = round(self.pos_x)
        py = round(self.pos_y)

        if self.forma == "quadrado":
            ret = pygame.Rect(
                px - raio_atual, py - raio_atual, raio_atual * 2, raio_atual * 2
            )
            pygame.draw.rect(tela, self.cor, ret, border_radius=2)
        else:
            pygame.draw.circle(tela, self.cor, (px, py), raio_atual)


class SistemaParticulas:
    """Gerencia a emissão, atualização por dt e desenho leve de partículas."""

    def __init__(self) -> None:
        """Inicializa a lista vazia de partículas ativas."""
        self.particulas: List[Particula] = []

    def emitir_intervencao(
        self,
        centro_x: float,
        centro_y: float,
        cor: CorRGB,
        quantidade: int = 10,
    ) -> None:
        """Emite partículas geométricas suaves ao resolver uma barreira."""
        for indice in range(quantidade):
            angulo = (2.0 * math.pi * indice / max(1, quantidade)) + random.uniform(-0.2, 0.2)
            velocidade = random.uniform(40.0, 92.0)
            forma = "quadrado" if indice % 2 == 0 else "circulo"
            self.particulas.append(
                Particula(
                    pos_x=centro_x,
                    pos_y=centro_y,
                    vel_x=math.cos(angulo) * velocidade,
                    vel_y=math.sin(angulo) * velocidade,
                    raio=random.uniform(3.5, 5.5),
                    cor=cor,
                    vida_max=random.uniform(0.35, 0.55),
                    forma=forma,
                )
            )

    def emitir_vitoria(
        self,
        centro_x: float,
        centro_y: float,
        cores: Sequence[CorRGB],
        quantidade: int = 18,
    ) -> None:
        """Emite partículas comemorativas suaves ao concluir a fase."""
        if not cores:
            return
        for indice in range(quantidade):
            angulo = random.uniform(0.0, 2.0 * math.pi)
            velocidade = random.uniform(45.0, 120.0)
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
                    vida_max=random.uniform(0.50, 0.80),
                    forma=forma,
                )
            )

    def limpar(self) -> None:
        """Remove todas as partículas ativas."""
        self.particulas.clear()

    def atualizar(self, dt: float) -> None:
        """Atualiza todas as partículas ativas e descarta as expiradas."""
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]

    def desenhar(self, tela: pygame.Surface) -> None:
        """Desenha todas as partículas ativas diretamente na superfície principal."""
        for particula in self.particulas:
            particula.desenhar(tela)
