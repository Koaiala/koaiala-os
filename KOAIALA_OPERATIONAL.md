# Koaiala OS — Camada Operacional

## Validação

```powershell
python -m src.core.operational_check
```

## Ciclo completo

```powershell
python -m src.core.full_cycle
```

## API

```powershell
python -m src.api.http_server
```

Endpoints:
- `/health`
- `/indicators`
- `/analysis?indicator=IPCA`
- `/scenario`
- `/forecast`
- `/risk`
- `/decision`
- `/run`

## Dashboard

Com a API rodando:

```powershell
python -m src.web.dashboard_server
```

Abra `http://127.0.0.1:8080`.

## Launcher

```powershell
python run_koaiala.py check
python run_koaiala.py cycle
python run_koaiala.py api
python run_koaiala.py dashboard
```

O dashboard é uma interface operacional simples; não substitui a validação econômica dos motores.
