#!/usr/bin/env python3
import os
import re
import zipfile
import subprocess

# SCRIPT DE COMPILACIÓN C5-REAL — EL ESPACIO ENTRE NOSOTROS
# Genera PDF (vía Chrome Headless) y EPUB (empaquetado manual XHTML) sin dependencias externas.

MD_FILE = "el_espacio_entre_nosotros.md"
PDF_FILE = "el_espacio_entre_nosotros.pdf"
EPUB_FILE = "el_espacio_entre_nosotros.epub"
HTML_TEMP = "el_espacio_entre_nosotros_print.html"

def md_to_html_chunk(text):
    # Parsea sintaxis básica de markdown a HTML para el libro
    # Escapar caracteres HTML básicos
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Restaurar los tags HTML que pusimos a propósito o blockquotes
    text = re.sub(r'^&gt;\s*(.*)', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    
    # Bloques de código (Clase e idioma)
    def repl_code_block(match):
        lang = match.group(1) or "txt"
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', repl_code_block, text, flags=re.DOTALL)
    
    # Cabeceras
    text = re.sub(r'^#\s+(.*)', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*)', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*)', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Formateo inline
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # Líneas horizontales
    text = re.sub(r'^---$', r'<hr />', text, flags=re.MULTILINE)
    
    # Párrafos
    blocks = text.split("\n\n")
    html_blocks = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("<h") or block.startswith("<pre") or block.startswith("<blockquote") or block.startswith("<hr"):
            html_blocks.append(block)
        else:
            # Reemplazar saltos de línea internos por <br/>
            block = block.replace("\n", "<br />")
            html_blocks.append(f"<p>{block}</p>")
            
    return "\n".join(html_blocks)

def compile_pdf():
    print("[PDF] Generando HTML optimizado para impresión...")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_content = f.read()
        
    html_body = md_to_html_chunk(md_content)
    
    css = """
    @page {
        size: A5;
        margin: 20mm 15mm 20mm 15mm;
        @bottom-right {
            content: counter(page);
            font-family: 'Georgia', serif;
            font-size: 9pt;
        }
    }
    body {
        font-family: 'Georgia', 'Palatino', serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #0A0A0A;
        background-color: #FFFFFF;
    }
    h1 {
        text-align: center;
        margin-top: 50mm;
        font-size: 26pt;
        font-weight: normal;
        page-break-after: always;
    }
    h2 {
        page-break-before: always;
        margin-top: 30mm;
        font-size: 18pt;
        font-weight: normal;
        border-bottom: 1px solid #E0E0E0;
        padding-bottom: 5px;
    }
    h3 {
        font-size: 13pt;
        margin-top: 15mm;
    }
    p {
        text-align: justify;
        text-indent: 8mm;
        margin: 0 0 4mm 0;
    }
    p:first-of-type {
        text-indent: 0;
    }
    pre {
        background-color: #F5F5F5;
        border-left: 3px solid #2B3BE5;
        padding: 10px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 6mm 0;
    }
    blockquote {
        margin: 6mm 8mm;
        font-style: italic;
        color: #555555;
        border-left: 2px solid #CCCCCC;
        padding-left: 10px;
    }
    code {
        font-family: 'Courier New', monospace;
        font-size: 9.5pt;
        background-color: #F9F9F9;
        padding: 1px 3px;
    }
    hr {
        border: 0;
        border-top: 1px solid #CCCCCC;
        margin: 10mm 0;
        text-align: center;
    }
    """
    
    html_full = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>El Espacio Entre Nosotros</title>
        <style>{css}</style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    with open(HTML_TEMP, "w", encoding="utf-8") as f:
        f.write(html_full)
        
    print("[PDF] Compilando PDF vía Google Chrome Headless...")
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={PDF_FILE}",
        HTML_TEMP
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[PDF] PDF generado con éxito: {PDF_FILE}")
    except Exception as e:
        print(f"[ERROR] Error al generar PDF: {e}")
    finally:
        if os.path.exists(HTML_TEMP):
            os.remove(HTML_TEMP)

def compile_epub():
    print("[EPUB] Compilando EPUB estructurado...")
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extraer capítulos y secciones
    sections = re.split(r'^(##\s+.*?|#\s+CAPÍTULO\s+30.*?)$', content, flags=re.MULTILINE)
    
    intro_html = ""
    chapters = []
    
    # El primer fragmento antes de la primera cabecera es la introducción/cabecera del libro
    current_title = "Cover"
    current_content = ""
    
    for part in sections:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## ") or part.startswith("# CAPÍTULO"):
            if current_content:
                chapters.append((current_title, current_content))
            current_title = part.replace("#", "").strip()
            current_content = ""
        else:
            current_content += part + "\n\n"
            
    if current_content:
        chapters.append((current_title, current_content))
        
    # Crear estructura de archivos temporales
    epub_dir = "epub_build"
    os.makedirs(os.path.join(epub_dir, "META-INF"), exist_ok=True)
    os.makedirs(os.path.join(epub_dir, "OEBPS"), exist_ok=True)
    
    # 1. mimetype (sin newline, sin comprimir)
    with open(os.path.join(epub_dir, "mimetype"), "w") as f:
        f.write("application/epub+zip")
        
    # 2. META-INF/container.xml
    container_xml = """<?xml version="1.0"?>
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
    </container>"""
    with open(os.path.join(epub_dir, "META-INF", "container.xml"), "w") as f:
        f.write(container_xml)
        
    # 3. OEBPS/styles.css
    epub_css = """
    body {
        font-family: Georgia, serif;
        margin: 5%;
        line-height: 1.5;
        text-align: justify;
    }
    h1, h2, h3 {
        text-align: center;
        color: #111111;
    }
    pre {
        background-color: #f4f4f4;
        padding: 5px;
        font-family: monospace;
        font-size: 0.85em;
        border-left: 2px solid #2B3BE5;
    }
    blockquote {
        margin: 1em 2em;
        font-style: italic;
        color: #555555;
    }
    p {
        text-indent: 1em;
        margin: 0;
    }
    """
    with open(os.path.join(epub_dir, "OEBPS", "styles.css"), "w") as f:
        f.write(epub_css)
        
    # 4. Escribir capítulos a XHTML
    xhtml_manifest = []
    xhtml_spine = []
    
    for idx, (title, raw_md) in enumerate(chapters):
        ch_filename = f"chapter_{idx}.xhtml"
        body_html = md_to_html_chunk(raw_md)
        
        xhtml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es">
        <head>
            <title>{title}</title>
            <link rel="stylesheet" type="text/css" href="styles.css" />
        </head>
        <body>
            {body_html}
        </body>
        </html>"""
        
        with open(os.path.join(epub_dir, "OEBPS", ch_filename), "w") as f:
            f.write(xhtml_content)
            
        xhtml_manifest.append(f'<item id="ch_{idx}" href="{ch_filename}" media-type="application/xhtml+xml" />')
        xhtml_spine.append(f'<itemref idref="ch_{idx}" />')
        
    # 5. OEBPS/content.opf
    manifest_items = "\n        ".join(xhtml_manifest)
    spine_items = "\n        ".join(xhtml_spine)
    
    content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
    <package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
            <dc:title>El Espacio Entre Nosotros</dc:title>
            <dc:creator opf:role="aut">MOSKV-1 APEX</dc:creator>
            <dc:language>es</dc:language>
            <dc:identifier id="BookId">urn:uuid:31359b4-usera-bilbao-omega</dc:identifier>
        </metadata>
        <manifest>
            <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml" />
            <item id="style" href="styles.css" media-type="text/css" />
            {manifest_items}
        </manifest>
        <spine toc="ncx">
            {spine_items}
        </spine>
    </package>"""
    
    with open(os.path.join(epub_dir, "OEBPS", "content.opf"), "w") as f:
        f.write(content_opf)
        
    # 6. OEBPS/toc.ncx (Table of Contents)
    nav_points = []
    for idx, (title, _) in enumerate(chapters):
        nav_points.append(f"""
        <navPoint id="navPoint-{idx}" playOrder="{idx+1}">
            <navLabel><text>{title}</text></navLabel>
            <content src="chapter_{idx}.xhtml" />
        </navPoint>""")
    nav_items = "\n".join(nav_points)
    
    toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE ncx PUBLIC "-//NISO//DTD NCX 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
        <head>
            <meta name="dtb:uid" content="urn:uuid:31359b4-usera-bilbao-omega"/>
            <meta name="dtb:depth" content="1"/>
            <meta name="dtb:totalPageCount" content="0"/>
            <meta name="dtb:maxPageNumber" content="0"/>
        </head>
        <docTitle><text>El Espacio Entre Nosotros</text></docTitle>
        <navMap>
            {nav_items}
        </navMap>
    </ncx>"""
    
    with open(os.path.join(epub_dir, "OEBPS", "toc.ncx"), "w") as f:
        f.write(toc_ncx)
        
    # 7. Comprimir en un archivo EPUB válido
    # El archivo mimetype debe ser el primero y estar STORED (sin compresión)
    with zipfile.ZipFile(EPUB_FILE, "w", zipfile.ZIP_DEFLATED) as epub:
        # Añadir mimetype sin comprimir
        epub.write(os.path.join(epub_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        
        # Añadir el resto de archivos comprimidos
        epub.write(os.path.join(epub_dir, "META-INF", "container.xml"), os.path.join("META-INF", "container.xml"))
        epub.write(os.path.join(epub_dir, "OEBPS", "styles.css"), os.path.join("OEBPS", "styles.css"))
        epub.write(os.path.join(epub_dir, "OEBPS", "content.opf"), os.path.join("OEBPS", "content.opf"))
        epub.write(os.path.join(epub_dir, "OEBPS", "toc.ncx"), os.path.join("OEBPS", "toc.ncx"))
        
        for idx, _ in enumerate(chapters):
            ch_filename = f"chapter_{idx}.xhtml"
            epub.write(os.path.join(epub_dir, "OEBPS", ch_filename), os.path.join("OEBPS", ch_filename))
            
    # Limpiar directorio de compilación
    for root, dirs, files in os.walk(epub_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(epub_dir)
    
    print(f"[EPUB] EPUB generado con éxito: {EPUB_FILE}")

if __name__ == "__main__":
    compile_pdf()
    compile_epub()
