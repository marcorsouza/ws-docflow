# ws-docflow

Pipeline de extração e validação de dados a partir de PDFs aduaneiros.
Atualmente suporta extração dos seguintes blocos:

- Origem (Unidade Local + Recinto Aduaneiro)
- Destino (Unidade Local + Recinto Aduaneiro)
- Beneficiário (CNPJ/CPF + Nome)
- Transportador (CNPJ/CPF + Nome)
- Tratamento na Origem Totais (Tipo, Valor USD, Valor BRL)

---

## Status
- [x] Estrutura inicial (Poetry, venv, Git)
- [x] Qualidade (ruff/black/mypy/pre-commit)
- [x] Models e validações Pydantic
- [x] Parser de Origem/Destino, Participantes e Totais
- [x] CLI `parse` funcional (JSON)
- [x] Testes unitários cobrindo models, parser e CLI
- [x] Refatoração para Clean Architecture (core/infra/cli)
- [ ] Exportar em múltiplos formatos (`--out`, `--format json|csv`)
- [ ] OCR (opcional, via pytesseract)
- [ ] Integração Contínua (GitHub Actions)

---

## Roadmap / Próximas Etapas

### 1. CLI
- [ ] Adicionar opção `--out <arquivo>` para salvar resultado
- [ ] Suporte a `--format json|csv`
- [ ] Melhorar UX com **rich** (logs, cores, tabela de resultados)
- [ ] Comando `parse-batch <dir>` para processar múltiplos PDFs

### 2. OCR (Opcional)
- [ ] Integrar **pytesseract** para PDFs escaneados
- [ ] Flag `--ocr` para fallback automático

### 3. Testes
- [ ] Fixtures de PDFs reais/mascarados
- [ ] Casos com variação de layout (acentos, hífenes diferentes, linhas em branco)
- [ ] Cobertura com `pytest-cov`

### 4. Integração Contínua
- [ ] Configurar **GitHub Actions** para rodar:
  - Ruff (lint)
  - Black (format)
  - Mypy (tipagem)
  - Pytest (testes + cobertura)

---

## Arquitetura

O projeto segue princípios de **Clean Architecture / Ports & Adapters**, separando camadas:

- **core** → Regras de negócio e contratos
  - `domain/` → modelos (Pydantic)
  - `ports.py` → interfaces (Protocols) para extratores/parsers
  - `use_cases/` → orquestrações (ex.: `ExtractDataUseCase`)
- **infra** → Implementações dos ports
  - `pdf/` → extratores de texto (ex.: `PdfPlumberExtractor`)
  - `parsers/` → parsers específicos (ex.: `BrDtaParser`)
- **cli** → Entrada de linha de comando (Typer)

---

## Roadmap / Próximas Etapas

### 1. CLI
- [ ] Adicionar opção `--out <arquivo>` para salvar resultado
- [ ] Suporte a `--format json|csv`
- [ ] Melhorar UX com **rich** (logs, cores, tabela de resultados)
- [ ] Comando `parse-batch <dir>` para processar múltiplos PDFs

### 2. OCR (Opcional)
- [ ] Integrar **pytesseract** para PDFs escaneados
- [ ] Flag `--ocr` para fallback automático

### 3. Testes
- [ ] Fixtures de PDFs reais/mascarados
- [ ] Casos com variação de layout (acentos, hífenes diferentes, linhas em branco)
- [ ] Cobertura com `pytest-cov`

### 4. Integração Contínua
- [ ] Configurar **GitHub Actions** para rodar:
  - Ruff (lint)
  - Black (format)
  - Mypy (tipagem)
  - Pytest (testes + cobertura)

---


## Como rodar o parser

```bash
poetry run ws-docflow parse caminho/do/arquivo.pdf
```

Saída (exemplo fictício):

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

## Como rodar os testes

```bash
poetry run pytest -v
poetry run pytest --cov=ws_docflow --cov-report=term-missing
```
