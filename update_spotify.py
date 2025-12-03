import os
import base64
import requests
import re
import sys

# Pega as credenciais
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("Erro: Secrets não encontradas.")
    sys.exit(1)

# 1. Autenticação (Refresh Token -> Access Token)
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post("https://accounts.spotify.com/api/token",
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})
try:
    access_token = response.json()["access_token"]
except KeyError:
    print("Erro ao atualizar token. Verifique se você gerou um token com escopo 'user-top-read'.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# 2. Busca o Top 5 Tracks (Curto Prazo = ~4 semanas)
# time_range options: short_term (4 weeks), medium_term (6 months), long_term (years)
response = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5", headers=headers)

content_lines = []

if response.status_code == 200:
    items = response.json().get("items", [])
    if not items:
        content_lines.append("Sem dados suficientes este mês.")
    else:
        # Monta a lista bonitinha
        content_lines.append("<b>🎧 Top 5 do Mês:</b><br/>")
        for i, track in enumerate(items, 1):
            name = track['name']
            artist = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            # Formato: 1. Nome da Música - Artista
            content_lines.append(f"{i}. <a href='{url}'>{name} - {artist}</a>")
else:
    content_lines.append("Erro ao buscar Top 5.")

# Junta tudo com quebra de linha HTML
final_content = "<br/>".join(content_lines)

print(f"Conteúdo gerado:\n{final_content}")

# 3. Atualiza o README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = r".*"
replacement = f"\n<div align='center'>{final_content}</div>\n"

new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
