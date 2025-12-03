import os
import base64
import requests
import sys

# --- CONFIGURAÇÃO ---
START_MARKER = "<h2>🎵 Meu Spotify</h2>"
END_MARKER = "</div>"

if not START_MARKER or not END_MARKER:
    print("ERRO CRÍTICO: Variáveis de marcação vazias.")
    sys.exit(1)

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
    print("Erro no token.")
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
        # INÍCIO DA TABELA
        content_lines.append("<table>")
        
        for track in items:
            name = track['name']
            artist = track['artists'][0]['name']
            url = track['external_urls']['spotify']
            # Pega a imagem do álbum (índice 2 é a pequena, 64x64, ideal para listas)
            try:
                image_url = track['album']['images'][2]['url']
            except IndexError:
                # Se não tiver imagem pequena, tenta a primeira
                image_url = track['album']['images'][0]['url']
            
            # Cria uma linha da tabela com Imagem + Texto
            row = f"""
            <tr>
                <td><a href="{url}"><img src="{image_url}" width="40" height="40" alt="Cover"></a></td>
                <td><a href="{url}"><b>{name}</b></a><br>{artist}</td>
            </tr>
            """
            content_lines.append(row)
            
        # FIM DA TABELA
        content_lines.append("</table>")
else:
    content_lines.append("Erro ao buscar músicas.")

# Junta tudo (remove quebras de linha extras para o HTML ficar compacto)
new_content_block = "".join(content_lines)
final_block = f"{START_MARKER}\n<div align='center'>{new_content_block}</div>\n{END_MARKER}"

# 3. Atualização do Arquivo
print("Lendo README.md...")
with open("README.md", "r", encoding="utf-8") as f:
    original_content = f.read()

if START_MARKER not in original_content or END_MARKER not in original_content:
    print("ERRO: Tags não encontradas.")
    sys.exit(1)

print("Substituindo conteúdo...")
part_before = original_content.split(START_MARKER)[0]
part_after = original_content.split(END_MARKER)[1]

new_readme = part_before + final_block + part_after

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Sucesso! Playlist visual gerada.")
