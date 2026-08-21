from src.database.connection import get_connection

INDICATORS = ("SELIC_META", "IPCA", "IGP_M", "INPC")

def ensure_snapshot_table():
    c = get_connection()
    cur = c.cursor()
    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS koaiala_dashboard_snapshots (
            id BIGSERIAL PRIMARY KEY,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            score NUMERIC(12,8),
            scenario VARCHAR(80),
            confidence VARCHAR(40),
            predictive_scenario VARCHAR(80),
            reconciliation VARCHAR(40),
            risk VARCHAR(40),
            decision VARCHAR(40)
        )""")
        c.commit()
    finally:
        cur.close(); c.close()

def save_snapshot(cycle):
    ensure_snapshot_table()
    m = cycle.get("master", {})
    r = cycle.get("reconciliation", {})
    d = cycle.get("decision", {})
    detail = m.get("score_detalhado", {})
    if not isinstance(detail, dict): detail = {}
    score = detail.get("score_normalizado", m.get("score"))
    scenario = detail.get("classificacao", r.get("cenario_atual"))
    confidence = d.get("confianca", m.get("confianca"))
    c = get_connection(); cur = c.cursor()
    try:
        cur.execute("""INSERT INTO koaiala_dashboard_snapshots
        (score,scenario,confidence,predictive_scenario,reconciliation,risk,decision)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (score,str(scenario) if scenario is not None else None,
         str(confidence) if confidence is not None else None,
         r.get("cenario_preditivo"),r.get("reconciliacao"),
         r.get("risco_reconciliacao"),d.get("postura")))
        c.commit()
    finally:
        cur.close(); c.close()

def get_indicator_history(indicator, limit=60):
    c = get_connection(); cur = c.cursor()
    try:
        cur.execute("""SELECT observation_date,value
        FROM economic_observations WHERE indicator_code=%s
        ORDER BY observation_date DESC LIMIT %s""",(indicator,int(limit)))
        rows = cur.fetchall(); rows.reverse()
        return [{"date":r[0].isoformat(),"value":float(r[1])} for r in rows]
    finally:
        cur.close(); c.close()

def get_snapshots(limit=60):
    ensure_snapshot_table()
    c = get_connection(); cur = c.cursor()
    try:
        cur.execute("""SELECT created_at,score,scenario,confidence,
        predictive_scenario,reconciliation,risk,decision
        FROM koaiala_dashboard_snapshots ORDER BY created_at DESC LIMIT %s""",
        (int(limit),))
        rows = cur.fetchall(); rows.reverse()
        return [{"created_at":r[0].isoformat(),"score":float(r[1]) if r[1] is not None else None,
        "scenario":r[2],"confidence":r[3],"predictive_scenario":r[4],
        "reconciliation":r[5],"risk":r[6],"decision":r[7]} for r in rows]
    finally:
        cur.close(); c.close()
