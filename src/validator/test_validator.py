from economic_validator import validate_selic_observation


def testar_data_futura():
    observacao = {
        "data": "05/08/2026",
        "valor": "14.00"
    }

    valido, erros = validate_selic_observation(observacao)

    print("=" * 60)
    print("KOAIALA VALIDATOR")
    print("=" * 60)
    print(f"Observação: {observacao}")
    print(f"Resultado válido: {valido}")
    print(f"Erros: {erros}")
    print("=" * 60)


if __name__ == "__main__":
    testar_data_futura()