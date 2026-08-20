"""
KOAIALA
DATABASE CONNECTION

Responsável por estabelecer a conexão
entre o Koaiala e o PostgreSQL.

As credenciais são carregadas do arquivo:

    src/.env
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# ============================================================
# LOCALIZAÇÃO DO ARQUIVO .ENV
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[1]

ENV_FILE = BASE_DIR / ".env"


# ============================================================
# CARREGAMENTO DAS VARIÁVEIS
# ============================================================

load_dotenv(
    dotenv_path=ENV_FILE
)


# ============================================================
# CONEXÃO COM POSTGRESQL
# ============================================================

def get_connection():
    """
    Cria e retorna uma conexão com o PostgreSQL.
    """

    return psycopg2.connect(
        host=os.getenv(
            "DATABASE_HOST"
        ),

        port=os.getenv(
            "DATABASE_PORT"
        ),

        database=os.getenv(
            "DATABASE_NAME"
        ),

        user=os.getenv(
            "DATABASE_USER"
        ),

        password=os.getenv(
            "DATABASE_PASSWORD"
        ),
    )