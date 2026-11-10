# PROD-002 Detalhes do produto exibem nome, preço e quantidade

- **ID:** PROD-002
- **Tags:** produtos, detalhes-do-produto
- **Suíte:** produtos (`tests/robot/produtos/produtos.robot`)
- **Regras:** RN-PROD-02

## Objetivo
Garantir que a tela de detalhes mostra os dados do produto selecionado.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto: Sauce Labs Backpack ($ 29.99)

## Passos
1. Tocar no produto "Sauce Labs Backpack" no catálogo.

## Resultado esperado (critérios verificáveis)
- [ ] Nome "Sauce Labs Backpack" e preço "$ 29.99".          📸 detalhes_produto
- [ ] Quantidade inicial 1 e botão "Add to cart" visível.
