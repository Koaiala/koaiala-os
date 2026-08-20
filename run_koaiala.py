"""Launcher operacional do Koaiala OS."""
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("modo", choices=["check", "cycle", "api", "dashboard"])
    args = parser.parse_args()
    comandos = {
        "check": [sys.executable, "-m", "src.core.operational_check"],
        "cycle": [sys.executable, "-m", "src.core.full_cycle"],
        "api": [sys.executable, "-m", "src.api.http_server"],
        "dashboard": [sys.executable, "-m", "src.web.dashboard_server"],
    }
    raise SystemExit(subprocess.call(comandos[args.modo]))


if __name__ == "__main__":
    main()
