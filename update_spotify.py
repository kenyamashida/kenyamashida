import os
import base64
import requests
import re
import sys

# 1. Configuração e Autenticação
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("ERRO: Secrets não encontradas.")
    sys.exit(1)

print("Autenticando...")
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post("[https://accounts.spotify.com/api/token](https://accounts.spotify.com/api/token)",
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})

try:
    access_token = response.json()["access_token"]
except KeyError:
    print("ERRO: Token inválido. Verifique o Refresh Token.")
    print(response.json())
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# 2. Buscar Top Músicas
print("Buscando Top 5...")
response = requests.get("[https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5](https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5)", headers=headers)

if response.status_code != 200:
    print(f"Erro na API: {response.status_code}")
    sys.exit(1)

items = response.json().get("items", [])
if not items:
    html_content = "Sem dados musicais recentes."
else:
    # Montando a tabela HTML numa linha só para não quebrar o Markdown
    rows = ""
    for track in items:
        name = track['name']
        artist = track['artists'][0]['name']
        link = track['external_urls']['spotify']
        # Tenta pegar imagem, se não tiver usa placeholder
        img = track['album']['images'][-1]['url'] if track['album']['images'] else "[https://via.placeholder.com/64](https://via.placeholder.com/64)"
        
        # Cria a linha da tabela (sem quebras de linha para evitar bugs)
        rows += f'<tr><td><img src="{img}" width="40" height="40" style="border-radius:5px;"/></td><td><a href="{link}"><b>{name}</b></a><br/>{artist}</td></tr>'

    html_content = f'<table>{rows}</table>'

# 3. Ler o README original
with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

# 4. Substituir APENAS o conteúdo entre as tags
# A regex procura: QUALQUER COISA pattern = r"()(.*?)()"

# A substituição recoloca as tags + o novo conteúdo HTML no meio
replacement = f"\\1\n<div align='center'>{html_content}</div>\n\\3"

# Verifica se as tags existem antes de substituir
if "" not in readme_content:
    print("ERRO: Tags do Spotify não encontradas no README.md. Resete o arquivo.")
    sys.exit(1)

new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

# 5. Salvar
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Sucesso! README atualizado com a tabela.")
