import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class ReplicaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/files/"):
            filename = self.path.split("/files/")[1]
            file_path = os.path.join(os.path.dirname(__file__), filename)

            if not os.path.isfile(file_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Arquivo nao encontrado")
                return

            file_size = os.path.getsize(file_path)
            range_header = self.headers.get("Range")
            start = 0
            if range_header:
                start = int(range_header.strip().split("=")[1].split("-")[0])

            self.send_response(206 if range_header else 200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(file_size - start))
            if range_header:
                self.send_header("Content-Range", f"bytes {start}-{file_size - 1}/{file_size}")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                while chunk := f.read(64 * 1024):
                    self.wfile.write(chunk)
                    self.wfile.flush()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8001), ReplicaHandler)
    print("🟡 Replica rodando em http://localhost:8001")
    server.serve_forever()
