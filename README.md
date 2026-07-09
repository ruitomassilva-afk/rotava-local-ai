# RotaVA

RotaVA é um assistente local de Inteligência Artificial com suporte para Retrieval-Augmented Generation (RAG), desenvolvido em Python e com uma interface Web própria.

O projeto indexa documentos de texto, gera embeddings através do Ollama e permite efetuar pesquisa semântica sobre a base de conhecimento.

## Funcionalidades

- Interface Web para interação com o assistente.
- Servidor HTTP multithread.
- API REST para pesquisa e estado do sistema.
- Indexação automática de documentos `.txt`.
- Divisão de documentos em chunks.
- Geração de embeddings através do Ollama.
- Pesquisa semântica utilizando similaridade por cosseno.
- Reindexação da base de conhecimento.
- Histórico de conversas armazenado localmente.
- Exportação de conversas em formato Markdown.

## Tecnologias

- Python
- HTML5
- CSS3
- JavaScript
- Ollama
- ThreadingHTTPServer
- JSON

## Estrutura

```
.
├── rag_server.py
├── index.html
├── rag_index.json
└── README.md
```
## Configuração

O servidor utiliza os seguintes parâmetros por defeito:
Parâmetro	Valor
Porta	8080
Embedding Model	nomic-embed-text
Chat Model	qwen3:4b
Execução
bash
Copy
python rag_server.py
Depois abrir:

http://localhost:8080
Arquitetura
Documentos TXT
       │
       ▼
Chunking
       │
       ▼
Embeddings (Ollama)
       │
       ▼
Índice JSON
       │
       ▼
Pesquisa Semântica
       │
       ▼
Interface Web
Autor
Rui Miguel Silva


---

### `.gitignore`

```gitignore
__pycache__/
*.pyc

rag_index.json

.vscode/
.idea/

Thumbs.db
.DS_Store
```

---

## Configuração

O servidor utiliza os seguintes parâmetros por defeito:

Parâmetro	Valor
Porta	8080
Embedding Model	nomic-embed-text
Chat Model	qwen3:4b
Execução
bash
Copy
python rag_server.py
Depois abrir:

http://localhost:8080
Arquitetura
Documentos TXT
       │
       ▼
Chunking
       │
       ▼
Embeddings (Ollama)
       │
       ▼
Índice JSON
       │
       ▼
Pesquisa Semântica
       │
       ▼
Interface Web
Autor
Rui Miguel Silva


---

### `.gitignore`

```gitignore
__pycache__/
*.pyc

rag_index.json

.vscode/
.idea/

Thumbs.db
.DS_Store
```

---
