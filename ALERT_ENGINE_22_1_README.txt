KOAIALA ALERT ENGINE 22.1

Objetivo:
Transformar eventos relevantes já produzidos pelo Koaiala
em alertas operacionais, sem alterar os motores existentes.

Regras iniciais:
1. Divergência atual x preditivo -> ALTO.
2. Divergência + 3 ou mais sinais ativos -> CRITICO.
3. Sinal ativo com ganho histórico positivo -> MODERADO.
4. Sem eventos -> INFO.

Teste:
python -m src.core.alert_engine_check

Este bloco é independente do Dashboard e pode ser integrado
ao Dashboard 22.1 depois que o check passar.
