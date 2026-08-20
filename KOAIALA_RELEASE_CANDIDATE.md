# Koaiala OS — Release Candidate

## Validação final

Execute, nesta ordem:

```powershell
python -m src.core.integration_check
python -m src.core.hardening_check
python -m src.core.system_check
python -m src.core.operational_check
```

O `integration_check` valida os imports e contratos de módulos.
O `hardening_check` executa a cadeia econômica real sobre o PostgreSQL e valida as respostas dos motores.
Os dois checks finais confirmam o núcleo e a camada operacional.

Se todos terminarem com `APROVADO`, o Koaiala entra em Release Candidate.
