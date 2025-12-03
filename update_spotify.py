import os
import base64
import requests
import re
import sys

# --- CONFIGURAÇÃO ---
try:
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
except KeyError:
    print("Erro: Secrets não encontradas.")
    sys.exit(1)

# 1. Autenticação
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
response = requests.post("https://accounts.spotify.com/api/token",
                         data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
                         headers={"Authorization": f"Basic {auth_header}"})
try:
    access_token = response.json()["access_token"]
except KeyError:
    print("Erro ao atualizar token. Verifique o escopo user-top-read.")
    sys.exit(1)

headers = {"Authorization": f"Bearer {access_token}"}

# 2. Busca Top 5
response = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5", headers=headers)

final_content = ""

if response.status_code == 200:
    items = response.json().get("items", [])
    if not items:
        final_content = "Sem dados suficientes este mês."
    else:
        # AQUI ESTAVA O ERRO: Precisamos abrir a tag <table> antes do loop
        final_content = "<table>"
        
        for track in items[:5]:
            name = track['name']
            # Pega o primeiro artista
            artist = track['artists'][0]['name']
            link = track['external_urls']['spotify']
            # Pega a imagem pequena (64x64) que costuma ser a última da lista
            try:
                image_url = track['album']['images'][-1]['url']
            except IndexError:
                # Caso não tenha imagem, usa um placeholder transparente ou ícone
                image_url = "https://via.placeholder.com/64"

            # Monta a linha da tabela com HTML seguro
            final_content += f'''
            <tr>
                <td><img src="{image_url}" width="40" height="40" style="border-radius: 4px;"/></td>
                <td><a href="{link}"><b>{name}</b></a><br/>{artist}</td>
            </tr>
            '''
        
        # Fecha a tabela
        final_content += "</table>"
else:
    final_content = f"Erro na API: {response.status_code}"

print("HTML Gerado com sucesso.")

# 3. Atualiza o README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

# Substituição segura
pattern = r".*"
# removemos quebras de linha extras para evitar bugs de markdown
clean_content = final_content.replace('\n', '') 
replacement = f"\n<div align='center'>{clean_content}</div>\n"

new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
