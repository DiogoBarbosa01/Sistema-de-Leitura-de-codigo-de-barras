import json
import socket
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Empty, Queue
from urllib.parse import parse_qs, urlparse


@dataclass
class MobileRequestStatus:
    ativo: bool
    mensagem: str


class MobileRequestService:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self._queue: Queue[str] = Queue()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def iniciar(self):
        if self._server:
            return

        queue_ref = self._queue

        class Handler(BaseHTTPRequestHandler):
            def _responder(self, status: int, payload: dict):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path != "/scan":
                    self._responder(404, {"ok": False, "mensagem": "Rota inválida"})
                    return
                params = parse_qs(parsed.query)
                codigo = (params.get("code") or [""])[0].strip().upper()
                if not codigo:
                    self._responder(400, {"ok": False, "mensagem": "Parâmetro 'code' é obrigatório"})
                    return
                queue_ref.put(codigo)
                self._responder(200, {"ok": True, "mensagem": "Código recebido"})

            def do_POST(self):
                parsed = urlparse(self.path)
                if parsed.path != "/scan":
                    self._responder(404, {"ok": False, "mensagem": "Rota inválida"})
                    return

                content_length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(content_length) if content_length else b"{}"
                try:
                    payload = json.loads(raw.decode("utf-8"))
                except Exception:
                    self._responder(400, {"ok": False, "mensagem": "JSON inválido"})
                    return

                codigo = str(payload.get("code", "")).strip().upper()
                if not codigo:
                    self._responder(400, {"ok": False, "mensagem": "Campo 'code' é obrigatório"})
                    return

                queue_ref.put(codigo)
                self._responder(200, {"ok": True, "mensagem": "Código recebido"})

            def log_message(self, _format, *_args):
                return

        self._server = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def parar(self):
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def ler_codigo(self) -> str | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def status(self) -> MobileRequestStatus:
        if not self._server:
            return MobileRequestStatus(False, "Servidor de requisição móvel inativo")

        ip = self._obter_ip_local()
        return MobileRequestStatus(
            True,
            f"Aguardando celular em http://{ip}:{self.port}/scan?code=CX-...",
        )

    @staticmethod
    def _obter_ip_local() -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            sock.close()
