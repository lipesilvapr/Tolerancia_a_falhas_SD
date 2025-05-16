import socket

def download_file(filename):
    host = "localhost"
    port = 8000
    filename = filename.strip()
    path = f"/download?file={filename}"

    print(f"⬇️ Solicitando arquivo: {filename}")

    with open(f"baixado_{filename}", "wb") as f:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode())

        # Ler cabeçalho
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            buffer += sock.recv(4096)
        header, _, buffer = buffer.partition(b"\r\n\r\n")
        print("Cabeçalho recebido.")

        # Processar corpo
        content_length = None
        for line in header.split(b"\r\n"):
            if line.lower().startswith(b"content-length:"):
                content_length = int(line.split(b":")[1].strip())

        received = len(buffer)
        f.write(buffer)

        while True:
            chunk = sock.recv(64 * 1024)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

        print(f"✅ Download concluído! ({received} bytes escritos)")

if __name__ == "__main__":
    filename = input("Digite o nome do arquivo para download: ")
    download_file(filename)