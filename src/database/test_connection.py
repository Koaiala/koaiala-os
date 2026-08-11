from connection import get_connection


if __name__ == "__main__":
    connection = get_connection()

    print("=" * 50)
    print("KOAIALA DATABASE")
    print("=" * 50)
    print("✓ Conexão com PostgreSQL estabelecida")
    print("✓ Camada de conexão funcionando")
    print("✓ Status: ONLINE")
    print("=" * 50)

    connection.close()