import os
import base64
import requests
import re
import sys

# --- 1. CONFIGURAÇÃO ---
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("ERRO: Secrets não encontradas.")
    sys.exit(1)

print("Autenticando com Spotify...")

# URL OFICIAL PARA PEGAR O TOKEN
auth_url = "https://accounts.spotify.com/api/token"

auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post(auth_url,
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})

try:
    access_token = response.json()["access_token"]
except KeyError:
    print("ERRO: Token inválido. Verifique o Refresh Token.")
    print("Resposta:", response.json())
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# --- 2. BUSCAR DADOS ---
print("Buscando Top 5 músicas...")

# URL OFICIAL PARA TOP TRACKS
# limit=5: Pega apenas 5 músicas
# time_range=short_term: Dados das últimas 4 semanas
top_tracks_url = "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=short_term"

response = requests.get(top_tracks_url, headers=headers)

if response.status_code != 200:
    print(f"Erro na API: {response.status_code}")
    sys.exit(1)

items = response.json().get("items", [])

if not items:
    html_content = "Sem dados musicais recentes."
else:
    # Montando a tabela HTML compacta
    rows = ""
    for track in items:
        name = track['name']
        artist = track['artists'][0]['name']
        link = track['external_urls']['spotify']
        
        # Imagem do álbum (tenta pegar a menor disponível)
        if track['album']['images']:
            img = track['album']['images'][-1]['url'] 
        else:
            img = "https://via.placeholder.com/64"
        
        # HTML sem quebra de linha para evitar bugs de markdown
        rows += f'<tr><td><img src="{img}" width="40" height="40" style="border-radius:5px;"/></td><td><a href="{link}"><b>{name}</b></a><br/>{artist}</td></tr>'

    html_content = f'<table>{rows}</table>'

# --- 3. ATUALIZAR README ---
print("Atualizando README.md...")

try:
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    print("ERRO: README.md não encontrado.")
    sys.exit(1)

# Regex que encontra o espaço entre as tags
pattern = r"()(.*?)()"

if "" not in readme_content:
    print("ERRO: Tags não encontradas no README.md")
    sys.exit(1)

# Substitui mantendo as tags e inserindo o HTML no meio
replacement = f"\\1\n{html_content}\n\\3"

new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Sucesso! Tabela inserida entre as tags.")
