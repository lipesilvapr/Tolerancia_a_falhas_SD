import os
import time
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

REPLICA_URL = "127.0.0.1"
REPLICA_PORT = 8001

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
                        if sent > 5 * 1024 * 1024:  # Simula falha após ~5MB
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

        host = REPLICA_URL
        port = REPLICA_PORT
        path = f"/files/{filename}"
        headers = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Range: bytes={start_byte}-\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(headers.encode())

            buffer = b""
            while b"\r\n\r\n" not in buffer:
                buffer += s.recv(4096)
            _, _, buffer = buffer.partition(b"\r\n\r\n")

            try:
                while True:
                    chunk = s.recv(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
                print(f"[Coordinator] ✅ Download finalizado com sucesso pela réplica")
            except Exception as e:
                print(f"[Coordinator] ❌ Erro ao continuar download da réplica: {e}")
                self.wfile.write(b"\nErro ao continuar download da replica.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python server.py <porta>")
        sys.exit(1)

    try:
        porta = int(sys.argv[1])
    except ValueError:
        print("Porta inválida. Deve ser um número.")
        sys.exit(1)

    server = HTTPServer(("localhost", porta), CoordinatorHandler)
    print(f"🔵 Coordenador rodando em http://localhost:{porta}")
    server.serve_forever()