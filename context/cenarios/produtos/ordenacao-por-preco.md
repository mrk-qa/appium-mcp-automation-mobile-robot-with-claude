# PROD-003 Ordenar catálogo por preço crescente

- **ID:** PROD-003
- **Tags:** produtos, ordenacao-por-preco
- **Suíte:** produtos (`tests/robot/produtos/produtos.robot`)
- **Regras:** RN-PROD-03

## Objetivo
Garantir que a ordenação por preço crescente reordena o catálogo.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto mais barato: Sauce Labs Onesie ($ 7.99)

## Passos
1. Tocar no botão de ordenação.
2. Selecionar "Price - Ascending".

## Resultado esperado (critérios verificáveis)
- [ ] O primeiro produto é "Sauce Labs Onesie" ($ 7.99).
- [ ] Os preços visíveis estão em ordem crescente.   📸 ordenado_preco_crescente
