# CART-004 Carrinho vazio exibe a mensagem de carrinho sem itens

- **ID:** CART-004
- **Tags:** carrinho, carrinho-vazio
- **Status:** automatizado em 2026-11-07 (`tests/robot/carrinho/carrinho.robot`)
- **Suíte:** carrinho (`tests/robot/carrinho/carrinho.robot`)

## Objetivo
Garantir que o carrinho sem itens orienta o usuário a voltar a comprar.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto: Sauce Labs Backpack ($ 29.99)

## Passos
1. Adicionar "Sauce Labs Backpack" e abrir o carrinho.
2. Tocar em "Remove Item".                                   📸 carrinho_sem_itens
3. Tocar em "Go Shopping".                                   📸 catalogo

## Resultado esperado (critérios verificáveis)
- [ ] O título "No Items" é exibido.
- [ ] O texto "Oh no! Your cart is empty. Fill it up with swag to complete your purchase." é exibido.
- [ ] O botão "Go Shopping" é exibido e leva à tela "Products".
- [ ] De volta ao catálogo, o ícone do carrinho não mostra contador.

## Origem
Proposto pela avaliação de QA de 2026-11-07: a tela foi vista em
`tests/reports/screenshots/CART-003/02_carrinho_vazio.png`, mas o CART-003 só valida a ausência do item.
Seletores mapeados com o Appium MCP em 2026-11-07: `noItemTitleTV`, mensagem dentro de `cartInfoLL`, `shoppingBt`.
