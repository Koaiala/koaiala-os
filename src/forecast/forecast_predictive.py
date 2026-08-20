"""
KOAIALA FORECAST 11.0

Converte o cenário preditivo em projeção estruturada de curto e médio
prazo. É uma camada complementar: não altera o Forecast Engine existente.
"""

from src.scenario.scenario_predictive import construir_cenario_preditivo


def _horizonte(direcao, forca, periodo):
    if direcao == "PRESSAO_INFLACIONARIA":
        if forca == "FORTE":
            return (
                "ALTA",
                "PRESSAO_INFLACIONARIA"
                if periodo == "CURTO"
                else "INFLACAO_PERSISTENTE",
            )
        return "ALTA", "PRESSAO_MODERADA"

    if direcao == "DESINFLACIONARIO":
        if forca == "FORTE":
            return (
                "QUEDA",
                "DESINFLACAO"
                if periodo == "CURTO"
                else "DESINFLACAO_PERSISTENTE",
            )
        return "QUEDA", "DESINFLACAO_MODERADA"

    return "ESTABILIDADE", "CENARIO_NEUTRO"


def construir_forecast():
    cenario = construir_cenario_preditivo()

    if cenario["status"] != "OK":
        return {
            "status": "ERRO",
            "mensagem": "Cenário preditivo indisponível.",
        }

    direcao_curta, leitura_curta = _horizonte(
        cenario["direcao"],
        cenario["forca"],
        "CURTO",
    )

    direcao_media, leitura_media = _horizonte(
        cenario["direcao"],
        cenario["forca"],
        "MEDIO",
    )

    sinais = cenario["sinais"]

    confiancas = {
        "ALTA": 3,
        "MODERADA": 2,
        "BAIXA": 1,
        "NENHUMA": 0,
    }

    ativos = [
        s for s in sinais.values()
        if s.get("status_sinal") == "SINAL_ATIVO"
    ]

    if ativos:
        score = sum(
            confiancas.get(
                s.get("confianca"),
                0,
            )
            for s in ativos
        ) / len(ativos)
    else:
        score = 0

    if score >= 2.5:
        confianca = "ALTA"
    elif score >= 1.5:
        confianca = "MODERADA"
    elif score > 0:
        confianca = "BAIXA"
    else:
        confianca = "NENHUMA"

    return {
        "status": "OK",
        "fonte": "KOAIALA_FORECAST_11",
        "cenario": cenario["direcao"],
        "forca_cenario": cenario["forca"],
        "curto_prazo": {
            "direcao": direcao_curta,
            "leitura": leitura_curta,
        },
        "medio_prazo": {
            "direcao": direcao_media,
            "leitura": leitura_media,
        },
        "confianca": confianca,
        "sinais_ativos": cenario["sinais_ativos"],
        "evidencias": sinais,
    }


def exibir(resultado):
    print("=" * 70)
    print("KOAIALA FORECAST 11.0")
    print("=" * 70)

    if resultado["status"] != "OK":
        print(resultado["mensagem"])
        return

    print(
        f"Cenário: {resultado['cenario']}"
    )
    print(
        f"Força: {resultado['forca_cenario']}"
    )
    print(
        f"Curto prazo: "
        f"{resultado['curto_prazo']['direcao']} | "
        f"{resultado['curto_prazo']['leitura']}"
    )
    print(
        f"Médio prazo: "
        f"{resultado['medio_prazo']['direcao']} | "
        f"{resultado['medio_prazo']['leitura']}"
    )
    print(
        f"Confiança: {resultado['confianca']}"
    )
    print(
        f"Sinais ativos: "
        f"{resultado['sinais_ativos']}"
    )
    print("=" * 70)


if __name__ == "__main__":
    exibir(construir_forecast())
