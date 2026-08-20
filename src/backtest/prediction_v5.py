"""
KOAIALA PREDICTION 5.0

Experimento de melhoria do preditor direcional.

Estratégias:
1. PERSISTENCIA: repete a última direção.
2. BASELINE: usa a direção mais frequente em todo o histórico disponível.
3. ROLLING: usa a direção mais frequente nas últimas N transições disponíveis.

Cada corte é estritamente temporal: somente dados anteriores ao
resultado são utilizados.
"""

from collections import Counter
from decimal import Decimal
from typing import Dict, List

from src.backtest.backtest_v2 import INDICADORES

# A importação acima não é usada porque buscar_registros é interna ao
# módulo original; a função abaixo acessa o banco diretamente.
from src.database.connection import get_connection


WINDOWS = [3, 5]


def buscar(indicador: str):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT observation_date, value
            FROM economic_observations
            WHERE indicator_code = %s
            ORDER BY observation_date ASC
            """,
            (indicador,),
        )
        return cursor.fetchall()
    finally:
        connection.close()


def direcao(a: Decimal, b: Decimal) -> str:
    if b > a:
        return "ALTA"
    if b < a:
        return "QUEDA"
    return "ESTABILIDADE"


def mais_frequente(valores: List[str]) -> str:
    if not valores:
        return "ESTABILIDADE"

    contagem = Counter(valores)

    # desempate determinístico
    ordem = ["ESTABILIDADE", "ALTA", "QUEDA"]

    return max(
        contagem,
        key=lambda x: (contagem[x], -ordem.index(x))
    )


def avaliar(indicador: str) -> Dict:
    registros = buscar(indicador)

    if len(registros) < 4:
        return {
            "status": "INSUFICIENTE",
            "indicador": indicador,
        }

    resultados = {
        "PERSISTENCIA": [],
        "BASELINE": [],
    }

    for janela in WINDOWS:
        resultados[f"ROLLING_{janela}"] = []

    transicoes_historicas = []

    # i é o ponto de corte; i+1 é o resultado futuro.
    for i in range(1, len(registros) - 1):
        _, v_anterior = registros[i - 1]
        data_corte, v_corte = registros[i]
        data_resultado, v_resultado = registros[i + 1]

        v_anterior = Decimal(str(v_anterior))
        v_corte = Decimal(str(v_corte))
        v_resultado = Decimal(str(v_resultado))

        ultima = direcao(v_anterior, v_corte)
        observado = direcao(v_corte, v_resultado)

        transicoes_anteriores = [
            direcao(
                Decimal(str(registros[j - 1][1])),
                Decimal(str(registros[j][1]))
            )
            for j in range(1, i + 1)
        ]

        resultados["PERSISTENCIA"].append({
            "acerto": ultima == observado,
            "observado": observado,
        })

        baseline = mais_frequente(transicoes_anteriores)
        resultados["BASELINE"].append({
            "acerto": baseline == observado,
            "observado": observado,
        })

        for janela in WINDOWS:
            janela_direcoes = transicoes_anteriores[-janela:]
            previsao = mais_frequente(janela_direcoes)

            resultados[f"ROLLING_{janela}"].append({
                "acerto": previsao == observado,
                "observado": observado,
            })

    metricas = {}

    for estrategia, itens in resultados.items():
        total = len(itens)
        acertos = sum(
            1 for item in itens if item["acerto"]
        )

        metricas[estrategia] = {
            "total": total,
            "acertos": acertos,
            "erros": total - acertos,
            "taxa": round(
                acertos / total, 4
            ) if total else 0.0,
        }

    return {
        "status": "OK",
        "indicador": indicador,
        "metricas": metricas,
    }


def executar() -> Dict:
    indicadores = {}

    for indicador in INDICADORES:
        indicadores[indicador] = avaliar(indicador)

    return {
        "status": "OK",
        "indicadores": indicadores,
    }


def exibir(resultado: Dict):
    print("=" * 70)
    print("KOAIALA PREDICTION 5.0")
    print("=" * 70)
    print("COMPARAÇÃO DE ESTRATÉGIAS DIRECIONAIS")
    print()

    acumulado = {}

    for indicador, item in resultado["indicadores"].items():
        print(indicador)

        if item["status"] != "OK":
            print("  DADOS INSUFICIENTES")
            continue

        for estrategia, dados in item["metricas"].items():
            acumulado.setdefault(estrategia, [])
            acumulado[estrategia].append(
                dados["taxa"]
            )

            print(
                f"  {estrategia:<14} "
                f"{dados['acertos']:>3}/"
                f"{dados['total']:<3} "
                f"| {dados['taxa']:.2%}"
            )

        print()

    print("-" * 70)
    print("MÉDIA ENTRE INDICADORES")

    medias = {}

    for estrategia, taxas in acumulado.items():
        medias[estrategia] = (
            sum(taxas) / len(taxas)
        )

        print(
            f"{estrategia:<14} "
            f"{medias[estrategia]:.2%}"
        )

    melhor = max(
        medias,
        key=medias.get
    )

    print()
    print(
        f"MELHOR ESTRATÉGIA: "
        f"{melhor} "
        f"({medias[melhor]:.2%})"
    )

    print("=" * 70)


if __name__ == "__main__":
    exibir(executar())
