import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import deque
import re

# CONFIGURATION
VAULT_PATH = os.path.expanduser("~/Obsidian/VaultName")  # Ruta a tu vault
COMMUNITY_BASE = "https://community.mightynetworks.com"  # Dominio base
START_PATH = "/"  # Ruta inicial para arrancar el crawl
NOTE_PREFIX = "Mighty_"  # Prefijo para las notas generadas
# Dominio aceptado (sin subdominio)
ALLOWED_DOMAIN = urlparse(COMMUNITY_BASE).netloc

# Selectores para extraer contenido
TITLE_SELECTOR = 'h1'
CONTENT_SELECTORS = ['p', 'li']  # párrafos y listas
VIDEO_SELECTORS = ['video source', 'video']  # para detectar videos
IMAGE_SELECTOR = 'img'  # para detectar imágenes

# UTILIDADES

def slugify(text):
    """Convierte un texto en un slug seguro para nombre de archivo."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')


def fetch_page(session, url):
    resp = session.get(url)
    resp.raise_for_status()
    return resp.text


def download_file(session, file_url, save_dir):
    """Descarga un archivo y lo guarda en save_dir, devolviendo el nombre de archivo."""
    os.makedirs(save_dir, exist_ok=True)
    parsed = urlparse(file_url)
    filename = os.path.basename(parsed.path) or 'file'
    # Asegurar nombre único
    local_path = os.path.join(save_dir, filename)
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(local_path):
        filename = f"{base}_{counter}{ext}"
        local_path = os.path.join(save_dir, filename)
        counter += 1
    # Descargar por streaming
    with session.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return filename


def parse_content_media_links(session, html, page_dir):
    """Extrae texto, detecta y descarga videos e imágenes, y recoge enlaces externos."""
    soup = BeautifulSoup(html, 'html.parser')
    # Extraer texto
    parts = []
    for sel in CONTENT_SELECTORS:
        for el in soup.select(sel):
            txt = el.get_text(strip=True)
            if txt:
                parts.append(txt)
    content_text = "\n\n".join(parts)

    # Videos
    local_videos = []
    for sel in VIDEO_SELECTORS:
        for tag in soup.select(sel):
            src = tag.get('src') or tag.get('data-src')
            if src:
                url = urljoin(COMMUNITY_BASE, src)
                filename = download_file(session, url, os.path.join(page_dir, 'attachments'))
                local_videos.append(os.path.join('attachments', filename))

    # Imágenes
    local_images = []
    for img in soup.select(IMAGE_SELECTOR):
        src = img.get('src') or img.get('data-src')
        if src:
            url = urljoin(COMMUNITY_BASE, src)
            filename = download_file(session, url, os.path.join(page_dir, 'attachments'))
            local_images.append(os.path.join('attachments', filename))

    # Enlaces externos y formularios
    external_links = []
    for a in soup.find_all('a', href=True):
        href = urljoin(COMMUNITY_BASE, a['href'])
        parsed = urlparse(href)
        if parsed.netloc != ALLOWED_DOMAIN:
            text = a.get_text(strip=True) or href
            external_links.append((text, href))

    return content_text, local_videos, local_images, external_links


def save_page(path, title, text, videos, images, ext_links):
    """Guarda una nota Markdown con embeds de medios y lista de enlaces externos."""
    # Directorio de la página
    clean_path = path.lstrip('/')
    page_dir = os.path.join(VAULT_PATH, os.path.dirname(clean_path))
    os.makedirs(page_dir, exist_ok=True)
    filename_base = os.path.basename(clean_path) or 'home'
    filename = slugify(f"{NOTE_PREFIX}_{filename_base}") + '.md'
    full_path = os.path.join(page_dir, filename)

    # Frontmatter
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    front = [
        '---',
        f'title: "{title}"',
        f'date: {date_str}',
        f'original_path: "{path}"',
        '---',
        ''
    ]
    # Cuerpo
    body = front + [text, '']
    # Imágenes embebidas
    for img in images:
        body.append(f"![[{img}]]")
    # Videos embebidos
    for vid in videos:
        body.append(f"![[{vid}]]")
    # Enlaces externos
    if ext_links:
        body.append('\n**Enlaces externos:**')
        for text, href in ext_links:
            body.append(f"- [{text}]({href})")

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(body))
    print(f"Guardada nota: {full_path}")


def extract_links(html):
    """Extrae enlaces internos al mismo dominio."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = urljoin(COMMUNITY_BASE, a['href'])
        parsed = urlparse(href)
        if parsed.netloc == ALLOWED_DOMAIN:
            links.add(parsed.path)
    return links


def crawl_site():
    session = requests.Session()
    visited = set()
    queue = deque([START_PATH])

    while queue:
        path = queue.popleft()
        if path in visited:
            continue
        visited.add(path)
        full_url = urljoin(COMMUNITY_BASE, path)
        try:
            html = fetch_page(session, full_url)
        except requests.HTTPError as e:
            print(f"Error accediendo {full_url}: {e}")
            continue

        title_el = BeautifulSoup(html, 'html.parser').select_one(TITLE_SELECTOR)
        title = title_el.get_text(strip=True) if title_el else 'Sin_Titulo'
        content, videos, images, ext_links = parse_content_media_links(
            session,
            html,
            os.path.join(VAULT_PATH, path.lstrip('/').rsplit('/',1)[0])
        )
        save_page(path, title, content, videos, images, ext_links)

        for link_path in extract_links(html):
            if link_path not in visited:
                queue.append(link_path)


def main():
    crawl_site()

if __name__ == '__main__':
    main()
