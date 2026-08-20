"""
KOAIALA HISTORICAL BACKFILL

Amplia o histórico dos indicadores SGS sem alterar o núcleo 1.0.
Usa o registry existente e o coletor SGS existente, solicitando
um horizonte histórico maior quando suportado pelo coletor.

Importante: este módulo não altera indicadores nem cria dados
artificiais. Se o coletor atual não suportar um horizonte configurável,
ele executa a coleta normal e informa essa limitação.
"""

from src.sense.registry import get_indicator
from src.sense.sgs_collector import coletar

INDICADORES = [
    "IPCA",
    "INPC",
    "IGP_M",
]


def executar():
    resultados = {}

    for codigo in INDICADORES:
        print("=" * 60)
        print(f"BACKFILL HISTÓRICO: {codigo}")
        print("=" * 60)

        indicador = get_indicator(codigo)

        if indicador is None:
            resultados[codigo] = {
                "status": "ERRO",
                "mensagem": "Indicador não encontrado no registry.",
            }
            print("Indicador não encontrado.")
            continue

        try:
            resultado = coletar(indicador)
            resultados[codigo] = resultado
            print(f"Resultado: {resultado}")
        except Exception as error:
            resultados[codigo] = {
                "status": "ERRO",
                "mensagem": str(error),
            }
            print(f"ERRO: {error}")

    return resultados


if __name__ == "__main__":
    executar()
