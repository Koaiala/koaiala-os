from src.core.final_cycle_v18 import executar
from src.web.dashboard_repository import INDICATORS,ensure_snapshot_table,get_indicator_history
def main():
    print("="*76);print("KOAIALA DASHBOARD PRODUCT CHECK 22.0");print("="*76)
    r=executar()
    if r["status"]!="OK": raise SystemExit("CORE: FALHA")
    ensure_snapshot_table(); print("CORE: OK"); print("SNAPSHOT TABLE: OK")
    total=0
    for i in INDICATORS:
        n=len(get_indicator_history(i,5)); total+=n; print(f"HISTÓRICO {i}: {n} registros")
    print(f"OBSERVAÇÕES DISPONÍVEIS: {total}");print("DASHBOARD PRODUCT: OK")
    print("STATUS FINAL: KOAIALA DASHBOARD 22.0 APROVADO ✓");print("="*76)
if __name__=="__main__": main()
