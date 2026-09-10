"""HTTP display plane for the SME Credit Underwriting Intelligence Workbench."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .flags import FlagError
from .serialize import jsonable
from .service import WorkbenchService

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "workbench"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

SERVICE = WorkbenchService()


def _query(path: str) -> dict[str, str]:
    parsed = urlparse(path)
    raw = parse_qs(parsed.query)
    return {key: values[0] for key, values in raw.items() if values}


def _actor(query: dict[str, str]) -> tuple[str, str, str]:
    return (
        query.get("application_id", "SME-L001"),
        query.get("actor_tenant", "TENANT-ALPHA"),
        query.get("actor_role", "CREDIT_ANALYST"),
    )


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "NexLendWorkbench/1.0"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send(self, code: int, payload: Any, content_type: str = "application/json; charset=utf-8") -> None:
        body = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = _query(self.path)
        if path in {"/", "/index.html"}:
            self._static("index.html", "text/html; charset=utf-8")
            return
        if path == "/styles.css":
            self._static("styles.css", "text/css; charset=utf-8")
            return
        if path == "/app.js":
            self._static("app.js", "text/javascript; charset=utf-8")
            return
        if path == "/api/health":
            self._send(200, {"ok": True, "product": "SME Credit Underwriting Intelligence Workbench"})
            return
        try:
            self._api_get(path, query)
        except Exception as exc:  # noqa: BLE001 — surface domain errors to the UI
            self._send(400, {"ok": False, "error": type(exc).__name__, "message": str(exc)})

    def _api_get(self, path: str, query: dict[str, str]) -> None:
        if path == "/api/catalog":
            self._send(200, SERVICE.catalog())
            return
        if path == "/api/flags":
            self._send(200, SERVICE.snapshot_flags())
            return
        if path == "/api/tower":
            _, tenant, role = _actor(query)
            self._send(200, SERVICE.control_tower(actor_tenant=tenant, actor_role=role))
            return
        if path == "/api/dossier":
            application_id, tenant, role = _actor(query)
            purpose = query.get("purpose", "UNDERWRITING_RUNTIME")
            self._send(
                200,
                jsonable(
                    SERVICE.case_dossier(
                        application_id, actor_tenant=tenant, actor_role=role, purpose=purpose
                    )
                ),
            )
            return
        if path == "/api/probe/invented-threshold":
            self._send(200, SERVICE.probe_invented_threshold(query.get("application_id", "SME-L014")))
            return
        if path == "/api/probe/injection":
            self._send(
                200,
                SERVICE.probe_injection(
                    query.get("application_id", "SME-L009"),
                    query.get("actor_tenant", "TENANT-ALPHA"),
                ),
            )
            return
        if path == "/api/probe/superseded-policy":
            self._send(200, SERVICE.probe_superseded_policy())
            return
        self._send(404, {"ok": False, "error": "not_found", "path": path})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._read_json()
            self._api_post(path, body)
        except FlagError as exc:
            self._send(400, {"ok": False, "error": "FlagError", "message": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._send(400, {"ok": False, "error": type(exc).__name__, "message": str(exc)})

    def _api_post(self, path: str, body: dict[str, Any]) -> None:
        if path == "/api/flags":
            self._send(200, SERVICE.set_flags({k: bool(v) for k, v in body.items()}))
            return
        if path == "/api/decision":
            self._send(
                200,
                SERVICE.record_decision(
                    str(body["application_id"]),
                    actor_role=str(body.get("actor_role", "CREDIT_ANALYST")),
                    actor_tenant=str(body.get("actor_tenant", "TENANT-ALPHA")),
                    outcome=str(body.get("outcome", "REFER")),
                ),
            )
            return
        if path == "/api/feedback":
            self._send(
                200,
                SERVICE.capture_feedback(
                    str(body["application_id"]),
                    actor_role=str(body.get("actor_role", "CREDIT_ANALYST")),
                    actor_tenant=str(body.get("actor_tenant", "TENANT-ALPHA")),
                    feedback_type=str(body.get("feedback_type", "AI_ACCEPTED")),
                ),
            )
            return
        if path == "/api/feedback/ungoverned":
            self._send(
                200,
                SERVICE.refuse_ungoverned_write(
                    str(body.get("application_id", "SME-L015")),
                    str(body.get("destination", "POLICY_BUNDLE")),
                ),
            )
            return
        self._send(404, {"ok": False, "error": "not_found", "path": path})

    def _static(self, name: str, content_type: str) -> None:
        target = (STATIC / name).resolve()
        if STATIC.resolve() not in target.parents and target != STATIC.resolve():
            self._send(403, {"ok": False, "error": "forbidden"})
            return
        if not target.is_file():
            self._send(404, {"ok": False, "error": "missing_static", "name": name})
            return
        self._send(200, target.read_bytes(), content_type)


def make_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), WorkbenchHandler)


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = make_server(host, port)
    print(f"NexLend workbench http://{host}:{port}/", flush=True)
    httpd.serve_forever()
