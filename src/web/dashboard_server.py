from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs
from html import escape
import json
from src.web.dashboard_repository import INDICATORS,get_indicator_history,get_snapshots,save_snapshot

API="http://127.0.0.1:8000/api/status"

def data():
    with urlopen(API,timeout=15) as r: return json.loads(r.read().decode())

def scalar(x):
    if isinstance(x,(str,int,float,bool)): return x
    if isinstance(x,dict):
        for k in ("classificacao","cenario_atual","cenario","nivel","valor","score_normalizado","score"):
            if k in x:
                v=scalar(x[k])
                if v is not None:return v
    return None

def fields(c):
    m,r,d=c["master"],c["reconciliation"],c["decision"]
    detail=m.get("score_detalhado",{}) if isinstance(m.get("score_detalhado",{}),dict) else {}
    score=scalar(detail.get("score_normalizado")) or scalar(m.get("score"))
    scenario=scalar(detail.get("classificacao")) or scalar(r.get("cenario_atual")) or "N/D"
    conf=scalar(d.get("confianca")) or scalar(m.get("confianca")) or "N/D"
    return score or "N/D",scenario,conf

def chart(h):
    if not h:return "<div class='empty'>Sem histórico.</div>"
    vals=[x["value"] for x in h]; lo,hi=min(vals),max(vals); span=hi-lo or 1
    pts=[]
    for i,v in enumerate(vals):
        x=20+i*860/max(len(vals)-1,1); y=210-170*(v-lo)/span
        pts.append(f"{x:.1f},{y:.1f}")
    return f"<svg viewBox='0 0 900 240'><polyline points='{' '.join(pts)}' fill='none' stroke='currentColor' stroke-width='3'/></svg>"

def html():
    d=data(); c=d["cycle"]; save_snapshot(c)
    score,scenario,conf=fields(c); r=c["reconciliation"]; dec=c["decision"]
    rows=""
    for k,v in c["prediction"].get("sinais",{}).items():
        gain=v.get("ganho_historico")
        g="N/D" if gain is None else f"{float(gain)*100:+.2f} p.p."
        rows+=f"<tr><td><b>{escape(str(k))}</b></td><td>{escape(str(v.get('sinal','N/D')))}</td><td>{escape(str(v.get('confianca','N/D')))}</td><td>{g}</td></tr>"
    charts=""
    for k in INDICATORS:
        charts+=f"<section class='card'><h3>{k}</h3>{chart(get_indicator_history(k,60))}</section>"
    hist=""
    for s in reversed(get_snapshots(20)):
        hist+=f"<tr><td>{s['created_at'][:19].replace('T',' ')}</td><td>{s['scenario']}</td><td>{s['predictive_scenario']}</td><td>{s['reconciliation']}</td><td>{s['decision']}</td></tr>"
    return f"""<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta http-equiv='refresh' content='300'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Koaiala 22.0</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Segoe UI,Arial;background:#f4f6f8;color:#17202a}}header{{background:#182848;color:white;padding:30px 5%}}main{{max-width:1250px;margin:28px auto;padding:0 20px}}.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}}.charts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.card{{background:white;border:1px solid #e4e8ec;border-radius:14px;padding:22px;min-width:0;box-shadow:0 4px 18px #00000009}}.label{{color:#68737d;font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.value{{font-size:27px;font-weight:700;margin-top:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.sub{{color:#68737d;margin-top:8px}}.alert{{border-left:5px solid #9a6700}}table{{width:100%;border-collapse:collapse}}th,td{{padding:13px 10px;border-bottom:1px solid #e4e8ec;text-align:left}}th{{color:#68737d;font-size:12px;text-transform:uppercase}}svg{{width:100%;height:240px;background:#fafbfc;border-radius:10px;color:#182848}}.empty{{padding:35px;color:#68737d}}@media(max-width:900px){{.grid,.charts{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:600px){{.grid,.charts{{grid-template-columns:1fr}}}}
</style></head><body><header><h1>KOAIALA</h1><p>Sistema Operacional de Inteligência Econômica · Dashboard 22.0</p></header><main>
<div class='grid'><section class='card'><div class='label'>Cenário atual</div><div class='value'>{scenario}</div><div class='sub'>Score: {score}</div></section>
<section class='card alert'><div class='label'>Cenário preditivo</div><div class='value'>{r.get('cenario_preditivo','N/D')}</div><div class='sub'>Confiança: {conf}</div></section>
<section class='card'><div class='label'>Reconciliação</div><div class='value'>{r.get('reconciliacao','N/D')}</div><div class='sub'>Risco: {r.get('risco_reconciliacao','N/D')}</div></section>
<section class='card'><div class='label'>Decisão</div><div class='value'>{dec.get('postura','N/D')}</div><div class='sub'>Horizonte: {dec.get('horizonte','N/D')}</div></section></div><br>
<div class='card'><h2>Histórico dos indicadores</h2><p class='sub'>Dados armazenados no PostgreSQL.</p></div><br><div class='charts'>{charts}</div><br>
<section class='card'><h2>Evidência preditiva</h2><table><thead><tr><th>Indicador</th><th>Sinal</th><th>Confiança</th><th>Ganho vs. baseline</th></tr></thead><tbody>{rows}</tbody></table></section><br>
<section class='card'><h2>Histórico do Koaiala</h2><p class='sub'>Evolução de cenário, previsão, reconciliação e decisão.</p><table><thead><tr><th>Data</th><th>Cenário</th><th>Preditivo</th><th>Reconciliação</th><th>Decisão</th></tr></thead><tbody>{hist}</tbody></table></section><br>
<section class='card'><div class='label'>Leitura econômica</div><p>{escape(str(dec.get('justificativa','N/D')))}</p><p class='sub'><b>Gatilho:</b> {escape(str(dec.get('gatilho_revisao','N/D')))}</p></section></main></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if urlparse(self.path).path=="/api/history":
                q=parse_qs(urlparse(self.path).query); ind=q.get("indicator",["IPCA"])[0]
                if ind not in INDICATORS: ind="IPCA"
                b=json.dumps(get_indicator_history(ind,120),ensure_ascii=False).encode()
                self.send_response(200);self.send_header("Content-Type","application/json; charset=utf-8");self.end_headers();self.wfile.write(b);return
            b=html().encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(b)
        except Exception as e:
            b=f"<h1>Koaiala Dashboard</h1><p>Erro: {escape(str(e))}</p>".encode();self.send_response(500);self.send_header("Content-Type","text/html; charset=utf-8");self.end_headers();self.wfile.write(b)
    def log_message(self,*args):pass

if __name__=="__main__": HTTPServer(("127.0.0.1",8080),Handler).serve_forever()
