# Koaiala OS — Core Completion Pack

Este pacote fecha e integra o núcleo analítico do MVP.

Incluído:
- Economic Score ampliado;
- Scenario Engine integrado ao Registry;
- suporte a SELIC, IPCA, INPC, IGP-M, PIB, desemprego e câmbio;
- Forecast Engine;
- Decision Engine;
- Master Engine;
- Full Cycle;
- System Check;
- API HTTP mínima sem dependência adicional.

Execução principal:

    python -m src.core.koaiala_engine

Ciclo completo:

    python -m src.core.full_cycle

Teste de integração:

    python -m src.core.system_check

API:

    python -m src.api.http_server

Endpoints:
    /health
    /scenario
    /forecast
    /decision
    /run

O Content Engine permanece separado do núcleo econômico.
