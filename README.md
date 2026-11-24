# Rota Acessível — Maricá/RJ

**Serious Game 2.5D (projeção 3/4)** desenvolvido em Python com **pygame-ce** para a disciplina de **Desenvolvimento de Jogos Digitais** (7º período de Engenharia de Software — Univassouras Campus Maricá) — **Tema 07: Acessibilidade e Inclusão**.

> *"Divertir é o meio. Resolver é o fim."*

---

## Problema Real Resolvido

Moradores e planejadores urbanos sem deficiência frequentemente não percebem barreiras cotidianas que impedem pessoas com deficiência física, visual ou auditiva de circular e se informar com autonomia: lixeiras bloqueando a faixa livre, degraus sem rebaixamento, buracos no pavimento, trechos críticos sem piso tátil direcional e avisos exclusivamente sonoros.

Em **Rota Acessível**, ambientado em 4 locais reais de **Maricá/RJ**, o aprendizado acontece diretamente pela **mecânica de jogo** (sem formato de quiz e sem gamificação superficial): o jogador controla **Alex** (agente de acessibilidade), conversa com o morador no popup de apresentação antes da fase começar, administra um orçamento limitado de obras e valida a continuidade da faixa livre acionando o **Morador** da fase (**Clara**, **Lucas**, **Sofia** ou **Mateus**), que percorre o trajeto via **Busca em Largura (BFS) em 4 direções**. A cada bloqueio real, o morador explica o impacto concreto daquela barreira segundo a **ABNT NBR 9050:2020** e a **Lei Brasileira de Inclusão (LBI)**.

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
5. Gere todos os sprites 2.5D PNG (`48x48` e `48x64` suavizados em 2x) e áudios WAV na pasta `data/`:
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
5. Gere os assets na pasta `data/`:
   ```bash
   python3 gerar_assets.py
   ```
6. Execute o jogo:
   ```bash
   python3 main.py
   ```

---

## Empacotamento Opcional com PyInstaller

O projeto resolve caminhos de leitura (`caminho_arquivo()` com suporte a `sys._MEIPASS`) e escrita (`caminho_save()` gravando `progresso.json` ao lado do executável).

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
     pyinstaller --onefile --windowed --name RotaAcessivel --add-data "data;data" main.py
     ```
   - **Linux / macOS:**
     ```bash
     pyinstaller --onefile --windowed --name RotaAcessivel --add-data "data:data" main.py
     ```
4. O executável estará disponível na pasta `dist/`.

---

## Controles e Recursos de Acessibilidade

| Entrada | Ação | Onde Funciona |
| :--- | :--- | :--- |
| `W`, `A`, `S`, `D` ou `Setas` | Move Alex em 8 direções com deslizamento suave em quinas / navega no Mapa | Jogando, Mapa |
| `SHIFT` | Corrida rápida (Sprint) de Alex | Jogando |
| `Clique do Mouse` | Navega em menus/mapa, clica em **Ajudar**, guia Alex na calçada, aplica obra próxima ou aciona **Testar Rota** | Todas as telas |
| `E` | Aplica intervenção na barreira destacada `[E]` (raio de 84 px) | Jogando |
| `TAB` | Alterna **Modo Raio-X de Acessibilidade** (destaca todas as barreiras pendentes) | Jogando |
| `ESPAÇO` ou `ENTER` | Valida a rota contínua com o Morador (BFS) / confirma popup **Ajudar** e telas | Todas as telas |
| `C` | Alterna **Modo Alto Contraste** em tempo real (bordas grossas + siglas `L`, `D`, `B`, `T`, `S`, `P`, `R`, `OK`, `FIM`) | **Todas as telas** |
| `F` | Alterna **Tamanho da Fonte** (`Normal` / `Grande`) em tempo real | **Todas as telas** |
| `M` | Silencia / ativa todo o áudio (efeitos + música) | **Todas as telas** |
| `N` | Silencia / ativa somente a trilha sonora de fundo | **Todas as telas** |
| `P` ou `ESC` | Pausa sem limite de tempo / retoma a partida | Jogando, Pausa |
| `R` | Reinicia a fase atual (reabre o popup antes de contar o tempo) | Jogando, Pausa, Fim |
| `S` | Abre o **Mapa de Maricá/RJ** para selecionar fases desbloqueadas (`1`–`4`) | Menu |
| `I` | Abre a tela de **Instruções e Legenda Visual** | Menu |
| `A` | Abre a tela de **Créditos e Referências Técnicas** | Menu |

### Fases Progressivas em Maricá/RJ e Avaliação de Autonomia

1. **Fase 1 — Orla de Araçatiba** (*Clara, cadeirante* — 90s, 3 obras): lixeiras + degrau até o ponto do **Vermelhinho (Tarifa Zero)**.
2. **Fase 2 — Escola no Centro de Maricá** (*Lucas, estudante cadeirante* — 85s, 4 obras): lixeiras, 2 degraus, buraco e canteiros em gargalos.
3. **Fase 3 — Praça Orlando de Barros Pimentel** (*Sofia, moradora surda* — 80s, 4 obras): lixeiras + 3 avisos exclusivamente sonoros convertidos em painéis visuais.
4. **Fase 4 — Posto de Saúde — Itaipuaçu** (*Mateus, baixa visão com bengala branca* — 75s, 5 obras): lixeira, 3 trechos sem piso tátil, 2 buracos e corredor superior armadilha fechado por canteiros fixos (orçamento contado).

Cada fase classifica o aprendizado observável em **Selos de Acessibilidade**: **Rota Exemplar (3/3)**, **Rota Eficiente (2/3)** ou **Rota Segura (1/3)**, salvos automaticamente em `progresso.json`.

---

## Estrutura de Arquivos

```text
projeto jogos/
├── .gitignore          # Ignora .venv/, __pycache__/, *.pyc, build/, dist/, *.spec e progresso.json
├── requirements.txt    # Dependência principal: pygame-ce (e comentário para pyinstaller)
├── config.py           # Fonte Única da Verdade: constantes, paletas, fontes, caminho_arquivo() e caminho_save()
├── gerar_assets.py     # Gerador procedural 2.5D (supersampling 2x): 15 sprites PNG e 5 áudios WAV
├── barreira.py         # Classe Barreira (Sprite): regras de negócio por tipo, resolver() e alto contraste
├── player.py           # Classe Jogador (Sprite): hitbox nos pés, wall-snap, corner-nudging, Sprint e clique
├── morador.py          # Classe Morador (Sprite): 3 perfis reais, BFS em 4 direções e deslize suave
├── fase.py             # Classe GerenciadorFases: 4 mapas de Maricá/RJ (20x11), grupos e níveis de autonomia
├── particulas.py       # Classes Particula e SistemaParticulas: feedback visual leve e sem flashes
├── save_manager.py     # Classe GerenciadorSave: persistência JSON com fallback seguro contra corrupção
├── hud.py              # Classe HUD: cenários 2.5D em cache, popup Briefing (Ajudar), Mapa, Créditos e telas
├── main.py             # Classe JogoRotaAcessivel: 9 estados, VSync + tick_busy_loop, Y-Sort 2.5D e loop 60 FPS
├── README.md           # Documentação completa de uso, acessibilidade, empacotamento e arquitetura
└── data/               # 15 sprites PNG (48x48 e 48x64) e 5 áudios WAV gerados por gerar_assets.py
```

---

## Equipe e Referências Técnicas

**Equipe (Engenharia de Software — 7º Período):**
- **Felipe-dev021** (`josefelipe2003.dev@gmail.com`) — Configuração centralizada, Game Loop, VSync/Y-Sort, Persistência JSON e casos de borda
- **anacgsx** (`acarolinags04@gmail.com`) — Geração procedural 2.5D de assets, entidade `Barreira`, acessibilidade visual/auditiva e trilha sonora
- **lucas-marins-dev** (`lucasommarins@gmail.com`) — Entidade `Jogador`, movimentação fluida, sistema de partículas e acessibilidade (`C`/`F`/`M`/`N`)
- **GuiMell0** (`guimellovr09@gmail.com`) — Algoritmo BFS (`Morador`), 4 fases de Maricá/RJ e avaliação qualitativa de autonomia
- **Gabriel-dev10** (`gabrielssantana41@gmail.com`) — HUD 2.5D em cache, popup Briefing (`Ajudar`), Mapa de Maricá/RJ, Créditos e documentação

**Referências Técnicas:**
- **ABNT NBR 9050:2020** — Acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos
- **Lei nº 13.146/2015 (LBI)** — Lei Brasileira de Inclusão da Pessoa com Deficiência
- **W3C WCAG 2.1** — Diretrizes de Acessibilidade para Conteúdo Web
