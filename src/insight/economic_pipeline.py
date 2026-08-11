"""
KOAIALA - ECONOMIC PIPELINE

Orquestrador principal da análise econômica.

Fluxo:

Scenario Engine
↓
Sinais econômicos
↓
Economic Score
↓
Diagnóstico econômico consolidado
"""

from src.insight.scenario_engine import construir_cenario
from src.insight.economic_score import analisar_cenario_economico


def executar_pipeline():
    """
    Executa o fluxo integrado de análise econômica do Koaiala.
    """

    print("=" * 60)
    print("KOAIALA ECONOMIC PIPELINE")
    print("=" * 60)

    # ==========================================================
    # 1. CONSTRUÇÃO DO CENÁRIO
    # ==========================================================

    print("\n[1] CONSTRUINDO CENÁRIO ECONÔMICO...")

    cenario = construir_cenario()

    print("\nCHAVES DO CENÁRIO:")
    print(cenario.keys())

    if not cenario:
        print("ERRO: Scenario Engine não retornou resultado.")
        return None

    if cenario.get("status") == "ERRO":
        print("ERRO NO SCENARIO ENGINE:")
        print(cenario)
        return None

    print("Cenário construído com sucesso.")

    # ==========================================================
    # 2. EXTRAÇÃO DOS SINAIS
    # ==========================================================

    indicadores = cenario.get("indicadores", {})

    sinais = {}

    for codigo, dados in indicadores.items():
        try:
            interpretacao = dados["interpretacao"]
            direcao = interpretacao["direcao"]
            sinais[codigo] = direcao

        except (KeyError, TypeError):
            continue

    if not sinais:
        print("ERRO: nenhum sinal econômico foi encontrado.")
        print("Resultado recebido:")
        print(cenario)
        return None

    print("\n[2] SINAIS ECONÔMICOS")

    for indicador, sinal in sinais.items():
        print(f"{indicador}: {sinal}")

    # ==========================================================
    # 3. CÁLCULO DO SCORE ECONÔMICO
    # ==========================================================

    print("\n[3] CALCULANDO SCORE ECONÔMICO...")

    resultado_score = analisar_cenario_economico(sinais)

    if not resultado_score:
        print("ERRO: Economic Score não retornou resultado.")
        return None

    # ==========================================================
    # 4. RESULTADO CONSOLIDADO
    # ==========================================================

    print("\n" + "=" * 60)
    print("DIAGNÓSTICO ECONÔMICO KOAIALA")
    print("=" * 60)

    print(
        f"Score total: "
        f"{resultado_score.get('score_total')}"
    )

    print(
        f"Score normalizado: "
        f"{resultado_score.get('score_normalizado')}"
    )

    print(
        f"Confiança: "
        f"{resultado_score.get('confianca')}"
    )

    print("=" * 60)

    return {
        "cenario": cenario,
        "sinais": sinais,
        "score": resultado_score
    }


def main():
    """
    Ponto de entrada do Pipeline.
    """

    resultado = executar_pipeline()

    if resultado is None:
        print("\nPipeline encerrado com erro.")
        return

    print("\nPIPELINE EXECUTADO COM SUCESSO.")


if __name__ == "__main__":
    main()