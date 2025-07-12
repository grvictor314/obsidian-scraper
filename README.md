# Obsidian Scraper

**Crawls a Mighty Networks community into a local Obsidian vault**, mirroring la estructura de carpetas, páginas, imágenes, vídeos y enlaces externos.

---

## Descripción

Este script en Python realiza un recorrido completo (crawler) de un sitio web basado en Mighty Networks y genera una copia local en formato Markdown dentro de tu vault de Obsidian. Extrae:

* Títulos y contenido de texto (párrafos y listas).
* Imágenes e incrusta los archivos en `attachments/`.
* Vídeos alojados en la plataforma.
* Enlaces externos (formularios, links a otros dominios).

Cada página se guarda con frontmatter (título, fecha, URL original) y rutas de carpeta que reflejan la jerarquía de URLs.

---

## Instalación

1. Clona el repositorio:

   ```bash
   git clone git@github.com:grvictor314/obsidian-scraper.git
   cd obsidian-scraper
   ```
2. Crea y activa un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate         # Windows PowerShell
   ```
3. Instala dependencias:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Configuración

Edita las variables en la parte superior de `scrape_to_obsidian.py`:

* `VAULT_PATH`: Ruta absoluta a tu vault de Obsidian.
* `COMMUNITY_BASE`: URL base del sitio (por ejemplo, `https://community.mightynetworks.com`).
* `START_PATH`: Ruta inicial del crawl (`"/"` por defecto para la home).
* `ALLOWED_DOMAIN`: Dominio interno permitido (se ajusta automáticamente desde `COMMUNITY_BASE`).
* Prefijos y selectores CSS:

  * `NOTE_PREFIX`: Prefijo para los archivos Markdown.
  * `TITLE_SELECTOR`, `CONTENT_SELECTORS`, `IMAGE_SELECTOR`, `VIDEO_SELECTORS` para ajustar la extracción de elementos.

---

## Uso

Ejecuta el script para iniciar el volcado de información:

```bash
python scrape_to_obsidian.py
```

Verás en consola mensajes indicando las notas guardadas:

```
Guardada nota: ~/Obsidian/VaultName/home/Mighty_home.md
Guardada nota: ~/Obsidian/VaultName/forums/general/Mighty_general.md
...
```

Después, abre Obsidian apuntando a tu vault (`VAULT_PATH`) para explorar la copia local de la comunidad.

---

## Personalización

* Excluir rutas o añadir patrones de filtrado en la función `extract_links`.
* Ajustar retrasos (`time.sleep`) o headers de `requests` para evitar bloqueos.
* Incluir autenticación si la plataforma requiere login.
* Ampliar `requirements.txt` con librerías adicionales si añades nuevas funcionalidades.

---

© 2025 grvictor314
