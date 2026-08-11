from datetime import date, datetime
from decimal import Decimal


def validate_selic_observation(observation):
    errors = []

    # 1. Verifica se a data existe
    if not observation.get("data"):
        errors.append("Data ausente")

    # 2. Verifica se o valor existe
    if not observation.get("valor"):
        errors.append("Valor ausente")

    if errors:
        return False, errors

    # 3. Valida o formato da data
    try:
        observation_date = datetime.strptime(
            observation["data"],
            "%d/%m/%Y"
        ).date()

    except ValueError:
        errors.append("Data em formato inválido")
        return False, errors

    # 4. Impede dados futuros
    if observation_date > date.today():
        errors.append("Data futura")

    # 5. Valida o valor
    try:
        Decimal(observation["valor"])

    except Exception:
        errors.append("Valor não numérico")

    # 6. Resultado final
    if errors:
        return False, errors

    return True, []