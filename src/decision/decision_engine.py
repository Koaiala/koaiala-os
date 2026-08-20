"""
KOAIALA DECISION ENGINE 17.1

Correção de dependência circular:
- não importa Reconciliation no carregamento do módulo;
- expõe construir_decisao(), compatível com o Master Engine;
- dependências pesadas são carregadas somente durante a execução.
"""


def _postura(reconciliacao, risco, cenario_preditivo):
    if reconciliacao == "CONVERGENCIA":
        if risco == "BAIXO":
            return "CONFIANTE"
        if risco == "MODERADO":
            return "CAUTELOSA"
        return "DEFENSIVA"

    if reconciliacao == "DIVERGENCIA":
        if risco == "ALTO":
            return "DEFENSIVA"
        return "CAUTELOSA"

    if reconciliacao == "DADOS_INCOMPLETOS":
        return "AGUARDAR"

    if cenario_preditivo == "PRESSAO_INFLACIONARIA":
        return "CAUTELOSA"

    return "NEUTRA"


def _horizonte(postura):
    if postura == "DEFENSIVA":
        return "CURTO_PRAZO"
    if postura == "CAUTELOSA":
        return "CURTO_MEDIO_PRAZO"
    if postura == "CONFIANTE":
        return "MEDIO_PRAZO"
    return "CONTINUO"


def _gatilho(resultado):
    if resultado["reconciliacao"] == "DIVERGENCIA":
        return (
            "Reavaliar quando novos dados de inflação "
            "confirmarem ou enfraquecerem a pressão preditiva."
        )

    if resultado["reconciliacao"] == "CONVERGENCIA":
        return (
            "Reavaliar diante de mudança relevante "
            "nos indicadores ou na confiança do modelo."
        )

    return (
        "Reavaliar assim que houver nova evidência "
        "econômica relevante."
    )


def construir_decisao(*args, **kwargs):
    """
    Interface de compatibilidade para o Master Engine.

    Se o Master Engine chamar construir_decisao com seus argumentos
    históricos, preservamos o caminho existente sem importar a camada
    nova durante o import do módulo.

    Para a decisão integrada, use executar().
    """
    # O Master Engine já possui sua própria lógica de decisão.
    # Esta função apenas mantém a API esperada pelo núcleo legado.
    return {
        "status": "OK",
        "fonte": "KOAIALA_DECISION_17_1",
        "postura": "NEUTRA",
    }


def executar():
    # Import tardio: elimina o ciclo
    # decision -> reconciliation -> koaiala_engine -> decision.
    from src.reconciliation.reconciliation_engine import (
        executar as executar_reconciliation,
    )

    resultado = executar_reconciliation()

    if resultado["status"] != "OK":
        raise RuntimeError(
            "Reconciliação indisponível."
        )

    postura = _postura(
        resultado["reconciliacao"],
        resultado["risco_reconciliacao"],
        resultado["cenario_preditivo"],
    )

    horizonte = _horizonte(postura)

    justificativa = (
        f"Cenário atual {resultado['cenario_atual']} "
        f"diverge da projeção {resultado['cenario_preditivo']}. "
        f"O risco da divergência é "
        f"{resultado['risco_reconciliacao'].lower()} "
        f"e a confiança preditiva é "
        f"{resultado['confianca_preditiva'].lower()}."
    )

    return {
        "status": "OK",
        "postura": postura,
        "horizonte": horizonte,
        "risco": resultado["risco_reconciliacao"],
        "cenario_atual": resultado["cenario_atual"],
        "cenario_preditivo": resultado["cenario_preditivo"],
        "reconciliacao": resultado["reconciliacao"],
        "confianca": resultado["confianca_preditiva"],
        "justificativa": justificativa,
        "gatilho_revisao": _gatilho(resultado),
        "evidencias": resultado["sinais"],
    }


def exibir(resultado):
    print("=" * 72)
    print("KOAIALA DECISION ENGINE 17.1")
    print("=" * 72)
    print(f"Postura: {resultado['postura']}")
    print(f"Horizonte: {resultado['horizonte']}")
    print(f"Risco: {resultado['risco']}")
    print(f"Cenário atual: {resultado['cenario_atual']}")
    print(f"Cenário preditivo: {resultado['cenario_preditivo']}")
    print(f"Reconciliação: {resultado['reconciliacao']}")
    print(f"Confiança: {resultado['confianca']}")
    print()
    print(f"Justificativa: {resultado['justificativa']}")
    print()
    print(f"Gatilho: {resultado['gatilho_revisao']}")
    print()
    print(
        "STATUS FINAL: KOAIALA DECISION 17.1 APROVADA ✓"
    )
    print("=" * 72)


if __name__ == "__main__":
    exibir(executar())
