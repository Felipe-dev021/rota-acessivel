"""Gerenciamento de persistência em JSON (progresso e preferências de acessibilidade).

Implementa a classe GerenciadorSave utilizando caminho_save('progresso.json')
com tratamento robusto de exceções para arquivos inexistentes ou corrompidos,
compatível com execução direta e empacotamento PyInstaller.
"""

import json
import os
from typing import Any, Dict

from config import ARQUIVO_SAVE_PROGRESSO, caminho_save


class GerenciadorSave:
    """Salva e carrega progresso de fases e preferências de acessibilidade em JSON."""

    def __init__(self, nome_arquivo: str = ARQUIVO_SAVE_PROGRESSO) -> None:
        """Inicializa o gerenciador carregando o arquivo JSON ou criando o padrão.

        Args:
            nome_arquivo: Nome do arquivo gravável (padrão: 'progresso.json').
        """
        self.caminho: str = caminho_save(nome_arquivo)
        self.dados: Dict[str, Any] = self._criar_estrutura_padrao()
        self.carregar()

    def _criar_estrutura_padrao(self) -> Dict[str, Any]:
        """Retorna um dicionário limpo com valores iniciais seguros.

        Returns:
            Estrutura padrão contendo fases_desbloqueadas, fases e preferencias.
        """
        return {
            "fases_desbloqueadas": 1,
            "fases": {},
            "preferencias": {
                "alto_contraste": False,
                "fonte_grande": False,
                "som_ativo": True,
                "musica_ativa": True,
            },
        }

    def _validar_estrutura(self, bruto: Any) -> Dict[str, Any]:
        """Saneia dados carregados de JSON garantindo todos os campos esperados.

        Args:
            bruto: Objeto retornado por json.load().

        Returns:
            Dicionário validado e seguro para uso imediato pelo jogo.
        """
        padrao = self._criar_estrutura_padrao()
        if not isinstance(bruto, dict):
            return padrao

        desbloqueadas = bruto.get("fases_desbloqueadas", 1)
        if isinstance(desbloqueadas, int) and 1 <= desbloqueadas <= 4:
            padrao["fases_desbloqueadas"] = desbloqueadas

        fases_brutas = bruto.get("fases", {})
        if isinstance(fases_brutas, dict):
            for chave, info in fases_brutas.items():
                if not isinstance(info, dict):
                    continue
                padrao["fases"][str(chave)] = {
                    "concluida": bool(info.get("concluida", False)),
                    "melhor_nivel": str(info.get("melhor_nivel", "")),
                    "melhor_selos": int(info.get("melhor_selos", 0)),
                    "menor_erros": int(info.get("menor_erros", 0)),
                }

        prefs_brutas = bruto.get("preferencias", {})
        if isinstance(prefs_brutas, dict):
            for chave in ("alto_contraste", "fonte_grande", "som_ativo", "musica_ativa"):
                if chave in prefs_brutas:
                    padrao["preferencias"][chave] = bool(prefs_brutas[chave])

        return padrao

    def carregar(self) -> Dict[str, Any]:
        """Carrega o progresso do disco com fallback seguro em caso de erro.

        Se o arquivo não existir ou estiver corrompido, restaura os valores
        padrão sem interromper a execução do jogo.

        Returns:
            Dicionário com o progresso e preferências atuais.
        """
        if not os.path.isfile(self.caminho):
            self.dados = self._criar_estrutura_padrao()
            return self.dados

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                bruto = json.load(arquivo)
            self.dados = self._validar_estrutura(bruto)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.dados = self._criar_estrutura_padrao()
            self.salvar()

        return self.dados

    def salvar(self) -> bool:
        """Persiste o estado atual no arquivo JSON de forma segura.

        Returns:
            True se gravou com sucesso; False se ocorreu erro de permissão/disco.
        """
        try:
            pasta = os.path.dirname(self.caminho)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as arquivo:
                json.dump(self.dados, arquivo, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False

    def atualizar_preferencias(
        self,
        alto_contraste: bool,
        fonte_grande: bool,
        som_ativo: bool,
        musica_ativa: bool,
    ) -> None:
        """Atualiza e persiste as preferências de acessibilidade do usuário.

        Args:
            alto_contraste: Estado do modo de alto contraste ([C]).
            fonte_grande: Estado da escala de fonte grande ([F]).
            som_ativo: Estado geral do áudio ([M]).
            musica_ativa: Estado da trilha sonora ([N]).
        """
        self.dados["preferencias"] = {
            "alto_contraste": bool(alto_contraste),
            "fonte_grande": bool(fonte_grande),
            "som_ativo": bool(som_ativo),
            "musica_ativa": bool(musica_ativa),
        }
        self.salvar()

    def registrar_conclusao_fase(
        self,
        numero_fase: int,
        total_fases: int,
        nivel_autonomia: str,
        selos: int,
        erros_rota: int,
    ) -> None:
        """Atualiza desbloqueio, melhor selo e menor número de erros da fase.

        Args:
            numero_fase: Número da fase concluída (1 a total_fases).
            total_fases: Quantidade total de fases da campanha.
            nivel_autonomia: Rótulo qualitativo conquistado ('Rota Exemplar', etc.).
            selos: Quantidade de selos de acessibilidade (1 a 3).
            erros_rota: Número de bloqueios encontrados na tentativa vitoriosa.
        """
        desbloqueadas = int(self.dados.get("fases_desbloqueadas", 1))
        proxima = min(total_fases, numero_fase + 1)
        if proxima > desbloqueadas:
            self.dados["fases_desbloqueadas"] = proxima

        chave = str(numero_fase)
        fases = self.dados.setdefault("fases", {})
        anterior = fases.get(chave)

        if anterior is None or not anterior.get("concluida", False):
            fases[chave] = {
                "concluida": True,
                "melhor_nivel": nivel_autonomia,
                "melhor_selos": selos,
                "menor_erros": erros_rota,
            }
        else:
            if selos >= int(anterior.get("melhor_selos", 0)):
                anterior["melhor_selos"] = selos
                anterior["melhor_nivel"] = nivel_autonomia
            anterior["menor_erros"] = min(
                int(anterior.get("menor_erros", erros_rota)), erros_rota
            )
            anterior["concluida"] = True

        self.salvar()

    def obter_preferencias(self) -> Dict[str, bool]:
        """Retorna uma cópia do dicionário de preferências de acessibilidade."""
        prefs = self.dados.get("preferencias", {})
        return {
            "alto_contraste": bool(prefs.get("alto_contraste", False)),
            "fonte_grande": bool(prefs.get("fonte_grande", False)),
            "som_ativo": bool(prefs.get("som_ativo", True)),
            "musica_ativa": bool(prefs.get("musica_ativa", True)),
        }

    def fases_desbloqueadas(self) -> int:
        """Retorna a quantidade de fases desbloqueadas (1 a 4)."""
        return int(self.dados.get("fases_desbloqueadas", 1))

    def obter_registro_fase(self, numero_fase: int) -> Dict[str, Any]:
        """Retorna o histórico salvo de uma fase específica ou valores zerados.

        Args:
            numero_fase: Número da fase (1 a 4).

        Returns:
            Dicionário com concluida, melhor_nivel, melhor_selos e menor_erros.
        """
        fases = self.dados.get("fases", {})
        info = fases.get(str(numero_fase))
        if isinstance(info, dict):
            return dict(info)
        return {
            "concluida": False,
            "melhor_nivel": "",
            "melhor_selos": 0,
            "menor_erros": 0,
        }
