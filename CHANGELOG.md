## Unreleased

### Refactor

- **arch**: aplicar clean architecture (core/infra/cli) e ajustar imports/entrypoint

## v0.3.1 (2025-08-29)

### Feat

- **core**: adicionar participantes (beneficiário/transportador) e totais na origem (tipo, USD, BRL)
- **core**: adicionar models, cli skeleton e testes iniciais

### Fix

- **cli**: serializar Decimal no JSON (model_dump(mode='json'))
- **parser**: ancorar regex por linha (MULTILINE) e tolerar espaços/linhas em branco
