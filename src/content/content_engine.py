"""
KOAIALA CONTENT ENGINE

Transforma as análises econômicas do Koaiala em conteúdo
editorial pronto para utilização em vídeos, Shorts e posts.

Fluxo:

    Dados econômicos
          ↓
    Analysis Engine
          ↓
    Economic Score
          ↓
    Seleção do Insight
          ↓
    Título
          ↓
    Gancho
          ↓
    Roteiro
          ↓
    Short / Reel
          ↓
    CTA
"""

from decimal import Decimal
from typing import Dict, List, Any

from src.insight.analysis_engine import analisar_indicador
from src.insight.economic_score import analisar_cenario_economico


# ============================================================
# CONFIGURAÇÃO
# ============================================================

INDICADORES_PRIORITARIOS = [
    "SELIC_META",
    "IPCA",
    "INPC",
    "IGP_M",
    "PIB",
    "DESEMPREGO",
    "CAMBIO",
]


INDICADOR_NOMES = {
    "SELIC_META": "juros",
    "IPCA": "inflação",
    "INPC": "inflação das famílias",
    "IGP_M": "preços",
    "PIB": "atividade econômica",
    "DESEMPREGO": "mercado de trabalho",
    "CAMBIO": "câmbio",
}


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_numero(valor: Any) -> str:
    """
    Formata um número para apresentação editorial.
    """

    if valor is None:
        return "n/d"

    try:
        numero = Decimal(str(valor))

        return (
            f"{numero:.2f}"
            .replace(".", ",")
        )

    except Exception:
        return str(valor)


# ============================================================
# CONVERSÃO DE TENDÊNCIA
# ============================================================

def obter_sinal(resultado: Dict) -> str:
    """
    Converte a tendência produzida pelo Analysis Engine
    para o formato utilizado pelo Economic Score.
    """

    tendencia = (
        resultado.get("tendencia_atual")
        or resultado.get("tendencia")
    )

    if tendencia == "ALTA":
        return "ALTA"

    if tendencia == "QUEDA":
        return "QUEDA"

    return "ESTABILIDADE"


# ============================================================
# COLETA DAS ANÁLISES
# ============================================================

def coletar_analises() -> Dict[str, Dict]:
    """
    Executa o Analysis Engine para os indicadores disponíveis.

    Indicadores que ainda não possuem dados são ignorados.
    """

    analises = {}

    for indicador in INDICADORES_PRIORITARIOS:

        try:

            resultado = analisar_indicador(
                indicador
            )

            if resultado.get("status") == "OK":

                analises[indicador] = resultado

        except Exception:

            continue

    return analises


# ============================================================
# SCORE ECONÔMICO
# ============================================================

def construir_score(
    analises: Dict[str, Dict]
) -> Dict:
    """
    Calcula o cenário econômico utilizando
    as tendências disponíveis.
    """

    sinais = {}

    for indicador, resultado in analises.items():

        sinais[indicador] = obter_sinal(
            resultado
        )

    if not sinais:

        return {
            "status": "ERRO",
            "mensagem":
                "Nenhum indicador disponível."
        }

    resultado = analisar_cenario_economico(
        sinais
    )

    resultado["sinais"] = sinais

    return resultado


# ============================================================
# SELEÇÃO DO INSIGHT
# ============================================================

def selecionar_tema(
    analises: Dict[str, Dict]
) -> Dict:
    """
    Seleciona automaticamente o indicador que apresentou
    a maior mudança absoluta na última observação.

    Isso cria um critério simples e transparente para
    escolher o assunto principal do conteúdo.
    """

    candidatos: List[Dict] = []

    for indicador, resultado in analises.items():

        variacao = resultado.get(
            "variacao_absoluta"
        )

        if variacao is None:
            continue

        try:

            magnitude = abs(
                float(variacao)
            )

        except Exception:

            magnitude = 0.0

        candidatos.append(
            {
                "indicador": indicador,
                "resultado": resultado,
                "magnitude": magnitude,
            }
        )

    if not candidatos:

        return {
            "indicador": None,
            "resultado": None,
            "tema":
                "Cenário econômico brasileiro",
        }

    candidatos.sort(
        key=lambda item: item["magnitude"],
        reverse=True,
    )

    principal = candidatos[0]

    indicador = principal["indicador"]

    resultado = principal["resultado"]

    tendencia = (
        resultado.get("tendencia_atual")
        or resultado.get("tendencia")
    )

    nome = INDICADOR_NOMES.get(
        indicador,
        indicador
    )

    if tendencia == "QUEDA":

        tema = (
            f"Queda recente em {nome}"
        )

    elif tendencia == "ALTA":

        tema = (
            f"Alta recente em {nome}"
        )

    else:

        tema = (
            f"Estabilidade em {nome}"
        )

    return {
        "indicador": indicador,
        "resultado": resultado,
        "tema": tema,
    }


# ============================================================
# TÍTULO
# ============================================================

def gerar_titulo(
    tema: Dict,
    score: Dict
) -> str:
    """
    Gera um título editorial baseado no indicador principal.
    """

    indicador = tema.get(
        "indicador"
    )

    titulos = {

        "IPCA":
            "IPCA cai: a inflação brasileira está finalmente desacelerando?",

        "INPC":
            "INPC desacelera: o que isso revela sobre a inflação?",

        "IGP_M":
            "IGP-M despenca: o que está acontecendo com os preços?",

        "SELIC_META":
            "Selic em 14%: o ciclo de queda dos juros chegou ao fim?",

        "PIB":
            "PIB muda de direção: a economia brasileira está acelerando?",

        "DESEMPREGO":
            "Desemprego muda: o que isso significa para a economia?",

        "CAMBIO":
            "Câmbio muda de direção: o que pode acontecer com a economia?",
    }

    if indicador in titulos:

        return titulos[indicador]

    classificacao = score.get(
        "classificacao",
        "NEUTRO"
    )

    return (
        "Economia brasileira: "
        f"o sinal que o Koaiala detectou "
        f"({classificacao})"
    )


# ============================================================
# GANCHO
# ============================================================

def gerar_gancho(
    tema: Dict,
    score: Dict
) -> str:
    """
    Cria o gancho inicial do vídeo.
    """

    indicador = tema.get(
        "indicador"
    )

    resultado = tema.get(
        "resultado"
    ) or {}

    valor_atual = formatar_numero(
        resultado.get("valor_atual")
    )

    tendencia = (
        resultado.get("tendencia_atual")
        or resultado.get("tendencia")
    )

    if indicador == "IPCA":

        return (
            f"O IPCA caiu para {valor_atual}% "
            "no último dado. Mas será que isso "
            "já é o começo de uma mudança importante "
            "na trajetória da inflação brasileira?"
        )

    if indicador == "INPC":

        return (
            f"O INPC chegou a {valor_atual}% "
            "no último dado. O movimento merece "
            "atenção porque mostra uma mudança "
            "recente na inflação das famílias."
        )

    if indicador == "IGP_M":

        return (
            f"O IGP-M chegou a {valor_atual}%. "
            "O movimento foi forte e levanta uma "
            "pergunta importante: o que está "
            "acontecendo com os preços?"
        )

    if indicador == "SELIC_META":

        return (
            f"A Selic está em {valor_atual}% "
            f"e o Koaiala detectou "
            f"{str(tendencia).lower()} "
            "na leitura mais recente. "
            "O que isso significa para os próximos meses?"
        )

    return (
        f"O Koaiala detectou uma mudança em "
        f"{indicador}. A pergunta agora é: "
        "esse movimento será temporário "
        "ou persistente?"
    )


# ============================================================
# ROTEIRO
# ============================================================

def gerar_roteiro(
    tema: Dict,
    score: Dict
) -> str:
    """
    Gera um roteiro curto para vídeo.
    """

    indicador = tema.get(
        "indicador"
    )

    resultado = tema.get(
        "resultado"
    ) or {}

    valor_atual = formatar_numero(
        resultado.get("valor_atual")
    )

    valor_anterior = formatar_numero(
        resultado.get("valor_anterior")
    )

    variacao = formatar_numero(
        resultado.get("variacao_absoluta")
    )

    classificacao = score.get(
        "classificacao",
        "NEUTRO"
    )

    confianca = score.get(
        "confianca",
        "INSUFICIENTE"
    )

    linhas = [

        "GANCHO",

        gerar_gancho(
            tema,
            score
        ),

        "",

        "DADO",

        (
            f"O {indicador} passou de "
            f"{valor_anterior} para "
            f"{valor_atual}. "
            f"A variação foi de "
            f"{variacao}."
        ),

        "",

        "LEITURA",

        (
            "O Koaiala não trata uma única "
            "observação como prova de uma "
            "mudança estrutural. "
            "O movimento precisa ser analisado "
            "junto com a tendência recente "
            "e com os demais indicadores."
        ),

        "",

        "CENÁRIO",

        (
            f"A leitura agregada disponível "
            f"neste momento é "
            f"{classificacao}, "
            f"com confiança {confianca}."
        ),

        "",

        "CONCLUSÃO",

        (
            "O próximo dado será importante "
            "para confirmar ou enfraquecer "
            "essa leitura. "
            "É justamente essa persistência "
            "que o Koaiala acompanha."
        ),

        "",

        "CTA",

        (
            "Siga o canal para acompanhar "
            "os sinais da economia brasileira "
            "antes que eles virem apenas manchetes."
        ),
    ]

    return "\n".join(
        linhas
    )


# ============================================================
# SHORT / REEL
# ============================================================

def gerar_short(
    tema: Dict,
    score: Dict
) -> str:
    """
    Gera texto para Shorts, Reels e TikTok.
    """

    indicador = tema.get(
        "indicador"
    )

    resultado = tema.get(
        "resultado"
    ) or {}

    atual = formatar_numero(
        resultado.get("valor_atual")
    )

    anterior = formatar_numero(
        resultado.get("valor_anterior")
    )

    tendencia = (
        resultado.get("tendencia_atual")
        or resultado.get("tendencia")
    )

    return (

        f"{indicador}: "
        f"{anterior} para {atual}. "

        f"O movimento recente é de "
        f"{str(tendencia).lower()}. "

        "Mas atenção: um único dado "
        "não confirma uma tendência estrutural. "

        "O Koaiala cruza esse movimento "
        "com os demais indicadores para "
        "identificar o cenário econômico. "

        "Siga o canal para acompanhar "
        "a próxima leitura."
    )


# ============================================================
# INSIGHT COMPLETO
# ============================================================

def gerar_insight(
    analises: Dict[str, Dict],
    score: Dict,
    tema: Dict
) -> Dict:
    """
    Monta o pacote completo de conteúdo.
    """

    return {

        "status": "OK",

        "tema":
            tema["tema"],

        "indicador_principal":
            tema["indicador"],

        "classificacao_economica":
            score.get(
                "classificacao"
            ),

        "score":
            score.get(
                "score_normalizado"
            ),

        "confianca":
            score.get(
                "confianca"
            ),

        "titulo":
            gerar_titulo(
                tema,
                score
            ),

        "gancho":
            gerar_gancho(
                tema,
                score
            ),

        "roteiro":
            gerar_roteiro(
                tema,
                score
            ),

        "short":
            gerar_short(
                tema,
                score
            ),

        "indicadores_analisados":
            list(
                analises.keys()
            ),

        "score_detalhado":
            score,
    }


# ============================================================
# EXECUÇÃO DO CONTENT ENGINE
# ============================================================

def gerar_conteudo() -> Dict:
    """
    Executa todo o fluxo do Content Engine.
    """

    analises = coletar_analises()

    if not analises:

        return {

            "status": "ERRO",

            "mensagem":
                "Nenhum indicador econômico disponível.",
        }

    score = construir_score(
        analises
    )

    if score.get("status") == "ERRO":

        return score

    tema = selecionar_tema(
        analises
    )

    return gerar_insight(
        analises,
        score,
        tema
    )


# ============================================================
# EXIBIÇÃO
# ============================================================

def exibir_conteudo(
    resultado: Dict
) -> None:
    """
    Exibe o conteúdo gerado no terminal.
    """

    print("=" * 60)

    print(
        "KOAIALA CONTENT ENGINE"
    )

    print("=" * 60)

    if resultado.get("status") != "OK":

        print(
            f"STATUS: "
            f"{resultado.get('status')}"
        )

        print(
            f"ERRO: "
            f"{resultado.get('mensagem')}"
        )

        print("=" * 60)

        return

    print(
        f"TEMA: "
        f"{resultado['tema']}"
    )

    print(
        f"INDICADOR PRINCIPAL: "
        f"{resultado['indicador_principal']}"
    )

    print(
        f"SCORE: "
        f"{resultado['score']}"
    )

    print(
        f"CENÁRIO: "
        f"{resultado['classificacao_economica']}"
    )

    print(
        f"CONFIANÇA: "
        f"{resultado['confianca']}"
    )

    print()

    print("TÍTULO")

    print("-" * 60)

    print(
        resultado["titulo"]
    )

    print()

    print("GANCHO")

    print("-" * 60)

    print(
        resultado["gancho"]
    )

    print()

    print("ROTEIRO")

    print("-" * 60)

    print(
        resultado["roteiro"]
    )

    print()

    print("SHORT / REEL")

    print("-" * 60)

    print(
        resultado["short"]
    )

    print()

    print("INDICADORES ANALISADOS")

    print("-" * 60)

    print(
        ", ".join(
            resultado[
                "indicadores_analisados"
            ]
        )
    )

    print("=" * 60)


# ============================================================
# TESTE
# ============================================================

def main():

    resultado = gerar_conteudo()

    exibir_conteudo(
        resultado
    )


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()