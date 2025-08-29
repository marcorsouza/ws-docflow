# 📦 ws-docflow

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)  
[![Poetry](https://img.shields.io/badge/Poetry-managed-informational)](https://python-poetry.org/)  
[![CI](https://img.shields.io/github/actions/workflow/status/marcorsouza/ws-docflow/ci.yml?label=CI)](https://github.com/marcorsouza/ws-docflow/actions)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Pipeline de **extração e validação de dados a partir de PDFs aduaneiros**, baseado em **Clean Architecture**.  
Atualmente suporta extração de:

- 📍 Origem (Unidade Local + Recinto Aduaneiro)  
- 🎯 Destino (Unidade Local + Recinto Aduaneiro)  
- 🏢 Beneficiário (CNPJ/CPF + Nome)  
- 🚢 Transportador (CNPJ/CPF + Nome)  
- 💰 Totais de origem (Tipo, Valor USD, Valor BRL)  

---

## ✨ Features

- ✅ Parser BR-DTA baseado em **regex line-based**  
- ✅ CLI simples via [Typer](https://typer.tiangolo.com/)  
- ✅ Models e validações com [Pydantic v2](https://docs.pydantic.dev/)  
- ✅ Lint/format/tipos com `ruff`, `black`, `mypy`, `pre-commit`  
- ✅ Testes unitários com `pytest` + cobertura  
- ✅ Versionamento semântico com **Commitizen**  
- 🔜 Exportar múltiplos formatos (`--out`, `--format json|csv`)  
- 🔜 OCR opcional (via **pytesseract**)  
- 🔜 Integração Contínua com **GitHub Actions**  

---

## 🏗 Arquitetura

O projeto segue **Clean Architecture / Ports & Adapters**:

```
src/ws_docflow/
├─ cli/                 # entrada CLI (Typer)
│  └─ app.py
├─ core/                # regras de negócio / contratos
│  ├─ domain/           # entidades (Pydantic)
│  ├─ ports.py          # interfaces (extratores/parsers)
│  └─ use_cases/        # orquestrações (ex.: ExtractDataUseCase)
└─ infra/               # implementações concretas
   ├─ pdf/              # extratores (ex.: PdfPlumberExtractor)
   └─ parsers/          # parsers (ex.: BrDtaParser)
```

---

## 🚀 Instalação rápida

```bash
# 1. Clonar repositório
git clone https://github.com/marcorsouza/ws-docflow.git
cd ws-docflow

# 2. Configurar Python 3.13
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

## 🖥️ Como rodar

```bash
# rodar parser
poetry run ws-docflow parse caminho/do/arquivo.pdf
```

Exemplo de saída:

```json
{
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

## 📌 Roadmap

- [ ] `--out <arquivo>` e `--format json|csv`  
- [ ] `parse-batch <dir>` para múltiplos PDFs  
- [ ] Logs coloridos com **rich**  
- [ ] OCR com fallback pytesseract  
- [ ] Fixtures com PDFs mascarados  
- [ ] CI (Ruff, Black, Mypy, Pytest, cobertura)  

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

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT.  
Veja [LICENSE](LICENSE) para mais detalhes.