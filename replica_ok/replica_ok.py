import socket
import os
import threading
import time

def handle_coord_request(conn):
    payload = conn.recv(1024).decode()
    client_ip, client_port, filename, offset = payload.split(":")
    client_port = int(client_port)
    offset = int(offset)

    file_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.isfile(file_path):
        print(f"[Replica] Arquivo não encontrado: {filename}")
        return

    print(f"[Replica] Iniciando envio para {client_ip}:{client_port} a partir do byte {offset}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((client_ip, client_port))

        with open(file_path, "rb") as f:
            f.seek(offset)
            while chunk := f.read(64 * 1024):
                client_sock.sendall(chunk)
                time.sleep(0.01)  # Aguarde um curto período antes de enviar o próximo bloco

    print(f"[Replica] ✅ Envio finalizado para {client_ip}:{client_port}")

if __name__ == "__main__":
    host = "localhost"
    port = 8001

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(5)
        print(f"🟡 Réplica rodando em {host}:{port}")
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle_coord_request, args=(conn,)).start()
