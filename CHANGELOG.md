## v0.2.0 (2025-08-28)

### Feat

- **core**: adicionar participantes (beneficiário/transportador) e totais na origem (tipo, USD, BRL)
- **core**: adicionar models, cli skeleton e testes iniciais

### Fix

- **cli**: serializar Decimal no JSON (model_dump(mode='json'))
- **parser**: ancorar regex por linha (MULTILINE) e tolerar espaços/linhas em branco
