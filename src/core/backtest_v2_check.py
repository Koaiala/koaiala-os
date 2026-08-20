"""
KOAIALA BACKTEST 2.0 CHECK
"""

from src.backtest.backtest_v2 import executar


def main():

    print("=" * 60)
    print("KOAIALA BACKTEST 2.0 CHECK")
    print("=" * 60)

    resultado = executar()

    if resultado["status"] != "OK":
        print(
            "STATUS FINAL: "
            "KOAIALA BACKTEST 2.0 REPROVADO ✗"
        )
        raise SystemExit(1)

    if resultado["total"] == 0:
        print(
            "STATUS FINAL: "
            "DADOS INSUFICIENTES"
        )
        raise SystemExit(2)

    print()

    for indicador, dados in resultado["indicadores"].items():

        if dados["status"] != "OK":
            print(
                f"{indicador}: "
                "DADOS INSUFICIENTES"
            )
            continue

        print(
            f"{indicador}: "
            f"{dados['acertos']}/"
            f"{dados['total']} "
            f"| taxa={dados['taxa']:.2%}"
        )

        for sinal, detalhe in dados["por_direcao"].items():

            if detalhe["total"] == 0:
                continue

            print(
                f"  {sinal}: "
                f"{detalhe['acertos']}/"
                f"{detalhe['total']} "
                f"| taxa={detalhe['taxa']:.2%}"
            )

    print("-" * 60)
    print(f"Avaliações: {resultado['total']}")
    print(f"Acertos: {resultado['acertos']}")
    print(f"Erros: {resultado['erros']}")
    print(
        f"Taxa agregada: "
        f"{resultado['taxa']:.2%}"
    )

    print()
    print(
        "STATUS FINAL: "
        "KOAIALA BACKTEST 2.0 APROVADO ✓"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
