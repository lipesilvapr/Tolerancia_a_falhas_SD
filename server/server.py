import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import request

REPLICA_URL = "http://127.0.0.1:8001"

class CoordinatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/download?file="):
            filename = self.path.split("=")[1]
            file_path = os.path.join(os.path.dirname(__file__), filename)

            if not os.path.isfile(file_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Arquivo nao encontrado")
                return

            file_size = os.path.getsize(file_path)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename={filename}")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()

            sent = 0
            try:
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(64 * 1024)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        sent += len(chunk)
                        self.wfile.flush()
                        time.sleep(0.05)
                        if sent > 5 * 1024 * 1024:
                            raise Exception("💥 Falha simulada no coordenador")
                print(f"[Coordinator] ✅ Download completo pelo coordenador")
            except Exception as e:
                print(f"[Coordinator] Falha detectada: {e}")
                print(f"[Coordinator] Tentando continuar o download pela réplica...")
                self._continuar_pela_replica(filename, sent)
        else:
            self.send_response(404)
            self.end_headers()

    def _continuar_pela_replica(self, filename, start_byte):
        print(f"[Coordinator] Conectando à réplica a partir do byte {start_byte}...")

        req = request.Request(
            f"{REPLICA_URL}/files/{filename}",
            headers={"Range": f"bytes={start_byte}-"}
        )
        try:
            with request.urlopen(req) as resp:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
            print(f"[Coordinator] ✅ Download finalizado com sucesso pela réplica")
        except Exception as e:
            print(f"[Coordinator] ❌ Erro ao continuar download da réplica: {e}")
            self.wfile.write(b"\nErro ao continuar download da replica.")

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), CoordinatorHandler)
    print("🔵 Coordenador rodando em http://localhost:8000")
    server.serve_forever()
