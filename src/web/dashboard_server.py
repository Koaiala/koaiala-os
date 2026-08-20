"""
KOAIALA DASHBOARD 19.0
Dashboard web simples, sem dependências externas.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
import json


def _get_api():
    with urlopen(
        "http://127.0.0.1:8000/api/status",
        timeout=10,
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def _html():
    data = _get_api()
    cycle = data["cycle"]

    master = cycle["master"]
    prediction = cycle["prediction"]
    reconciliation = cycle["reconciliation"]
    decision = cycle["decision"]

    detailed = master.get("score_detalhado", {})
    score = detailed.get(
        "score_normalizado",
        master.get("score", "N/D"),
    )
    scenario = detailed.get(
        "classificacao",
        master.get("classificacao", "N/D"),
    )

    sinais = prediction.get("sinais", {})

    rows = ""

    for indicador, item in sinais.items():
        rows += f"""
        <tr>
          <td>{indicador}</td>
          <td>{item.get('sinal', 'N/D')}</td>
          <td>{item.get('confianca', 'N/D')}</td>
          <td>{item.get('ganho_historico', 'N/D')}</td>
        </tr>
        """

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="300">
<title>Koaiala OS</title>
<style>
body {{
  font-family: Arial, sans-serif;
  margin: 0;
  background: #f4f6f8;
  color: #17202a;
}}
header {{
  background: #17202a;
  color: white;
  padding: 24px 40px;
}}
main {{
  max-width: 1200px;
  margin: 25px auto;
  padding: 0 20px;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
  gap: 16px;
}}
.card {{
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px #0001;
}}
h1,h2 {{ margin-top: 0; }}
.value {{
  font-size: 28px;
  font-weight: bold;
}}
table {{
  width: 100%;
  border-collapse: collapse;
}}
th,td {{
  padding: 12px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}}
</style>
</head>
<body>
<header>
  <h1>KOAIALA OS</h1>
  <div>Sistema Operacional de Inteligência Econômica</div>
</header>
<main>

<div class="grid">
  <div class="card">
    <h2>Cenário</h2>
    <div class="value">{scenario}</div>
    <p>Score: {score}</p>
  </div>

  <div class="card">
    <h2>Reconciliação</h2>
    <div class="value">{reconciliation.get('reconciliacao','N/D')}</div>
    <p>Risco: {reconciliation.get('risco_reconciliacao','N/D')}</p>
  </div>

  <div class="card">
    <h2>Decisão</h2>
    <div class="value">{decision.get('postura','N/D')}</div>
    <p>Horizonte: {decision.get('horizonte','N/D')}</p>
  </div>

  <div class="card">
    <h2>Confiança</h2>
    <div class="value">{decision.get('confianca','N/D')}</div>
    <p>Forecast preditivo</p>
  </div>
</div>

<br>

<div class="card">
<h2>Evidência Preditiva</h2>
<table>
<thead>
<tr>
<th>Indicador</th>
<th>Sinal</th>
<th>Confiança</th>
<th>Ganho vs. baseline</th>
</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>

<br>

<div class="card">
<h2>Leitura do sistema</h2>
<p>{decision.get('justificativa','N/D')}</p>
<p><strong>Gatilho de revisão:</strong>
{decision.get('gatilho_revisao','N/D')}</p>
</div>

</main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            body = _html().encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.end_headers()
            self.wfile.write(body)

        except Exception as exc:
            body = (
                f"<h1>KOAIALA Dashboard</h1>"
                f"<p>Erro: {exc}</p>"
            ).encode("utf-8")

            self.send_response(500)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8",
            )
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, format, *args):
        return


def iniciar(host="127.0.0.1", port=8080):
    server = HTTPServer(
        (host, port),
        Handler,
    )

    print(
        f"KOAIALA Dashboard 19.0 "
        f"http://{host}:{port}"
    )

    server.serve_forever()


if __name__ == "__main__":
    iniciar()
