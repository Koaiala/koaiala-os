"""
KOAIALA SCENARIO PREDICTIVE 10.0

Integra evidência preditiva ao cenário econômico sem substituir
o Scenario Engine existente.

Regra:
- sinais positivos de inflação: reforçam cenário de pressão;
- sinais negativos: reforçam desinflação;
- sinais neutros: não alteram o cenário.

A função retorna uma camada complementar para ser consumida pelo
Master Engine.
"""

from src.predictive.signal_engine import executar


def construir_cenario_preditivo():
    resultado = executar()

    if resultado["status"] != "OK":
        return {
            "status": "ERRO",
            "mensagem": "Camada preditiva indisponível.",
        }

    sinais = resultado["sinais"]

    positivos = 0
    negativos = 0
    ativos = 0

    for indicador in ("IPCA", "IGP_M", "INPC"):
        sinal = sinais.get(indicador)

        if not sinal or sinal.get("status") != "OK":
            continue

        if sinal["status_sinal"] != "SINAL_ATIVO":
            continue

        ativos += 1

        if sinal["sinal"] == "ALTA":
            positivos += 1

        elif sinal["sinal"] == "QUEDA":
            negativos += 1

    if positivos > negativos:
        direcao = "PRESSAO_INFLACIONARIA"
    elif negativos > positivos:
        direcao = "DESINFLACIONARIO"
    else:
        direcao = "NEUTRO"

    if ativos == 0:
        forca = "NENHUMA"
    elif abs(positivos - negativos) >= 2:
        forca = "FORTE"
    else:
        forca = "MODERADA"

    return {
        "status": "OK",
        "fonte": "KOAIALA_PREDICTIVE_EVIDENCE",
        "direcao": direcao,
        "forca": forca,
        "sinais_ativos": ativos,
        "sinais_positivos": positivos,
        "sinais_negativos": negativos,
        "sinais": sinais,
    }


def exibir(resultado):
    print("=" * 70)
    print("KOAIALA SCENARIO PREDICTIVE 10.0")
    print("=" * 70)

    if resultado["status"] != "OK":
        print(resultado["mensagem"])
        return

    print(
        f"Direção preditiva: "
        f"{resultado['direcao']}"
    )
    print(
        f"Força: {resultado['forca']}"
    )
    print(
        f"Sinais ativos: "
        f"{resultado['sinais_ativos']}"
    )
    print(
        f"Positivos: "
        f"{resultado['sinais_positivos']}"
    )
    print(
        f"Negativos: "
        f"{resultado['sinais_negativos']}"
    )

    print("=" * 70)


if __name__ == "__main__":
    exibir(
        construir_cenario_preditivo()
    )
