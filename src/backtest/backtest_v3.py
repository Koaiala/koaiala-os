"""
KOAIALA BACKTEST 3.0

Métricas balanceadas para evitar que a SELIC, por possuir muitos
dias de estabilidade, domine a taxa agregada.

Calcula:
- acurácia bruta;
- acurácia sem estabilidade;
- acurácia balanceada por indicador;
- desempenho por direção;
- cobertura por direção.

Não altera o núcleo econômico do Koaiala.
"""

from typing import Dict

from src.backtest.backtest_v2 import avaliar_indicador, INDICADORES


def calcular_metricas(item: Dict) -> Dict:
    avaliacoes = item.get("avaliacoes", [])

    total = len(avaliacoes)
    acertos = sum(
        1 for x in avaliacoes if x["acerto"]
    )

    direcoes = ("ALTA", "QUEDA", "ESTABILIDADE")
    por_direcao = {}

    for direcao in direcoes:
        grupo = [
            x for x in avaliacoes
            if x["prevista"] == direcao
        ]

        n = len(grupo)
        a = sum(1 for x in grupo if x["acerto"])

        por_direcao[direcao] = {
            "total": n,
            "acertos": a,
            "erros": n - a,
            "taxa": round(a / n, 4) if n else None,
        }

    nao_estavel = [
        x for x in avaliacoes
        if x["prevista"] != "ESTABILIDADE"
    ]

    ne_total = len(nao_estavel)
    ne_acertos = sum(
        1 for x in nao_estavel if x["acerto"]
    )

    taxas_disponiveis = [
        v["taxa"]
        for v in por_direcao.values()
        if v["taxa"] is not None
    ]

    balanced = (
        sum(taxas_disponiveis) / len(taxas_disponiveis)
        if taxas_disponiveis
        else 0.0
    )

    return {
        "total": total,
        "acertos": acertos,
        "erros": total - acertos,
        "taxa_bruta": round(acertos / total, 4) if total else 0.0,
        "total_sem_estabilidade": ne_total,
        "acertos_sem_estabilidade": ne_acertos,
        "taxa_sem_estabilidade": (
            round(ne_acertos / ne_total, 4)
            if ne_total else None
        ),
        "taxa_balanceada": round(balanced, 4),
        "por_direcao": por_direcao,
    }


def executar() -> Dict:
    indicadores = {}
    taxas_brutas = []
    taxas_balanceadas = []

    for indicador in INDICADORES:
        resultado = avaliar_indicador(indicador)

        if resultado["status"] != "OK":
            indicadores[indicador] = {
                "status": resultado["status"]
            }
            continue

        metricas = calcular_metricas(resultado)

        indicadores[indicador] = {
            "status": "OK",
            **metricas,
        }

        taxas_brutas.append(metricas["taxa_bruta"])
        taxas_balanceadas.append(metricas["taxa_balanceada"])

    return {
        "status": "OK",
        "indicadores": indicadores,
        "media_acuracia_bruta": round(
            sum(taxas_brutas) / len(taxas_brutas), 4
        ) if taxas_brutas else 0.0,
        "media_acuracia_balanceada": round(
            sum(taxas_balanceadas) / len(taxas_balanceadas), 4
        ) if taxas_balanceadas else 0.0,
    }


def exibir(resultado: Dict) -> None:
    print("=" * 60)
    print("KOAIALA BACKTEST 3.0")
    print("=" * 60)
    print("MÉTRICAS BALANCEADAS")
    print()

    for indicador, item in resultado["indicadores"].items():
        if item["status"] != "OK":
            print(f"{indicador}: DADOS INSUFICIENTES")
            continue

        print(f"{indicador}")
        print(
            f"  Bruta:              {item['taxa_bruta']:.2%}"
        )

        if item["taxa_sem_estabilidade"] is not None:
            print(
                f"  Sem estabilidade:   "
                f"{item['taxa_sem_estabilidade']:.2%}"
            )

        print(
            f"  Balanceada:         "
            f"{item['taxa_balanceada']:.2%}"
        )

        for direcao, dados in item["por_direcao"].items():
            if dados["total"]:
                print(
                    f"  {direcao}: "
                    f"{dados['acertos']}/{dados['total']} "
                    f"| {dados['taxa']:.2%}"
                )

        print()

    print("-" * 60)
    print(
        f"Média bruta por indicador: "
        f"{resultado['media_acuracia_bruta']:.2%}"
    )
    print(
        f"Média balanceada:          "
        f"{resultado['media_acuracia_balanceada']:.2%}"
    )
    print("=" * 60)


if __name__ == "__main__":
    exibir(executar())
