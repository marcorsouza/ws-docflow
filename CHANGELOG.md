## v0.8.1 (2025-08-30)

## v0.8.0 (2025-08-29)

## v0.7.0 (2025-08-29)

### Feat

- **logging**: adicionar configuração Rich com emojis e níveis via env

### Fix

- **api**: expor ExtractDataUseCase em main para compatibilidade com testes

## v0.6.0 (2025-08-29)

### Feat

- **api**: adicionar endpoints /api/parse e /api/parse-b64

### Fix

- **types**: definir DocModel Protocol e tipar run() para retornar DocModel
- **types**: normalizar TotaisOrigem.tipo e aceitar Union[str, bytes] no use case/ports

## v0.5.2 (2025-08-29)

### Docs

- **readme**: atualizar instruções com parser de extrato e novos campos

## v0.5.1 (2025-08-29)

### Feat

- **core**: atualizar models com blocos Transporte e Situacao

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
