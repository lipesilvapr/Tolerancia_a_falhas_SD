import socket
import threading
import os
import time

REPLICA_HOST = "localhost"
REPLICA_PORT = 8001

def handle_client(conn, addr):
    filename = conn.recv(1024).decode().strip()
    file_path = os.path.join(os.path.dirname(__file__), filename)

    if not os.path.isfile(file_path):
        print(f"[Coordinator] Arquivo não encontrado: {filename}")
        conn.close()
        return

    file_size = os.path.getsize(file_path)
    sent = 0
    try:
        print(f"[Coordinator] Enviando arquivo: {filename} ({file_size} bytes) para {addr[0]}:{addr[1]}")
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(64 * 1024)
                if not chunk:
                    break
                conn.sendall(chunk)
                sent += len(chunk)
                time.sleep(0.05)
                if sent > 10 * 1024 * 1024:
                    raise Exception("💥 Falha simulada")

        print(f"[Coordinator] ✅ Envio completo: {filename}")
    except Exception as e:
        print(f"[Coordinator] ⚠️ Falha simulada: {e}")
        conn.close()
        print("[Coordinator] Notificando réplica para continuar...")

        notify_replica(addr[0], 9000, filename, sent)

def notify_replica(client_ip, client_port, filename, start_byte):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((REPLICA_HOST, REPLICA_PORT))
        payload = f"{client_ip}:{client_port}:{filename}:{start_byte}"
        s.sendall(payload.encode())

if __name__ == "__main__":
    host = "localhost"
    port = 8000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(5)
        print(f"🔵 Coordenador rodando em {host}:{port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
