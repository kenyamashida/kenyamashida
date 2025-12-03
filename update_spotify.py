import os
import base64
import requests
import sys

# --- CONFIGURAÇÃO ---
START_MARKER = "<h2>🎵 Meu Spotify</h2>"
END_MARKER = "</div>"

# Pega as credenciais
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("Erro: Secrets não encontradas.")
    sys.exit(1)

# 1. Autenticação
print("Autenticando...")
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post("https://accounts.spotify.com/api/token",
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})
try:
    access_token = response.json()["access_token"]
except KeyError:
    print("Erro no token. Verifique o JSON retornado:")
    print(response.json())
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# 2. Busca o Top 5
print("Buscando Top 5...")
response = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5", headers=headers)

content_lines = []
if response.status_code == 200:
    items = response.json().get("items", [])
    if not items:
        content_lines.append("Sem dados suficientes este mês.")
    else:
        content_lines.append("<b>🎧 Top 5 do Mês:</b><br/>")
        for i, track in enumerate(items, 1):
            name = track['name']
            artist = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            content_lines.append(f"{i}. <a href='{url}'>{name} - {artist}</a>")
else:
    print(f"Erro na API do Spotify: {response.status_code}")
    content_lines.append("Erro ao buscar músicas.")

# Conteúdo final formatado
new_content_block = "<br/>".join(content_lines)
final_block = f"{START_MARKER}\n<div align='center'>{new_content_block}</div>\n{END_MARKER}"

# 3. Lógica Segura de Substituição (SEM REGEX)
print("Lendo README.md...")
with open("README.md", "r", encoding="utf-8") as f:
    original_content = f.read()

# Verifica se as tags existem
if START_MARKER not in original_content or END_MARKER not in original_content:
    print("ERRO: Tags ou não encontradas no README.")
    sys.exit(1)

# Corta o arquivo em: Antes da Tag | (Conteúdo Velho) | Depois da Tag
part_before = original_content.split(START_MARKER)[0]
part_after = original_content.split(END_MARKER)[1]

# Monta o novo arquivo
new_readme = part_before + final_block + part_after

# Salva
print("Salvando alterações...")
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Sucesso!")
