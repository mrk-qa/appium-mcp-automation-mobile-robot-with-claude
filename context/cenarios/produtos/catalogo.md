# PROD-001 Catálogo exibe os produtos com nome e preço

- **ID:** PROD-001
- **Tags:** produtos, listagem-de-produtos
- **Suíte:** produtos (`tests/robot/produtos/produtos.robot`)

## Objetivo
Garantir que o catálogo lista os produtos com nome e preço corretos.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produtos: Backpack ($ 29.99), Bike Light ($ 9.99), Onesie ($ 7.99)

## Passos
1. Na tela Products, localizar "Sauce Labs Backpack".            📸 catalogo
2. Rolar até "Sauce Labs Bike Light" e "Sauce Labs Onesie".     📸 catalogo_rolado

## Resultado esperado (critérios verificáveis)
- [ ] O título da tela é "Products".
- [ ] Cada produto aparece com o preço esperado.
