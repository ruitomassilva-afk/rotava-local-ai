#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Server Local - Consola IA Rui Miguel Silva
Como usar: python rag_server.py
"""

import os
import json
import math
import time
import threading
import webbrowser
import urllib.request
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__)) or os.getcwd()

# CONFIGURACAO
KNOWLEDGE_DIR = r"C:\Users\ruito\OneDrive\Ambiente de Trabalho\Rui\Conhecimento_IA_Rui"
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen3:4b"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4
INDEX_FILE = "rag_index.json"
LOGO_FILE = "Rui_logo.png"
PORT = 8080

INDEX_LOCK = threading.Lock()


def ollama_embed(text):
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_HOST + "/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding", [])
    except Exception as e:
        print("[ERRO] Ollama embeddings: " + str(e))
        return []


def cosine_similarity(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def chunk_text(text, size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            while end > start and text[end] not in " \n\t":
                end -= 1
            if end == start:
                end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        start = end - overlap if end - overlap > start else end
        if start >= len(text):
            break
    return chunks


def load_index():
    p = os.path.join(SCRIPT_DIR, INDEX_FILE)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("[AVISO] Indice corrompido, sera reconstruido: " + str(e))
    return None


def save_index(index):
    with open(os.path.join(SCRIPT_DIR, INDEX_FILE), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)


def build_index():
    kp = Path(KNOWLEDGE_DIR)
    if not kp.exists():
        print("[ERRO] Pasta nao encontrada: " + KNOWLEDGE_DIR)
        return {"chunks": [], "version": 1}
    txt_files = list(kp.rglob("*.txt"))
    if not txt_files:
        print("[AVISO] Nenhum .txt em " + KNOWLEDGE_DIR)
        return {"chunks": [], "version": 1}
    print("[INFO] A indexar " + str(len(txt_files)) + " ficheiros...")
    all_chunks = []
    for i, fp in enumerate(txt_files, 1):
        rel = str(fp.relative_to(kp))
        print("  [" + str(i) + "/" + str(len(txt_files)) + "] " + rel)
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if not content.strip():
                continue
            for idx, ch in enumerate(chunk_text(content, CHUNK_SIZE, CHUNK_OVERLAP)):
                if not ch:
                    continue
                emb = ollama_embed(ch)
                if emb:
                    all_chunks.append({"text": ch, "embedding": emb, "source": rel, "chunk_index": idx})
        except Exception as e:
            print("    [AVISO] " + rel + ": " + str(e))
    index = {"chunks": all_chunks, "version": 1, "model": EMBED_MODEL,
             "created_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    save_index(index)
    print("[INFO] Indice guardado (" + str(len(all_chunks)) + " chunks)")
    return index


def get_or_build_index():
    idx = load_index()
    if idx is None:
        print("[INFO] A construir indice novo...")
        return build_index()
    print("[INFO] Indice carregado: " + str(len(idx.get("chunks", []))) + " chunks")
    return idx


def search_index(index, query, top_k=TOP_K):
    if not index or not index.get("chunks"):
        return []
    qe = ollama_embed(query)
    if not qe:
        return []
    results = [{**c, "score": cosine_similarity(qe, c["embedding"])} for c in index["chunks"]]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# CARREGAMENTO
INDEX_DATA = get_or_build_index()

HTML_PATH = os.path.join(SCRIPT_DIR, "index.html")
if os.path.exists(HTML_PATH):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        HTML_CONTENT = f.read()
else:
    HTML_CONTENT = "<html><body><h1>index.html nao encontrado na pasta do script</h1></body></html>"

LOGO_PATH = os.path.join(SCRIPT_DIR, LOGO_FILE)
LOGO_BYTES = b""
print("[DEBUG] SCRIPT_DIR = " + SCRIPT_DIR)
print("[DEBUG] Logo esperado em: " + LOGO_PATH)
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        LOGO_BYTES = f.read()
    print("[DEBUG] Logo OK (" + str(len(LOGO_BYTES)) + " bytes)")
else:
    print("[ERRO] Logo NAO encontrado. Conteudo da pasta:")
    for n in os.listdir(SCRIPT_DIR):
        print("    - " + n)


class RAGHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        elif parsed.path == "/logo.png":
            if LOGO_BYTES:
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(LOGO_BYTES)
            else:
                self.send_error(404)
        elif parsed.path == "/api/status":
            self._json({"total_chunks": len(INDEX_DATA.get("chunks", []))})
        elif parsed.path == "/api/search":
            q = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
            results = search_index(INDEX_DATA, q, TOP_K) if q else []
            self._json({"results": [{"text": r["text"], "source": r["source"], "score": r["score"]} for r in results],
                        "total_chunks": len(INDEX_DATA.get("chunks", []))})
        else:
            self.send_error(404)

    def do_POST(self):
        global INDEX_DATA
        if self.path == "/api/search":
            ln = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(ln).decode("utf-8"))
            except Exception:
                self._json({"results": [], "total_chunks": 0})
                return
            results = search_index(INDEX_DATA, data.get("q", ""), data.get("top_k", TOP_K))
            self._json({"results": [{"text": r["text"], "source": r["source"], "score": r["score"]} for r in results],
                        "total_chunks": len(INDEX_DATA.get("chunks", []))})
        elif self.path == "/api/reindex":
            with INDEX_LOCK:
                INDEX_DATA = build_index()
            self._json({"ok": True, "total_chunks": len(INDEX_DATA.get("chunks", []))})
        else:
            self.send_error(404)

    def _json(self, obj):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    print("=" * 60)
    print("  CONSOLA IA - Rui Miguel Silva")
    print("=" * 60)
    print("  Chunks indexados: " + str(len(INDEX_DATA.get("chunks", []))))
    print("  Logo carregado:   " + ("sim" if LOGO_BYTES else "NAO"))
    print("  Servidor:         http://localhost:" + str(PORT))
    print("")

    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:" + str(PORT))
    threading.Thread(target=open_browser, daemon=True).start()

    with ThreadingHTTPServer(("", PORT), RAGHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Servidor terminado.")


if __name__ == "__main__":
    main()