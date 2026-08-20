"""
KOAIALA OS
INDICATOR SYNC

Sincronizador entre:

    src.sense.registry
            ↓
    economic_indicators

Responsabilidade:

1. Ler os indicadores ativos do Registry.
2. Verificar se cada indicador existe no PostgreSQL.
3. Inserir indicadores inexistentes.
4. Atualizar os metadados dos indicadores existentes.
5. Manter Registry e PostgreSQL sincronizados.

O Registry permanece como fonte de verdade
dos metadados dos indicadores.
"""

from src.database.connection import get_connection
from src.sense.registry import get_active_indicators


# ============================================================
# SINCRONIZAÇÃO DE UM INDICADOR
# ============================================================

def sincronizar_indicador(
    connection,
    indicador
):
    """
    Sincroniza um indicador do Registry
    com a tabela economic_indicators.

    Retorna:

        "INSERIDO"  -> indicador novo
        "ATUALIZADO" -> indicador já existente
    """

    codigo = indicador["code"]

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # Verifica se o indicador já existe
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM economic_indicators
            WHERE code = %s
            """,
            (codigo,)
        )

        resultado = cursor.fetchone()

        # ----------------------------------------------------
        # Indicador inexistente
        # ----------------------------------------------------

        if resultado is None:

            cursor.execute(
                """
                INSERT INTO economic_indicators (
                    code,
                    name,
                    source,
                    source_series,
                    unit,
                    frequency,
                    category,
                    description,
                    active
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    indicador["code"],
                    indicador["name"],
                    indicador["source"],
                    indicador["source_code"],
                    indicador["unit"],
                    indicador["frequency"],
                    indicador["category"],
                    indicador.get("description"),
                    indicador.get("active", True),
                )
            )

            return "INSERIDO"

        # ----------------------------------------------------
        # Indicador existente
        # ----------------------------------------------------

        indicator_id = resultado[0]

        cursor.execute(
            """
            UPDATE economic_indicators
            SET
                code = %s,
                name = %s,
                source = %s,
                source_series = %s,
                unit = %s,
                frequency = %s,
                category = %s,
                description = %s,
                active = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                indicador["code"],
                indicador["name"],
                indicador["source"],
                indicador["source_code"],
                indicador["unit"],
                indicador["frequency"],
                indicador["category"],
                indicador.get("description"),
                indicador.get("active", True),
                indicator_id,
            )
        )

        return "ATUALIZADO"

    finally:

        cursor.close()


# ============================================================
# SINCRONIZAÇÃO COMPLETA
# ============================================================

def sincronizar_registry():
    """
    Sincroniza todos os indicadores ativos
    do Registry com o PostgreSQL.

    Retorna um dicionário com o resultado
    de cada indicador.
    """

    indicadores = get_active_indicators()

    resultados = {}

    print()
    print("=" * 60)
    print("KOAIALA INDICATOR SYNC")
    print("=" * 60)

    print(
        f"Indicadores no Registry: "
        f"{len(indicadores)}"
    )

    connection = get_connection()

    try:

        for codigo, indicador in indicadores.items():

            try:

                resultado = sincronizar_indicador(
                    connection,
                    indicador
                )

                resultados[codigo] = {
                    "status": "OK",
                    "acao": resultado,
                }

                print(
                    f"{codigo}: {resultado}"
                )

            except Exception as erro:

                resultados[codigo] = {
                    "status": "ERRO",
                    "erro": str(erro),
                }

                print(
                    f"{codigo}: ERRO - {erro}"
                )

        # ----------------------------------------------------
        # Confirma todas as alterações
        # ----------------------------------------------------

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    inseridos = sum(
        1
        for resultado in resultados.values()
        if resultado.get("acao") == "INSERIDO"
    )

    atualizados = sum(
        1
        for resultado in resultados.values()
        if resultado.get("acao") == "ATUALIZADO"
    )

    erros = sum(
        1
        for resultado in resultados.values()
        if resultado.get("status") == "ERRO"
    )

    print()
    print("=" * 60)
    print("RESUMO DA SINCRONIZAÇÃO")
    print("=" * 60)

    print(
        f"Indicadores processados: "
        f"{len(resultados)}"
    )

    print(
        f"Indicadores inseridos: "
        f"{inseridos}"
    )

    print(
        f"Indicadores atualizados: "
        f"{atualizados}"
    )

    print(
        f"Erros: "
        f"{erros}"
    )

    if erros == 0:

        print(
            "STATUS FINAL: REGISTRY SINCRONIZADO ✓"
        )

    else:

        print(
            "STATUS FINAL: SINCRONIZAÇÃO COM ERROS"
        )

    print("=" * 60)

    return resultados


# ============================================================
# TESTE
# ============================================================

def main():

    sincronizar_registry()


# ============================================================
# PONTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    main()