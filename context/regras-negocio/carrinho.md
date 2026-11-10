# Regras de negócio — Carrinho

Regras do **app** que os cenários de `context/cenarios/carrinho/` verificam. Mantidas pela skill
`product-owner` (formato e ciclo de vida em `.claude/skills/product-owner/SKILL.md`). Cada cenário cita as
regras que cobre em `- **Regras:**`; a matriz regra × cenário × teste sai da skill `analista-de-testes`.

**Status:** `vigente` · `a confirmar` · `divergente` · `obsoleta` (definições em `produtos.md`).

### RN-CART-01 Carrinho vazio não mostra contador
- **Regra:** Com o carrinho vazio, o ícone do carrinho no cabeçalho não exibe contador.
- **Fonte:** observada em 2026-11-07; validada no CART-001 e no CART-004.
- **Status:** vigente

### RN-CART-02 Cada "Add to cart" soma 1 ao contador
- **Regra:** Cada toque em "Add to cart" soma 1 ao contador do ícone do carrinho, que mostra a quantidade total de itens.
- **Fonte:** observada em 2026-11-07; validada no CART-001 (1 item). Com 2 produtos diferentes: CART-002 (SKIP por defeito conhecido).
- **Status:** vigente

### RN-CART-03 Carrinho lista cada produto com nome, preço e quantidade
- **Regra:** A tela "My Cart" lista cada produto adicionado com o nome, o preço unitário e a quantidade.
- **Fonte:** observada em 2026-11-07; validada no CART-001 e no CART-003.
- **Status:** vigente

### RN-CART-04 Totais do carrinho
- **Regra:** O carrinho mostra a quantidade de itens no formato "<n> Items" (inclusive "1 Items") e o total igual à soma de preço × quantidade de cada item, sem frete.
- **Fonte:** observada em 2026-11-07; validada no CART-001.
- **Status:** vigente

### RN-CART-05 Remover o único item esvazia o carrinho
- **Regra:** "Remove Item" retira o produto do carrinho; sem itens, somem o botão "Proceed To Checkout" e o contador do cabeçalho.
- **Fonte:** observada em 2026-11-07; validada no CART-003.
- **Status:** vigente

### RN-CART-06 Carrinho sem itens orienta a voltar às compras
- **Regra:** O carrinho sem itens mostra o título "No Items", o texto "Oh no! Your cart is empty. Fill it up with swag to complete your purchase." e o botão "Go Shopping", que leva ao catálogo ("Products").
- **Fonte:** observada em 2026-11-07; validada no CART-004.
- **Status:** vigente

### RN-CART-07 Checkout exige login
- **Regra:** Deslogado, "Proceed To Checkout" leva à tela de Login em vez do endereço de entrega.
- **Fonte:** observada em 2026-11-07 (`navegacao.md` › Transições validadas). Sem cenário: todo teste começa autenticado (`Iniciar App Autenticado`), então cobrir esta regra exige decidir um setup sem login.
- **Status:** vigente
