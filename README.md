# 📦 ws-docflow
[![CI](https://img.shields.io/github/actions/workflow/status/marcorsouza/ws-docflow/ci.yml?label=CI)](https://github.com/marcorsouza/ws-docflow/actions)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-managed-informational)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Pipeline de **extração e validação de dados a partir de PDFs aduaneiros**, baseado em **Clean Architecture**.
Atualmente suporta extração de:

- 🧾 Declaração (Número sem hífen + Tipo)
- 📌 Situação Atual (bloco de status livre, quando existir)
- 📍 Origem (Unidade Local + Recinto Aduaneiro)
- 🎯 Destino (Unidade Local + Recinto Aduaneiro)
- 🏢 Beneficiário (CNPJ/CPF + Nome)
- 🚢 Transportador (CNPJ/CPF + Nome)
- 💰 Totais de origem (Tipo, Valor USD, Valor BRL)
- 🛣️ Via de Transporte (*RODOVIARIA*, etc.) — **apenas em Extratos**
- 📑 Situação detalhada da Declaração (*solicitada/registrada em + CPF, veículos informados, dossiês vinculados*) — **apenas em Extratos**

---

## ✨ Features

- ✅ Parsers BR-DTA (dois layouts):
  - **Clássico**: “Trânsito Aduaneiro – Extrato da Declaração de Trânsito”
  - **Extrato (Dados Gerais)**: inclui bloco *Via de Transporte/Situação*
- ✅ Fallback automático (Extrato → Clássico) tanto na **CLI** quanto na **API**
- ✅ Models e validações com [Pydantic v2](https://docs.pydantic.dev/)
- ✅ CLI simples via [Typer](https://typer.tiangolo.com/)
- ✅ API REST com [FastAPI](https://fastapi.tiangolo.com/)
- ✅ Lint/format/tipos com `ruff`, `black`, `mypy`, `pre-commit`
- ✅ Testes unitários com `pytest` + cobertura
- ✅ Versionamento semântico com **Commitizen**
- ✅ Integração Contínua com **GitHub Actions**
- 🔜 Exportar múltiplos formatos (`--out`, `--format json|csv`)
- 🔜 OCR opcional (via **pytesseract**)

---

## 🏗 Arquitetura

O projeto segue **Clean Architecture / Ports & Adapters**:

```
src/ws_docflow/
├─ cli/                 # entrada CLI (Typer)
│  └─ app.py
├─ api/                 # entrada API (FastAPI)
│  └─ main.py
├─ core/                # regras de negócio / contratos
│  ├─ domain/           # entidades (Pydantic)
│  ├─ ports.py          # interfaces (extratores/parsers)
│  └─ use_cases/        # orquestrações (ex.: ExtractDataUseCase)
└─ infra/               # implementações concretas
   ├─ pdf/              # extratores (ex.: PdfPlumberExtractor)
   └─ parsers/          # parsers (BrDtaParser, BrDtaExtratoParser)
```

---

## 🚀 Instalação rápida

```bash
# 1. Clonar repositório
git clone https://github.com/marcorsouza/ws-docflow.git
cd ws-docflow

# 2. Configurar Python 3.13 (ou >=3.10,<4.0 se já flexibilizado)
pyenv install 3.13.0
pyenv local 3.13.0

# 3. Instalar dependências
pip install poetry
poetry install

# 4. Testar CLI
poetry run ws-docflow --version
```

> 💡 No Windows, use **PowerShell**.
> 💡 Para OCR futuro, instale também [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).

---

## 🖥️ Como rodar via CLI

```bash
# rodar parser
poetry run ws-docflow parse caminho/do/arquivo.pdf
```

---

## 🖧 API REST

O projeto também expõe uma API com **FastAPI** (`src/ws_docflow/api/main.py`).

### Subir servidor local

```bash
poetry run uvicorn ws_docflow.api.main:app --reload --port 8000
```

### Endpoints

- `POST /api/parse`
  Recebe arquivo PDF (multipart/form-data) → retorna JSON extraído.

  **Exemplo (PowerShell):**
  ```powershell
  $form = @{
    file = Get-Item "C:\caminho\arquivo.pdf"
  }
  Invoke-RestMethod -Method Post `
    -Uri "http://localhost:8000/api/parse" `
    -Form $form
  ```

- `POST /api/parse-b64`
  Recebe JSON com PDF em base64 → retorna JSON extraído.

  **Exemplo de payload:**
  ```json
  {
    "filename": "documento.pdf",
    "content_base64": "JVBERi0xLjQKJc..."
  }
  ```

  **Exemplo (PowerShell):**
  ```powershell
  $b = [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\caminho\arquivo.pdf"))
  $body = @{ filename = "arquivo.pdf"; content_base64 = $b } | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Method POST `
    -Uri "http://localhost:8000/api/parse-b64" `
    -ContentType "application/json" `
    -Body $body
  ```

---

## 🧪 Testes e qualidade

```bash
# rodar testes
poetry run pytest -v
poetry run pytest --cov=ws_docflow --cov-report=term-missing

# rodar lint/format/tipos
poetry run pre-commit run --all-files
```

---

### Exemplo de saída (layout clássico)

```json
{
  "declaracao": {
    "numero": "2401250020",
    "tipo": "DTA - ENTRADA COMUM"
  },
  "situacao_atual": "CONCESSAO em 18/03/2024 às 10:34:55 hs  Por Etapa Automática. automática\nFinalizada em 18/03/2024 às 10:34:55 hs",
  "origem": {
    "unidade_local": {"codigo": "8765432", "descricao": "PORTO DE SANTOS"},
    "recinto_aduaneiro": {"codigo": "1234567", "descricao": "TECON SANTOS TERMINAL DE CONTÊINERES"}
  },
  "destino": {
    "unidade_local": {"codigo": "7654321", "descricao": "PORTO DE ITAJAÍ"},
    "recinto_aduaneiro": {"codigo": "2345678", "descricao": "PORTONAVE TERMINAL DE NAVEGANTES"}
  },
  "beneficiario": {
    "documento": "11.222.333/0001-44",
    "nome": "COMPANHIA BRASILEIRA DE EXPORTAÇÃO LTDA"
  },
  "transportador": {
    "documento": "55.666.777/0001-88",
    "nome": "NAVIOS ATLÂNTICO LOGÍSTICA S/A"
  },
  "totais_origem": {
    "tipo": "ARMAZENAMENTO",
    "valor_total_usd": 45200.75,
    "valor_total_brl": 235000.40
  }
}
```

### Exemplo de saída (layout Extrato — Dados Gerais)

```json
{
  "declaracao": {
    "numero": "2503999080",
    "tipo": "DTA - ENTRADA COMUM"
  },
  "origem": {
    "unidade_local": {"codigo": "1017700", "descricao": "PORTO DE RIO GRANDE"},
    "recinto_aduaneiro": {"codigo": "0301304", "descricao": "INST.PORT.MAR.ALF.USO PUBLICO-TECON RIO GRANDE-RIO GRANDE/RS"}
  },
  "destino": {
    "unidade_local": {"codigo": "1010700", "descricao": "DRF NOVO HAMBURGO"},
    "recinto_aduaneiro": {"codigo": "0403201", "descricao": "EADI-MULTI ARMAZENS LTDA-NOVO HAMBURGO/RS"}
  },
  "beneficiario": {
    "documento": "08.325.039/0001-90",
    "nome": "SS INDUSTRIA METALURGICA DE TELAS LTDA"
  },
  "transportador": {
    "documento": "13.233.554/0001-80",
    "nome": "MULTI EXPRESS BRASIL TRANSPORTES DE CARGAS LTDA"
  },
  "totais_origem": {
    "tipo": "ARMAZENAMENTO",
    "valor_total_usd": 57024.00,
    "valor_total_brl": 308585.37
  },
  "transporte": {"via": "RODOVIARIA"},
  "situacao": {
    "solicitada_em": "2025-08-29T16:30:23-03:00",
    "solicitada_por_cpf": "778.857.910-68",
    "registrada_em": "2025-08-29T16:37:40-03:00",
    "registrada_por_cpf": "778.857.910-68",
    "veiculos_informados": false,
    "dossies_vinculados": ["20250029718711-2"]
  }
}
```


## 📌 Roadmap

- [ ] `--out <arquivo>` e `--format json|csv`
- [ ] `parse-batch <dir>` para múltiplos PDFs
- [ ] Logs coloridos com **rich**
- [ ] OCR com fallback pytesseract
- [ ] Fixtures com PDFs mascarados

---

## 🔗 Contribuição

1. Crie branch a partir de `main`:
   ```bash
   git checkout -b feature/sua-feature
   ```
2. Rode testes e pre-commit:
   ```bash
   poetry run pytest
   poetry run pre-commit run --all-files
   ```
3. Commits no padrão [Conventional Commits](https://www.conventionalcommits.org/)
4. Abra um PR — template disponível em `.github/pull_request_template.md`

---

## 📜 Versionamento

- Versionamento semântico com **Commitizen**
- Histórico no [CHANGELOG.md](CHANGELOG.md)
- Tags no formato `vX.Y.Z`
