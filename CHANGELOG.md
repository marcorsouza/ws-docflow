## v0.5.0 (2025-08-29)

### Fix

- **core**: alinhar contratos e defaults p/ mypy (extract, DeclaracaoInfo)
- **ci**: corrigir indentação e sintaxe dos workflows YAML

## v0.4.1 (2025-08-29)

### Fix

- **pdf**: implementar PdfPlumberExtractor.extract_text para a CLI

## v0.4.0 (2025-08-29)

### Feat

- **parser**: extrair declaracao.numero, declaracao.tipo e situacao_atual

## v0.3.1 (2025-08-29)

### Refactor

- **arch**: aplicar clean architecture (core/infra/cli) e ajustar imports/entrypoint

## v0.3.0 (2025-08-29)

### Feat

- **core**: adicionar participantes (beneficiário/transportador) e totais na origem (tipo, USD, BRL)
- **core**: adicionar models, cli skeleton e testes iniciais

### Fix

- **cli**: serializar Decimal no JSON (model_dump(mode='json'))
- **parser**: ancorar regex por linha (MULTILINE) e tolerar espaços/linhas em branco
