# Regras de negócio — Produtos (catálogo, detalhes e ordenação)

Regras do **app** que os cenários de `context/cenarios/produtos/` verificam. Mantidas pela skill
`product-owner` (formato e ciclo de vida em `.claude/skills/product-owner/SKILL.md`). Cada cenário cita as
regras que cobre em `- **Regras:**`; a matriz regra × cenário × teste sai da skill `analista-de-testes`.

**Status:** `vigente` (confirmada por evidência ou decisão do usuário) · `a confirmar` (falta decisão do
usuário; não vira critério) · `divergente` (o app contraria a regra: ver `limitacoes-conhecidas.md`) · `obsoleta`.

### RN-PROD-01 Catálogo lista cada produto com nome e preço
- **Regra:** A tela de catálogo tem o título "Products" e cada card mostra o nome do produto e o preço no formato `$ <valor com 2 casas>` (ex.: "$ 29.99").
- **Fonte:** observada no app em 2026-11-07 (`comportamentos-observados.md` › Catálogo); validada no PROD-001.
- **Status:** vigente

### RN-PROD-02 Detalhes do produto mostram nome, preço e quantidade inicial 1
- **Regra:** Tocar na imagem de um produto do catálogo abre os detalhes com o nome, o preço igual ao do catálogo, a quantidade inicial 1 e o botão "Add to cart".
- **Fonte:** observada em 2026-11-07; validada no PROD-002.
- **Status:** vigente

### RN-PROD-03 Ordenação por preço crescente
- **Regra:** Ao escolher "Price - Ascending", o catálogo exibe os produtos do menor para o maior preço; o 1º é "Sauce Labs Onesie" ($ 7.99) e o ícone de ordenação mostra "↑$".
- **Fonte:** observada em 2026-11-07; validada no PROD-003 (`tests/reports/screenshots/PROD-003/01_ordenado_preco_crescente.png`); o ícone "↑$" só aparece na evidência, sem asserção.
- **Status:** vigente

### RN-PROD-04 Ordem padrão do catálogo é nome crescente
- **Regra:** Sem escolher ordenação, o catálogo vem em ordem de nome crescente e o ícone de ordenação mostra "↑AB".
- **Fonte:** observada em 2026-11-07 (`comportamentos-observados.md` › Catálogo); sem cenário.
- **Status:** vigente

### RN-PROD-05 Ordenação se mantém ao voltar dos detalhes
- **Regra:** Depois de ordenar, abrir um produto e voltar, o catálogo mantém a ordenação escolhida.
- **Fonte:** observada em 2026-11-07 (`comportamentos-observados.md` › Catálogo); sem cenário.
- **Status:** vigente

### RN-PROD-06 Demais opções de ordenação
- **Regra:** O menu de ordenação oferece também "Name - Ascending", "Name - Descending" e "Price - Descending"; cada uma ordena pelo critério e sentido do nome.
- **Fonte:** as opções aparecem no menu (observado em 2026-11-07); o resultado de cada uma **não** foi verificado.
- **Status:** a confirmar
