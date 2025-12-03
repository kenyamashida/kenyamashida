import os
import base64
import requests
import re
import sys

# Pega as credenciais das Variáveis de Ambiente (Secrets)
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("Erro: Secrets não encontradas. Verifique o GitHub Settings.")
    sys.exit(1)

# 1. Obter novo Access Token (usando o Refresh Token)
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post("https://accounts.spotify.com/api/token",
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})

try:
    access_token = response.json()["access_token"]
except KeyError:
    print("Erro ao atualizar token. Verifique seu Refresh Token.")
    print(response.json())
    sys.exit(1)

# 2. Consultar API "Currently Playing"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("https://api.spotify.com/v1/me/player/currently-playing?market=BR", headers=headers)

song_content = ""

# Verifica se está tocando algo (Status 204 = nada tocando)
if response.status_code == 204 or response.json() is None:
    song_content = "🎵 Não estou ouvindo nada no Spotify agora."
else:
    data = response.json()
    # Verifica se é música (pode ser podcast)
    if data["item"] is None:
         song_content = "🎵 Ouvindo um Podcast ou arquivo local."
    else:
        song_name = data["item"]["name"]
        artist_name = data["item"]["artists"][0]["name"]
        link = data["item"]["external_urls"]["spotify"]
        # Formata o texto com Link
        song_content = f"🎵 Ouvindo agora: <a href='{link}'>**{song_name}** - {artist_name}</a>"

print(f"Status: {song_content}")

# 3. Atualizar o README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

# Regex para substituir apenas o conteúdo entre as tags
pattern = r".*"
replacement = f"\n<div align='center'>{song_content}</div>\n"

new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
