# CART-001 Adicionar um produto ao carrinho

- **ID:** CART-001
- **Tags:** carrinho, adicionar-um-item
- **Suíte:** carrinho (`tests/robot/carrinho/carrinho.robot`)
- **Regras:** RN-CART-01, RN-CART-02, RN-CART-03, RN-CART-04

## Objetivo
Garantir que um produto adicionado aparece no carrinho com os dados corretos.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto: Sauce Labs Backpack ($ 29.99)

## Passos
1. Abrir "Sauce Labs Backpack".
2. Tocar em "Add to cart".
3. Abrir o carrinho.

## Resultado esperado (critérios verificáveis)
- [ ] Antes de adicionar, o ícone do carrinho não tem contador.
- [ ] Depois de adicionar, o contador mostra 1.          📸 contador_carrinho
- [ ] O carrinho lista o produto com preço $ 29.99 e quantidade 1.
- [ ] Totais: "1 Items" e "$ 29.99".                    📸 item_no_carrinho
