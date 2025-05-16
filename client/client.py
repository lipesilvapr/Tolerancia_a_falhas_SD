from urllib import request

filename = input("Digite o nome do arquivo para download: ")
url = f"http://localhost:8000/download?file={filename}"

print(f"⬇️ Solicitando arquivo: {filename}")
with request.urlopen(url) as resp:
    with open(f"baixado_{filename}", "wb") as f:
        while chunk := resp.read(64 * 1024):
            f.write(chunk)
print("✅ Download concluído!")
