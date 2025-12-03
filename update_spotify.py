import os
import base64
import requests
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

# URL OFICIAL DO SPOTIFY (Corrigida)
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

# URL OFICIAL DO SPOTIFY API (Corrigida)
top_tracks_url = "https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5"

response = requests.get(top_tracks_url, headers=headers)

if response.status_code != 200:
    print(f"Erro na API: {response.status_code}")
    sys.exit(1)

items = response.json().get("items", [])

if not items:
    html_content = "Sem dados musicais recentes."
else:
    rows = ""
    for track in items:
        name = track['name']
        artist = track['artists'][0]['name']
        link = track['external_urls']['spotify']
        
        # Imagem (tenta pegar a menor)
        if track['album']['images']:
            img = track['album']['images'][-1]['url'] 
        else:
            img = "https://via.placeholder.com/64"
        
        # HTML compacto numa linha
        rows += f'<tr><td><img src="{img}" width="40" height="40" style="border-radius:5px;"/></td><td><a href="{link}"><b>{name}</b></a><br/>{artist}</td></tr>'

    html_content = f'<table>{rows}</table>'

# --- 3. ATUALIZAR README (Lógica Start/Stop) ---
print("Atualizando README.md...")

with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

# Definindo os marcadores exatos
start_marker = "<h3>🔥 Top 5 do Mês</h3>"
end_marker = "</div>"

# Encontrar a posição do Título
start_index = readme_content.find(start_marker)

if start_index == -1:
    print(f"ERRO: Não encontrei o título '{start_marker}' no README.md")
    sys.exit(1)

# Encontrar a posição do fechamento da DIV (após o título)
# O offset (start_index + len(start_marker)) garante que buscamos o </div> DEPOIS do título
search_start_pos = start_index + len(start_marker)
end_index = readme_content.find(end_marker, search_start_pos)

if end_index == -1:
    print(f"ERRO: Não encontrei o fechamento '{end_marker}' após o título.")
    sys.exit(1)

# Recortar e Colar:
# 1. Tudo antes do título + título
part_before = readme_content[:search_start_pos]
# 2. Tudo depois do fechamento da div
part_after = readme_content[end_index:]

# Monta o novo arquivo: Parte Anterior + Nova Tabela + Parte Final
new_readme = f"{part_before}\n\n{html_content}\n\n{part_after}"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Sucesso! Tabela inserida entre o Título e o </div>.")
