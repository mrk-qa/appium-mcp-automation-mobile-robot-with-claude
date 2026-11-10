# Regras de negócio — Compra (checkout)

Regras do **app** que os cenários de `context/cenarios/compra/` verificam. Mantidas pela skill
`product-owner` (formato e ciclo de vida em `.claude/skills/product-owner/SKILL.md`). Cada cenário cita as
regras que cobre em `- **Regras:**`; a matriz regra × cenário × teste sai da skill `analista-de-testes`.

**Status:** `vigente` · `a confirmar` · `divergente` · `obsoleta` (definições em `produtos.md`).

### RN-BUY-01 Etapas do checkout
- **Regra:** O checkout segue Carrinho → Endereço ("Enter a shipping address") → Pagamento ("Enter a payment method") → Revisão ("Review your order") → Conclusão ("Checkout Complete").
- **Fonte:** observada em 2026-11-07; validada no BUY-001.
- **Status:** vigente

### RN-BUY-02 Revisão mostra itens, entrega e titular do cartão
- **Regra:** A revisão lista cada produto com o preço, o nome e o endereço de entrega, "<país>, <CEP>" e o titular do cartão informados.
- **Fonte:** observada em 2026-11-07; validada no BUY-001.
- **Status:** vigente

### RN-BUY-03 Total do pedido = itens + frete fixo de $ 5.99
- **Regra:** Na revisão, a quantidade aparece como "<n> Items" e o total é a soma dos itens mais o frete fixo de $ 5.99 (ex.: $ 29.99 → $ 35.98).
- **Fonte:** observada em 2026-11-07; validada no BUY-001. Frete com vários itens: BUY-002 (SKIP por defeito conhecido).
- **Status:** vigente

### RN-BUY-04 Confirmação do pedido
- **Regra:** "Place Order" abre a tela "Checkout Complete" com o texto "Thank you for your order" e o botão "Continue Shopping".
- **Fonte:** observada em 2026-11-07; validada no BUY-001.
- **Status:** vigente

### RN-BUY-05 Depois da compra o carrinho fica vazio
- **Regra:** "Continue Shopping" volta ao catálogo com o carrinho esvaziado (sem contador no cabeçalho).
- **Fonte:** observada em 2026-11-07; validada no BUY-001.
- **Status:** vigente

### RN-BUY-06 Validade do cartão formatada como MM/AA
- **Regra:** Digitar a validade só com números (MMAA) faz o app exibir "MM/AA" no campo.
- **Fonte:** observada em 2026-11-07 (`comportamentos-observados.md` › Checkout); sem cenário.
- **Status:** vigente
