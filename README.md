# Rota Acessível

**Serious Game 2D Top-Down** desenvolvido em Python com **pygame-ce** para a disciplina de **Desenvolvimento de Jogos Digitais** (7º período de Engenharia de Software) — **Tema 07: Acessibilidade e Inclusão**.

> *"Divertir é o meio. Resolver é o fim."*

---

## Problema Real Resolvido

Moradores e planejadores urbanos sem deficiência frequentemente não percebem barreiras cotidianas que impedem pessoas com deficiência física, visual ou auditiva de circular e se informar com autonomia: lixeiras bloqueando a faixa livre, degraus sem rebaixamento, buracos no pavimento, trechos críticos sem piso tátil direcional e avisos exclusivamente sonoros.

Em **Rota Acessível**, o aprendizado acontece diretamente pela **mecânica de jogo** (sem formato de quiz e sem gamificação superficial): o jogador controla **Alex** (agente de acessibilidade), analisa toda a calçada urbana em grade `20x11`, administra um orçamento limitado de intervenções e valida a continuidade da faixa livre acionando o **Morador** da fase, que percorre o trajeto via **Busca em Largura (BFS) em 4 direções**. A cada bloqueio real, o jogo explica o impacto concreto daquela barreira segundo a **ABNT NBR 9050:2020** e a **Lei Brasileira de Inclusão (LBI)**.

---

## Requisitos

- **Python 3.10 ou superior** (validado em Python 3.14)
- **pygame-ce** (declarado em `requirements.txt`)
- *(Opcional)* **PyInstaller** para gerar executável standalone

---

## Como Executar a Partir de uma Máquina Limpa

### Windows (PowerShell)

1. Abra o PowerShell na pasta raiz do projeto.
2. Crie o ambiente virtual isolado:
   ```powershell
   python -m venv .venv
   ```
3. Ative o ambiente virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
4. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
5. Gere todos os sprites PNG (`48x48`) e áudios WAV na pasta `data/`:
   ```powershell
   python gerar_assets.py
   ```
6. Execute o jogo:
   ```powershell
   python main.py
   ```

### Linux / macOS

1. Abra o terminal na pasta raiz do projeto.
2. Crie o ambiente virtual isolado:
   ```bash
   python3 -m venv .venv
   ```
3. Ative o ambiente virtual:
   ```bash
   source .venv/bin/activate
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
5. Gere todos os sprites PNG (`48x48`) e áudios WAV na pasta `data/`:
   ```bash
   python3 gerar_assets.py
   ```
6. Execute o jogo:
   ```bash
   python3 main.py
   ```

---

## Empacotamento Opcional com PyInstaller

O projeto já resolve caminhos de leitura (`caminho_arquivo()` com suporte a `sys._MEIPASS`) e escrita (`caminho_save()` gravando `progresso.json` ao lado do executável).

1. Com o `.venv` ativo, instale o PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Gere os assets antes de empacotar:
   ```powershell
   python gerar_assets.py
   ```
3. Gere o executável standalone:
   - **Windows (PowerShell):**
     ```powershell
     pyinstaller --onefile --windowed --add-data "data;data" main.py
     ```
   - **Linux / macOS:**
     ```bash
     pyinstaller --onefile --windowed --add-data "data:data" main.py
     ```
4. O executável estará disponível na pasta `dist/`.

---

## Controles e Recursos de Acessibilidade

| Tecla | Ação | Onde Funciona |
| :--- | :--- | :--- |
| `W`, `A`, `S`, `D` ou `Setas` | Move Alex em 8 direções (normalizado) / navega no Mapa | Jogando, Mapa |
| `E` | Aplica intervenção na barreira destacada `[E]` (raio de 64 px) | Jogando |
| `ESPAÇO` ou `ENTER` | Valida a rota contínua com o Morador (BFS) / confirma telas | Menu, Instruções, Mapa, Jogando, Transição, Fim |
| `C` | Alterna **Modo Alto Contraste** em tempo real (bordas grossas + siglas `L`, `D`, `B`, `T`, `S`, `P`, `R`, `OK`, `FIM`) | **Todas as telas** |
| `F` | Alterna **Tamanho da Fonte** (`Normal` / `Grande`) em tempo real | **Todas as telas** |
| `M` | Silencia / ativa todo o áudio (efeitos + música) | **Todas as telas** |
| `N` | Silencia / ativa somente a trilha sonora de fundo | **Todas as telas** |
| `P` ou `ESC` | Pausa sem limite de tempo / retoma a partida | Jogando, Pausa |
| `R` | Reinicia a fase atual (ou campanha após vitória) | Jogando, Pausa, Fim |
| `S` | Abre o **Mapa Urbano** para selecionar fases desbloqueadas (`1`–`4`) | Menu |
| `I` | Abre a tela de **Instruções e Legenda Visual** | Menu |
| `A` | Abre a tela de **Créditos e Referências Técnicas** | Menu |

### Barreiras, Intervenções e Custos

| Elemento | Sigla (Alto Contraste) | Intervenção (`[E]`) | Custo | Dimensão de Acessibilidade |
| :--- | :---: | :--- | :---: | :--- |
| Lixeira na faixa livre | `L` | Deslocada para a faixa de serviço (`kill()`) | 0 rec | Física / Circulação |
| Degrau sem rebaixamento | `D` | Convertido em **Rampa acessível (`R`)** | 1 rec | Física / Mobilidade |
| Buraco no pavimento | `B` | Convertido em **Piso nivelado (`OK`)** | 1 rec | Física / Segurança |
| Trecho sem piso tátil | `T` | Convertido em **Piso tátil direcional (`OK`)** | 1 rec | Visual (baixa visão / cegueira) |
| Aviso apenas sonoro | `S` | Convertido em **Painel visual + sonoro (`OK`)** | 1 rec | Auditiva / Comunicacional |
| Poste fixo | `P` | Intransponível — exige planejamento de desvio | — | Planejamento de rota contínua |

### Avaliação Qualitativa de Autonomia (4 Fases Progressivas)

1. **Fase 1 — Calçada do Bairro** (90s, 3 rec): lixeiras + degrau (faixa livre contínua).
2. **Fase 2 — Entrada da Escola** (80s, 4 rec): lixeiras, 2 degraus, buraco e postes formando gargalos estreitos.
3. **Fase 3 — Praça Comunitária** (75s, 4 rec): barreiras físicas + avisos exclusivamente sonoros para Morador surdo.
4. **Fase 4 — Caminho ao Posto de Saúde** (70s, 5 rec): piso tátil, degraus, buracos e corredor superior armadilha fechado por postes fixos (orçamento contado).

Cada fase classifica o aprendizado observável em **Selos de Acessibilidade**: **Rota Exemplar (3/3)**, **Rota Eficiente (2/3)** ou **Rota Segura (1/3)**, salvos automaticamente em `progresso.json`.

---

## Estrutura de Arquivos

```text
projeto jogos/
├── .gitignore          # Ignora .venv/, __pycache__/, *.pyc, build/, dist/, *.spec e progresso.json
├── requirements.txt    # Dependência principal: pygame-ce (e comentário para pyinstaller)
├── config.py           # Fonte Única da Verdade: constantes, paletas, fontes, caminho_arquivo() e caminho_save()
├── gerar_assets.py     # Gerador procedural de 13 sprites PNG (48x48), 4 efeitos WAV e musica.wav
├── barreira.py         # Classe Barreira (Sprite): regras de negócio por tipo, resolver() e alto contraste
├── player.py           # Classe Jogador (Sprite): movimento 8 direções float+dt, spritecollide() e raio [E]
├── morador.py          # Classe Morador (Sprite): BFS em 4 direções, trajeto parcial/completo e update(dt)
├── fase.py             # Classe GerenciadorFases: 4 mapas 20x11, grupos de colisão e níveis de autonomia
├── particulas.py       # Classes Particula e SistemaParticulas: feedback visual suave sem flashes
├── save_manager.py     # Classe GerenciadorSave: persistência JSON com fallback seguro contra corrupção
├── hud.py              # Classe HUD: barra superior (96 px), feedback educativo, Mapa Urbano, Créditos e telas
├── main.py             # Classe JogoRotaAcessivel: máquina de estados (8 estados), grupo_desenho único e loop 60 FPS
├── README.md           # Documentação completa de uso, acessibilidade, empacotamento e arquitetura
└── data/               # 13 sprites PNG e 5 áudios WAV gerados por gerar_assets.py
```

---

## Equipe e Referências Técnicas

**Equipe (Engenharia de Software — 7º Período):**
- **Felipe-dev021** (`josefelipe2003.dev@gmail.com`) — Configuração centralizada, Game Loop, Persistência JSON e casos de borda
- **anacgsx** (`acarolinags04@gmail.com`) — Geração procedural de assets, entidade `Barreira`, acessibilidade visual/auditiva e trilha sonora
- **lucas-marins-dev** (`lucasommarins@gmail.com`) — Entidade `Jogador`, sistema de partículas ("juice") e acessibilidade avançada (`C`/`F`/`M`/`N`)
- **GuiMell0** (`guimellovr09@gmail.com`) — Algoritmo BFS (`Morador`), 4 fases progressivas e avaliação qualitativa de autonomia
- **Gabriel-dev10** (`gabrielssantana41@gmail.com`) — HUD completo, Mapa Urbano de seleção, tela de Créditos e documentação final

**Referências Técnicas:**
- **ABNT NBR 9050:2020** — Acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos
- **Lei nº 13.146/2015 (LBI)** — Lei Brasileira de Inclusão da Pessoa com Deficiência
- **W3C WCAG 2.1** — Diretrizes de Acessibilidade para Conteúdo Web
