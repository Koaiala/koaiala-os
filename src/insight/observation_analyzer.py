"""
KOAIALA
OBSERVATION ANALYZER

Analisa matematicamente as observações econômicas
fornecidas pelo Observation Repository.

Responsabilidades:

- Identificar a última observação.
- Identificar a observação anterior.
- Calcular variação absoluta.
- Calcular variação percentual.
- Classificar o movimento como:
    ALTA
    QUEDA
    ESTABILIDADE

Esta camada NÃO interpreta o significado econômico
do movimento.

Exemplo:

IPCA:
    0,16 -> 0,07

Resultado:

    movimento = QUEDA

A interpretação:

    QUEDA do IPCA = impacto econômico favorável

será realizada por outra camada.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from src.insight.observation_repository import (
    get_history,
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Diferença mínima para considerar que houve movimento.

# Valores menores ou iguais a este limite serão tratados
# como estabilidade.

STABILITY_THRESHOLD = Decimal("0.0001")


# ============================================================
# CLASSIFICAÇÃO DO MOVIMENTO
# ============================================================

def classificar_movimento(
    variacao: Decimal,
) -> str:
    """
    Classifica uma variação numérica.

    Retorna:

        ALTA
        QUEDA
        ESTABILIDADE
    """

    if variacao > STABILITY_THRESHOLD:
        return "ALTA"

    if variacao < -STABILITY_THRESHOLD:
        return "QUEDA"

    return "ESTABILIDADE"


# ============================================================
# ANÁLISE DE DUAS OBSERVAÇÕES
# ============================================================

def analisar_movimento(
    anterior: Dict,
    atual: Dict,
) -> Dict:
    """
    Compara duas observações consecutivas.

    Parâmetros:

        anterior:
            Observação mais antiga.

        atual:
            Observação mais recente.

    Retorno:

        Dicionário contendo:

            valor_anterior
            valor_atual
            variacao
            variacao_percentual
            movimento
    """

    valor_anterior = Decimal(
        anterior["value"]
    )

    valor_atual = Decimal(
        atual["value"]
    )

    variacao = (
        valor_atual
        - valor_anterior
    )

    if valor_anterior == 0:

        variacao_percentual = None

    else:

        variacao_percentual = (
            variacao
            / abs(valor_anterior)
        ) * Decimal("100")

    movimento = classificar_movimento(
        variacao
    )

    return {
        "data_anterior":
            anterior["observation_date"],

        "data_atual":
            atual["observation_date"],

        "valor_anterior":
            valor_anterior,

        "valor_atual":
            valor_atual,

        "variacao":
            variacao,

        "variacao_percentual":
            variacao_percentual,

        "movimento":
            movimento,
    }


# ============================================================
# ANÁLISE DO INDICADOR
# ============================================================

def analisar_indicador(
    indicator_code: str,
) -> Optional[Dict]:
    """
    Analisa o movimento mais recente de um indicador.

    Utiliza as duas observações mais recentes
    armazenadas no PostgreSQL.

    Retorna None quando não existem pelo menos
    duas observações.
    """

    historico = get_history(
        indicator_code,
        limit=2,
    )

    if len(historico) < 2:

        return None

    # O Repository retorna do mais recente
    # para o mais antigo.

    atual = historico[0]

    anterior = historico[1]

    resultado = analisar_movimento(
        anterior,
        atual,
    )

    resultado["indicador"] = indicator_code

    resultado["indicador_nome"] = (
        atual["indicator_name"]
    )

    resultado["unidade"] = (
        atual["unit"]
    )

    return resultado


# ============================================================
# ANÁLISE DE VÁRIOS INDICADORES
# ============================================================

def analisar_indicadores(
    indicator_codes: List[str],
) -> Dict[str, Optional[Dict]]:
    """
    Analisa o movimento mais recente de vários
    indicadores.
    """

    resultados = {}

    for codigo in indicator_codes:

        resultados[codigo] = (
            analisar_indicador(codigo)
        )

    return resultados


# ============================================================
# EXIBIÇÃO
# ============================================================

def exibir_resultado(
    resultado: Dict,
):
    """
    Exibe o resultado de uma análise.
    """

    print("=" * 60)

    print(
        "KOAIALA OBSERVATION ANALYZER"
    )

    print("=" * 60)

    print(
        f"Indicador: "
        f"{resultado['indicador_nome']}"
    )

    print(
        f"Código: "
        f"{resultado['indicador']}"
    )

    print(
        f"Data anterior: "
        f"{resultado['data_anterior']}"
    )

    print(
        f"Valor anterior: "
        f"{resultado['valor_anterior']}"
    )

    print(
        f"Data atual: "
        f"{resultado['data_atual']}"
    )

    print(
        f"Valor atual: "
        f"{resultado['valor_atual']}"
    )

    print(
        f"Variação: "
        f"{resultado['variacao']}"
    )

    if (
        resultado["variacao_percentual"]
        is not None
    ):

        print(
            f"Variação percentual: "
            f"{resultado['variacao_percentual']:.4f}%"
        )

    else:

        print(
            "Variação percentual: "
            "N/A"
        )

    print(
        f"Movimento: "
        f"{resultado['movimento']}"
    )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    indicadores = [
        "IPCA",
        "INPC",
        "IGP_M",
        "SELIC_META",
    ]

    print("=" * 60)
    print("KOAIALA OBSERVATION ANALYZER")
    print("=" * 60)

    for codigo in indicadores:

        resultado = analisar_indicador(
            codigo
        )

        print()

        if resultado is None:

            print(
                f"{codigo}: "
                "dados insuficientes"
            )

            continue

        print(
            f"{codigo} | "
            f"{resultado['data_anterior']} "
            f"-> "
            f"{resultado['data_atual']} | "
            f"{resultado['valor_anterior']} "
            f"-> "
            f"{resultado['valor_atual']} | "
            f"{resultado['movimento']}"
        )

    print()
    print("=" * 60)
    print(
        "ANALYZER FUNCIONANDO ✓"
    )
    print("=" * 60)


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main() 