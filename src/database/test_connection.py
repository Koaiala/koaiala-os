import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def test_connection():
    connection = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
    )

    print("============================================")
    print("KOAIALA DATABASE")
    print("============================================")
    print("✓ Conexão com PostgreSQL estabelecida")
    print(f"✓ Banco: {os.getenv('DATABASE_NAME')}")
    print("✓ Status: ONLINE")
    print("============================================")

    connection.close()


if __name__ == "__main__":
    test_connection()