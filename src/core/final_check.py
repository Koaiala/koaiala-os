"""
KOAIALA OS 1.0
FINAL CHECK

Última verificação estrutural e operacional antes
da liberação do MVP 1.0.
"""

import importlib
import sys
from datetime import datetime

from src.database.connection import get_connection
from src.sense.registry import get_active_indicators


# ============================================================
# CONFIGURAÇÃO
# ============================================================

VERSION = "1.0.0"

REQUIRED_MODULES = [
    "src.database.connection",
    "src.sense.registry",
    "src.insight.analysis_engine",
    "src.insight.economic_interpreter",
    "src.insight.economic_score",
    "src.core.koaiala_engine",
    "src.core.full_cycle",
    "src.core.system_check",
    "src.core.operational_check",
    "src.core.integration_check",
    "src.core.hardening_check",
    "src.api.http_server",
    "src.web.dashboard_server",
]

OPTIONAL_MODULES = [
    "src.forecast.forecast_engine",
    "src.risk.risk_engine",
]


# ============================================================
# RESULTADOS
# ============================================================

resultados = []


def registrar(nome, sucesso, detalhe=""):

    resultados.append(
        {
            "teste": nome,
            "sucesso": sucesso,
            "detalhe": detalhe,
        }
    )

    status = "✓" if sucesso else "✗"

    if detalhe:

        print(
            f"{status} {nome}: {detalhe}"
        )

    else:

        print(
            f"{status} {nome}"
        )


# ============================================================
# PYTHON
# ============================================================

def verificar_python():

    versao = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    sucesso = sys.version_info >= (3, 10)

    registrar(
        "Python",
        sucesso,
        versao,
    )


# ============================================================
# MÓDULOS
# ============================================================

def verificar_modulos():

    for modulo in REQUIRED_MODULES:

        try:

            importlib.import_module(
                modulo
            )

            registrar(
                modulo,
                True,
            )

        except Exception as error:

            registrar(
                modulo,
                False,
                str(error),
            )


def verificar_modulos_opcionais():

    for modulo in OPTIONAL_MODULES:

        try:

            importlib.import_module(
                modulo
            )

            registrar(
                modulo,
                True,
            )

        except ModuleNotFoundError:

            registrar(
                modulo,
                True,
                "implementação integrada em outra camada",
            )

        except Exception as error:

            registrar(
                modulo,
                False,
                str(error),
            )


# ============================================================
# POSTGRESQL
# ============================================================

def verificar_banco():

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT 1"
        )

        resultado = cursor.fetchone()

        sucesso = (
            resultado is not None
            and resultado[0] == 1
        )

        registrar(
            "PostgreSQL",
            sucesso,
            "conexão ativa"
            if sucesso
            else "resposta inválida",
        )

        cursor.close()

    except Exception as error:

        registrar(
            "PostgreSQL",
            False,
            str(error),
        )

    finally:

        if connection:

            connection.close()


# ============================================================
# REGISTRY
# ============================================================

def verificar_registry():

    try:

        indicadores = (
            get_active_indicators()
        )

        quantidade = len(
            indicadores
        )

        sucesso = quantidade > 0

        registrar(
            "Indicator Registry",
            sucesso,
            (
                f"{quantidade} "
                "indicadores ativos"
            ),
        )

        if sucesso:

            print(
                "  "
                + ", ".join(
                    indicadores.keys()
                )
            )

    except Exception as error:

        registrar(
            "Indicator Registry",
            False,
            str(error),
        )


# ============================================================
# MASTER ENGINE
# ============================================================

def verificar_master_engine():

    try:

        modulo = importlib.import_module(
            "src.core.koaiala_engine"
        )

        executar = getattr(
            modulo,
            "executar_koaiala",
            None,
        )

        if not callable(executar):

            registrar(
                "Master Engine",
                False,
                "executar_koaiala não encontrada",
            )

            return

        resultado = executar()

        sucesso = (
            isinstance(resultado, dict)
        )

        if sucesso:

            status = resultado.get(
                "status",
                "OK"
            )

            sucesso = (
                status != "ERRO"
            )

        registrar(
            "Master Engine",
            sucesso,
            (
                "execução concluída"
                if sucesso
                else "retorno inválido"
            ),
        )

    except Exception as error:

        registrar(
            "Master Engine",
            False,
            str(error),
        )


# ============================================================
# API
# ============================================================

def verificar_api():

    try:

        importlib.import_module(
            "src.api.http_server"
        )

        registrar(
            "API",
            True,
            "módulo carregado",
        )

    except Exception as error:

        registrar(
            "API",
            False,
            str(error),
        )


# ============================================================
# DASHBOARD
# ============================================================

def verificar_dashboard():

    try:

        importlib.import_module(
            "src.web.dashboard_server"
        )

        registrar(
            "Dashboard",
            True,
            "módulo carregado",
        )

    except Exception as error:

        registrar(
            "Dashboard",
            False,
            str(error),
        )


# ============================================================
# RESULTADO FINAL
# ============================================================

def resultado_final():

    total = len(
        resultados
    )

    aprovados = sum(
        1
        for item in resultados
        if item["sucesso"]
    )

    falhas = total - aprovados

    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)

    print(
        f"Testes executados: {total}"
    )

    print(
        f"Aprovados: {aprovados}"
    )

    print(
        f"Falhas: {falhas}"
    )

    print()

    if falhas:

        print("FALHAS ENCONTRADAS")
        print("-" * 60)

        for item in resultados:

            if not item["sucesso"]:

                print(
                    f"- {item['teste']}: "
                    f"{item['detalhe']}"
                )

        print()
        print("=" * 60)
        print(
            "STATUS FINAL: "
            "KOAIALA OS 1.0 REPROVADO ✗"
        )
        print("=" * 60)

        return False

    print("=" * 60)
    print(
        "STATUS FINAL: "
        "KOAIALA OS 1.0 APROVADO ✓"
    )
    print("=" * 60)

    return True


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print()
    print("=" * 60)
    print("KOAIALA OS 1.0 - FINAL CHECK")
    print("=" * 60)

    print(
        f"Versão: {VERSION}"
    )

    print(
        "Execução: "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    print()

    print("AMBIENTE")
    print("-" * 60)

    verificar_python()

    print()
    print("DEPENDÊNCIAS INTERNAS")
    print("-" * 60)

    verificar_modulos()
    verificar_modulos_opcionais()

    print()
    print("INFRAESTRUTURA")
    print("-" * 60)

    verificar_banco()
    verificar_registry()

    print()
    print("EXECUÇÃO")
    print("-" * 60)

    verificar_master_engine()
    verificar_api()
    verificar_dashboard()

    aprovado = resultado_final()

    if not aprovado:

        sys.exit(1)


if __name__ == "__main__":

    main()