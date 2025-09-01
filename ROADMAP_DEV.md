# 🧭 Roadmap de Engenharia (DEV)

> Documento vivo com prioridades técnicas para evolução do **ws-docflow**. Itens estão em formato de checklist para facilitar acompanhamento.

---

## 🎯 Objetivos estratégicos
- [ ] Garantir **confiabilidade** na extração (testes, contratos e validações)
- [ ] Aumentar **observabilidade** (logs estruturados, métricas, tracing)
- [ ] Facilitar **evolução** (arquitetura plugável para parsers e extratores)
- [ ] Fortalecer **segurança** (dependências, secrets, dados sensíveis)
- [ ] Melhorar **DX** (dev experience): setup rápido, docs claras, CI veloz

---

## ✅ Qualidade & Padrões
- [ ] Meta de cobertura de testes ≥ **85%** (gate no CI)
- [ ] `mypy --strict` em módulos **core** (ampliar gradualmente para o repo inteiro)
- [ ] `ruff`, `black`, `isort` e `pydocstyle` via **pre-commit**
- [ ] Docstrings padrão **PEP 257** em `core/use_cases` e `core/domain`
- [ ] Tratamento de exceções padronizado com hierarquia `DocflowError`
- [ ] ADRs (Architecture Decision Records) para decisões relevantes
- [ ] **Mutation testing** (ex.: `mutmut`, `cosmic-ray`)
- [ ] **Property-based testing** (`hypothesis`) para parsers e extratores
- [ ] **Coverage reports em PR** (comentários automáticos no GitHub)

---

## 🔐 Segurança
- [ ] **Dependabot** (GitHub) para atualizar libs (poetry)
- [ ] **CodeQL** (workflow) e **bandit** (pre-commit) para SAST
- [ ] Rotação de **secrets** (GH Actions) e uso de `secrets.*` em workflows
- [ ] Política de **least privilege** para tokens de CI
- [ ] Scrubber de dados sensíveis nos logs (CNPJ/CPF → mascarado)
- [ ] **Secrets scanning** (ex.: `trufflehog`, GitHub Secret Scanning)
- [ ] **Threat modeling**: abusos possíveis (PDF malicioso, DoS via PDFs grandes)

---

## 🧪 Testes
- [ ] Testes unitários de **parsers** com **fixtures de PDFs mascarados**
- [ ] Testes parametrizados (`pytest.mark.parametrize`) cobrindo variações de layout
- [ ] Testes de **contratos** (Pydantic) validando schema de saída
- [ ] Testes de **integração** (CLI + API) e de **erro** (PDF inválido, base64 inválido)
- [ ] Snapshot tests do JSON de saída (normalizar campos não determinísticos)
- [ ] Mocks de extratores (PdfPlumberExtractor)
- [ ] **Contract tests** nos endpoints API com JSON Schema

---

## 🧱 Arquitetura
- [ ] **Factory** de parsers (registry) + seleção por heurística/score
- [ ] **Contracts** estáveis em `core/ports.py` com Protocols (typing)
- [ ] **Boundary** entre `core` e `infra` reforçado (sem dependências invertidas)
- [ ] Camada de **normalização** (post-processing)
- [ ] Planejar **OCR fallback** como extrator plugável (`TesseractExtractor`)
- [ ] Suporte a **múltiplos layouts** BR e futura extensão LATAM
- [ ] **Feature flags** para habilitar/desabilitar parsers em runtime

---

## 📈 Observabilidade
- [ ] Logs **estruturados** (JSON) com `logger.bind()`
- [ ] **Correlation/Request ID** por execução (CLI e API)
- [ ] **Métricas** (tempo médio de parsing, taxa de erro, OCR fallback)
- [ ] **Tracing** (OpenTelemetry)
- [ ] Export de métricas via `/metrics` (Prometheus)
- [ ] **Healthcheck endpoints** (liveness/readiness)
- [ ] **Tracing sample** no CI (coletar spans)

---

## ⚡ Performance
- [ ] Benchmark por tipo de PDF; meta p95 < **1.5s**
- [ ] **Cache** por hash SHA-256 do PDF
- [ ] Paralelização no `parse-batch`
- [ ] Short-circuit no parsing
- [ ] **Profiling** (cProfile/py-spy) em regex/parsers
- [ ] **Benchmarks em batch** (ex.: 100 PDFs)

---

## 🚢 Release, Versionamento & CI/CD
- [ ] Matriz do CI: Python 3.10 → 3.13
- [ ] Workflow: lint → build → tests → coverage gate → package
- [ ] `cz bump --changelog` automatizado
- [ ] Publicar Docker image no GHCR
- [ ] Release notes automatizadas
- [ ] **Coverage gate no CI** (`--cov-fail-under=85`)
- [ ] **Diff coverage ≥90%** com `diff-cover`
- [ ] **Cache de deps** Poetry no GitHub Actions

---

## 🧰 DX (Developer Experience)
- [ ] `make`/`taskfile` com comandos frequentes
- [ ] Script de **bootstrap** (pyenv, poetry, hooks, pre-commit)
- [ ] Ambiente **DevContainer** (VS Code)
- [ ] Templates de PR/Issue mais prescritivos
- [ ] **Git hooks client-side** (bloquear commit na main)

---

## 📚 Documentação
- [ ] **MkDocs** (Material) + GitHub Pages
- [ ] Guia de contribuição detalhado
- [ ] Especificação de contratos (JSON Schema)
- [ ] Guia de criação de parsers
- [ ] Tabela de erros (códigos + causas)
- [ ] **Tutorial end-to-end**: PDF → JSON → CSV

---

## 🧾 Dados & Compliance
- [ ] Política de retenção de logs/resultados
- [ ] Mascaramento de PII (CNPJs fictícios garantidos)
- [ ] Conformidade LGPD
- [ ] Política de acesso a artefatos CI

---

## 🔎 Estratégia de Parsing
- [ ] Regex **line-based** tolerante a acentos/linhas extras
- [ ] Normalização de números (Decimal) e datas (tz-aware)
- [ ] Catálogo de **amostras** com metadados
- [ ] Heurística Extrato vs Clássico
- [ ] **Property-based tests** de parsing (Hypothesis)

---

## 🌐 API & CLI
- [ ] CLI: `--out <arquivo>`, `--format`, `parse-batch`
- [ ] API: endpoint batch, `/health`, `/metrics`
- [ ] Retorno parcial (`?fields=origem,destino`)
- [ ] Limites configuráveis (tamanho máx., timeout)

---

## 📦 Empacotamento & Distribuição
- [ ] Publicar no PyPI (privado/público)
- [ ] Assinatura/Reprodutibilidade (`pip hash`)
- [ ] `poetry export` para `requirements.txt`

---

## 🌐 Futuro SaaS / Expansão
- [ ] Multi-tenant (isolamento de configs)
- [ ] Dashboard Web (UI upload/preview JSON)
- [ ] Suporte LATAM (Chile, Argentina)
- [ ] Billing hooks (contagem de PDFs processados)

---

## 🗺️ Backlog de Inovação
- [ ] Plugin de validação externa (CNPJs em bases públicas)
- [ ] Webhook p/ integração com sistemas terceiros
- [ ] Suporte a XLSX/Parquet (data pipelines)
- [ ] Integração com GitHub Projects (issues ↔ roadmap)
- [ ] **Mutation testing** em CI noturno
- [ ] **Hypothesis fuzzing** para regressões
- [ ] **Threat modeling** documentado no repo

---

## 📌 Priorização imediata (próximo ciclo)
1) Observabilidade mínima (logs estruturados + correlation id)
2) Testes de contratos + fixtures mascaradas
3) CLI `--out`/`--format` e `parse-batch`
4) CI com matriz 3.10→3.13 + coverage gate/diff-cover
5) Publicação de Docker image no GHCR
