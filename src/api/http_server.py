"""
KOAIALA API 19.0
API HTTP mínima e funcional para consumo do Koaiala.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from src.core.final_cycle_v18 import executar


def _json_default(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "to_eng_string"):
        return obj.to_eng_string()
    return str(obj)


def payload():
    resultado = executar()
    return {
        "status": "OK",
        "system": "KOAIALA OS",
        "version": "1.0.0",
        "cycle": resultado,
    }


class Handler(BaseHTTPRequestHandler):

    def _send(self, status, data):
        body = json.dumps(
            data,
            default=_json_default,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        try:
            data = payload()

            if path == "/health":
                self._send(
                    200,
                    {
                        "status": "OK",
                        "system": "KOAIALA OS",
                        "version": "1.0.0",
                    },
                )
                return

            if path in (
                "/",
                "/api",
                "/api/status",
            ):
                self._send(200, data)
                return

            if path == "/api/scenario":
                self._send(
                    200,
                    data["cycle"]["master"],
                )
                return

            if path == "/api/prediction":
                self._send(
                    200,
                    data["cycle"]["prediction"],
                )
                return

            if path == "/api/reconciliation":
                self._send(
                    200,
                    data["cycle"]["reconciliation"],
                )
                return

            if path == "/api/decision":
                self._send(
                    200,
                    data["cycle"]["decision"],
                )
                return

            self._send(
                404,
                {
                    "status": "ERROR",
                    "message": "Endpoint não encontrado.",
                },
            )

        except Exception as exc:
            self._send(
                500,
                {
                    "status": "ERROR",
                    "message": str(exc),
                },
            )

    def log_message(self, format, *args):
        return


def iniciar(host="127.0.0.1", port=8000):
    server = HTTPServer(
        (host, port),
        Handler,
    )

    print(
        f"KOAIALA API 19.0 "
        f"http://{host}:{port}"
    )

    server.serve_forever()


if __name__ == "__main__":
    iniciar()
