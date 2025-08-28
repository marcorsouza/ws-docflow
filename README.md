# ws-docflow

Pipeline de extração e validação de dados a partir de PDFs (Origem/Destino, Unidade Local, Recinto Aduaneiro).

## Status
- [x] Estrutura inicial (Poetry, venv, Git)
- [x] Qualidade (ruff/black/mypy/pre-commit)
- [ ] CLI e parsers
- [ ] OCR (opcional)

---

## Roadmap / Próximas Etapas

### 1. Testes First
- [ ] Configurar **pytest** com fixtures de PDFs de exemplo
- [ ] Criar testes unitários para:
- [ ] Extração de texto cru de PDF (`pdfplumber`)
- [ ] Regex para Origem/Destino, Unidade Local, Recinto Aduaneiro
- [ ] Modelo Pydantic de validação dos campos
- [ ] Configurar `pytest-cov` para medir cobertura

### 2. Parser (Extração de Dados)
- [ ] Implementar função de leitura de PDF → texto
- [ ] Implementar função de parsing dos blocos **Origem** e **Destino**
- [ ] Validar dados via modelos Pydantic
- [ ] Exportar resultado em JSON

### 3. CLI (Typer)
- [ ] Criar comando `parse <arquivo.pdf>`
- [ ] Opção `--out json/csv` para salvar saída
- [ ] Logs coloridos com **rich**

### 4. OCR (Opcional)
- [ ] Integrar **pytesseract** para PDFs escaneados
- [ ] Adicionar flag `--ocr` na CLI

### 5. Integração Contínua
- [ ] Configurar **GitHub Actions** para rodar:
  - Ruff (lint)
  - Black (format)
  - Mypy (tipagem)
  - Pytest (testes + cobertura)

---

## Como rodar os testes
```bash
poetry run pytest -v
poetry run pytest --cov=ws_docflow --cov-report=term-missing
