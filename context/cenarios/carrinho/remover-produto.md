# CART-003 Remover produto do carrinho

- **ID:** CART-003
- **Tags:** carrinho, remover-item
- **Suíte:** carrinho (`tests/robot/carrinho/carrinho.robot`)
- **Regras:** RN-CART-05

## Objetivo
Garantir que remover o único item esvazia o carrinho.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto: Sauce Labs Backpack ($ 29.99)

## Passos
1. Adicionar "Sauce Labs Backpack" e abrir o carrinho.          📸 carrinho_com_item
2. Tocar em "Remove Item".

## Resultado esperado (critérios verificáveis)
- [ ] O produto não aparece mais no carrinho.
- [ ] O botão de checkout e o contador do carrinho somem.   📸 carrinho_vazio
