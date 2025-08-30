# 🧭 Roadmap de Engenharia (DEV)

> Documento vivo com prioridades técnicas para evolução do
> **ws-docflow**. Itens estão em formato de checklist para facilitar
> acompanhamento.

------------------------------------------------------------------------

## 🎯 Objetivos estratégicos

-   [ ] Garantir **confiabilidade** na extração (testes, contratos e
    validações)
-   [ ] Aumentar **observabilidade** (logs estruturados, métricas,
    tracing)
-   [ ] Facilitar **evolução** (arquitetura plugável para parsers e
    extratores)
-   [ ] Fortalecer **segurança** (dependências, secrets, dados
    sensíveis)
-   [ ] Melhorar **DX** (dev experience): setup rápido, docs claras, CI
    veloz

------------------------------------------------------------------------

## ✅ Qualidade & Padrões

-   [ ] Meta de cobertura de testes ≥ **85%** (gate no CI)
-   [ ] `mypy --strict` em módulos **core** (ampliar gradualmente para o
    repo inteiro)
-   [ ] `ruff`, `black`, `isort` e `pydocstyle` via **pre-commit**
-   [ ] Docstrings padrão **PEP 257** em `core/use_cases` e
    `core/domain`
-   [ ] Tratamento de exceções padronizado com hierarquia `DocflowError`
-   [ ] ADRs (Architecture Decision Records) para decisões relevantes

------------------------------------------------------------------------

## 🔐 Segurança

-   [ ] **Dependabot** (GitHub) para atualizar libs (poetry)
-   [ ] **CodeQL** (workflow) e **bandit** (pre-commit) para SAST
-   [ ] Rotação de **secrets** (GH Actions) e uso de `secrets.*` em
    workflows
-   [ ] Política de **least privilege** para tokens de CI
-   [ ] Scrubber de dados sensíveis nos logs (CNPJ/CPF → mascarado)

------------------------------------------------------------------------

## 🧪 Testes

-   [ ] Testes unitários de **parsers** com **fixtures de PDFs
    mascarados**
-   [ ] Testes parametrizados (`pytest.mark.parametrize`) cobrindo
    variações de layout
-   [ ] Testes de **contratos** (Pydantic) validando schema de saída
-   [ ] Testes de **integração** (CLI + API) e de **erro** (PDF
    inválido, base64 inválido)
-   [ ] Snapshot tests do JSON de saída (com campos não determinísticos
    normalizados)
-   [ ] Mocks de extratores (ex.: `PdfPlumberExtractor`) para isolar
    parsing

------------------------------------------------------------------------

## 🧱 Arquitetura

-   [ ] **Factory** de parsers (registry) + seleção por heurística/score
-   [ ] **Contracts** estáveis em `core/ports.py` com Protocols (typing)
-   [ ] **Boundary** entre `core` e `infra` reforçado (sem dependências
    invertidas)
-   [ ] Camada de **normalização** (post-processing) para padronizar
    datas/valores
-   [ ] Planejar **OCR fallback** como extrator plugável
    (`TesseractExtractor`)
-   [ ] Suporte a **múltiplos layouts** BR e futura extensão LATAM

------------------------------------------------------------------------

## 📈 Observabilidade

-   [ ] Logs **estruturados** (JSON) com `logger.bind()` (rich/loguru ou
    stdlib com extras)
-   [ ] **Correlation/Request ID** por execução (CLI e API)
-   [ ] **Métricas** (tempo médio de parsing, PDFs/min, tamanho médio,
    taxa de erro)
-   [ ] **Tracing** (OpenTelemetry) quando em ambiente com collector
-   [ ] Export de métricas via **/metrics** (Prometheus) na API

------------------------------------------------------------------------

## ⚡ Performance

-   [ ] Benchmark por tipo de PDF; meta de p95 \< **1.5s** em PDFs com
    texto
-   [ ] **Cache** por hash SHA-256 do conteúdo (resultado de parsing)
-   [ ] Paralelização opcional no **parse-batch** (pool de processos)
-   [ ] Short-circuit: parar cedo quando bloco alvo já foi extraído

------------------------------------------------------------------------

## 🚢 Release, Versionamento & CI/CD

-   [ ] Matriz do CI: Python **3.10 → 3.13**
-   [ ] Workflow: lint → build → tests → coverage gate → package
-   [ ] `cz bump --changelog` automatizado via tag `vX.Y.Z`
-   [ ] Publicar **Docker image** no GHCR
    (`ghcr.io/<org>/ws-docflow:<tag>`)
-   [ ] Release notes automatizadas a partir do CHANGELOG

------------------------------------------------------------------------

## 🧰 DX (Developer Experience)

-   [ ] `make`/`taskfile` com comandos frequentes (lint, test, run, dev)
-   [ ] Script de **bootstrap** (instala pyenv, poetry, hooks,
    pre-commit)
-   [ ] Ambiente **DevContainer** (VS Code) com Python 3.13 + Poetry +
    deps
-   [ ] Templates de PR e Issue (bug/feature) mais prescritivos

------------------------------------------------------------------------

## 📚 Documentação

-   [ ] **MkDocs** (Material) com publicação no GitHub Pages
-   [ ] Guia de **contribuição** detalhando fluxo de branches e commits
-   [ ] Especificação de **contratos de saída** (JSON Schema + exemplos)
-   [ ] Guia de **parsers**: como criar um novo e registrá-lo
-   [ ] Tabela de **erros** (códigos + causas + como resolver)

------------------------------------------------------------------------

## 🧾 Dados & Compliance

-   [ ] Política de retenção (quanto tempo guardar logs/resultados)
-   [ ] **Mascaramento** de PII (CNPJ/CPF) e política de acesso a
    artefatos de CI
-   [ ] Conformidade com **LGPD** (minimização e finalidade)

------------------------------------------------------------------------

## 🔎 Estratégia de Parsing

-   [ ] Regex **line-based** tolerante a variações (acentos/linhas em
    branco)
-   [ ] Normalização de números (Decimal) e datas (timezone-aware)
-   [ ] Catálogo de **amostras** com metadados (layout, tamanho, fonte)
-   [ ] Heurística para detectar **Extrato vs Clássico** e escolher
    parser

------------------------------------------------------------------------

## 🌐 API & CLI

-   [ ] CLI: `--out <arquivo>` e `--format json|csv`;
    `parse-batch <dir>`
-   [ ] API: endpoint **batch** e **/health**/**/metrics**
-   [ ] Retorno **parcial** por query param (`?fields=origem,destino`)
-   [ ] Limites configuráveis (tamanho máx. PDF, timeout)

------------------------------------------------------------------------

## 📦 Empacotamento & Distribuição

-   [ ] Publicar pacote no **PyPI** (opcional, privado ou público)
-   [ ] Assinatura/Reprodutibilidade (hash de build;
    `pip hash`/`poetry export`)
-   [ ] `poetry export` para **requirements.txt** (ambientes sem poetry)

------------------------------------------------------------------------

## 🗺️ Backlog de ideias

-   [ ] Plugin **validador externo** (ex.: checagem CNPJ em serviços
    públicos)
-   [ ] UI simples (upload, preview do JSON, download CSV)
-   [ ] Modo **dry-run** (mostrar blocos reconhecidos sem persistir)
-   [ ] Webhook para **integração** com sistemas terceiros
-   [ ] Suporte a **XLSX** (export) e **Parquet** (data pipelines)

------------------------------------------------------------------------

## 📌 Priorização imediata (próximo ciclo)

1)  Observabilidade mínima (logs estruturados + correlation id)
2)  Testes de contratos + fixtures mascaradas
3)  CLI `--out`/`--format` e `parse-batch`
4)  CI com matriz 3.10→3.13 + coverage gate
5)  Publicação de Docker image no GHCR
