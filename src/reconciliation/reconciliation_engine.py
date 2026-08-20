"""
KOAIALA RECONCILIATION ENGINE 16.2

Correção adicional de import circular:
koaiala_engine só é carregado dentro de executar().
"""

from src.predictive.signal_engine import executar as executar_prediction
from src.forecast.forecast_predictive import construir_forecast


def _buscar_recursivo(obj, chaves):
    if isinstance(obj, dict):
        for chave in chaves:
            valor = obj.get(chave)
            if isinstance(valor, str) and valor.strip():
                return valor

        for valor in obj.values():
            encontrado = _buscar_recursivo(valor, chaves)
            if encontrado:
                return encontrado

    elif isinstance(obj, (list, tuple)):
        for valor in obj:
            encontrado = _buscar_recursivo(valor, chaves)
            if encontrado:
                return encontrado

    return None


def _normalizar_cenario(master):
    valor = _buscar_recursivo(
        master,
        (
            "classificacao",
            "classificação",
            "cenario",
            "cenário",
            "cenario_atual",
            "cenario_base",
            "classificacao_cenario",
        ),
    )

    if valor is None:
        return "DESCONHECIDO"

    return str(valor).strip().upper()


def _classificar(master, forecast):
    atual = _normalizar_cenario(master)
    futuro = str(forecast.get("cenario", "NEUTRO")).upper()

    if atual == futuro:
        return "CONVERGENCIA"

    if atual == "DESCONHECIDO":
        return "DADOS_INCOMPLETOS"

    inflacionario = (
        "INFLA" in futuro or "PRESSAO" in futuro
    )

    atual_favoravel = atual in {
        "OTIMISTA",
        "BASE",
        "ESTAVEL",
        "ESTÁVEL",
    }

    if inflacionario and atual_favoravel:
        return "DIVERGENCIA"

    return "TRANSICAO"


def _risco(reconciliacao, forecast):
    confianca = forecast.get("confianca", "NENHUMA")

    if reconciliacao == "CONVERGENCIA":
        return "BAIXO" if confianca == "ALTA" else "MODERADO"

    if reconciliacao == "DIVERGENCIA":
        return "ALTO" if confianca == "ALTA" else "MODERADO"

    if reconciliacao == "DADOS_INCOMPLETOS":
        return "ALTO"

    return "MODERADO"


def executar():
    # Import tardio: evita
    # decision -> reconciliation -> koaiala_engine -> decision.
    from src.core.koaiala_engine import executar_koaiala

    master = executar_koaiala()
    prediction = executar_prediction()
    forecast = construir_forecast()

    if prediction["status"] != "OK":
        raise RuntimeError("Prediction indisponível.")

    if forecast["status"] != "OK":
        raise RuntimeError("Forecast indisponível.")

    cenario_atual = _normalizar_cenario(master)
    reconciliacao = _classificar(master, forecast)
    risco = _risco(reconciliacao, forecast)

    return {
        "status": "OK",
        "cenario_atual": cenario_atual,
        "cenario_preditivo": forecast["cenario"],
        "reconciliacao": reconciliacao,
        "risco_reconciliacao": risco,
        "confianca_preditiva": forecast["confianca"],
        "sinais": prediction["sinais"],
    }


def exibir(resultado):
    print("=" * 72)
    print("KOAIALA RECONCILIATION ENGINE 16.2")
    print("=" * 72)
    print(f"Cenário atual: {resultado['cenario_atual']}")
    print(f"Cenário preditivo: {resultado['cenario_preditivo']}")
    print(f"Reconciliação: {resultado['reconciliacao']}")
    print(f"Risco da divergência: {resultado['risco_reconciliacao']}")
    print(f"Confiança preditiva: {resultado['confianca_preditiva']}")
    print()
    print("STATUS FINAL: KOAIALA RECONCILIATION 16.2 APROVADA ✓")
    print("=" * 72)
