import socket

def download_file(filename):
    host = "localhost"
    port = 8000
    filename = filename.strip()

    print(f"⬇️ Solicitando arquivo: {filename}")

    with open(f"baixado_{filename}", "wb") as f:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 9000))  # Cliente escuta nesta porta para possível continuação
        sock.listen(1)

        # Conexão com coordenador
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as coord_sock:
            coord_sock.connect((host, port))
            coord_sock.sendall(filename.encode())

            # Recebe início do arquivo
            while True:
                data = coord_sock.recv(64 * 1024)
                if not data:
                    break
                f.write(data)

        print("⚠️ Conexão encerrada pelo coordenador. Aguardando continuação da réplica...")

        # Aceita conexão da réplica
        conn, _ = sock.accept()
        with conn:
            while True:
                data = conn.recv(64 * 1024)
                if not data:
                    break
                f.write(data)

        print("✅ Download finalizado com sucesso pela réplica.")

if __name__ == "__main__":
    filename = input("Digite o nome do arquivo para download: ")
    download_file(filename)
