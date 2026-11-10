# CART-002 Adicionar vários produtos ao carrinho

- **ID:** CART-002
- **Tags:** carrinho, adicionar-varios-itens
- **Suíte:** carrinho (`tests/robot/carrinho/carrinho.robot`)
- **Regras:** RN-CART-02, RN-CART-03, RN-CART-04

## Objetivo
Garantir que vários produtos diferentes são somados no carrinho.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produtos: Sauce Labs Onesie ($ 7.99) e Sauce Labs Bike Light ($ 9.99)

## Passos
1. Ordenar o catálogo por "Price - Ascending".
2. Adicionar "Sauce Labs Onesie" e voltar ao catálogo.
3. Adicionar "Sauce Labs Bike Light".
4. Abrir o carrinho.

## Resultado esperado (critérios verificáveis)
- [ ] O contador do carrinho mostra 2.                     📸 contador_carrinho
- [ ] O carrinho lista "Sauce Labs Onesie" ($ 7.99) e "Sauce Labs Bike Light" ($ 9.99).
- [ ] Totais: "2 Items" e "$ 17.98".                    📸 itens_no_carrinho

## Observações da execução
- 2026-11-07: SKIP (defeito-conhecido) — após ordenar por preço, o "Sauce Labs Bike Light" fica na 2ª posição, e
  tocar nela fecha o app (bug proposital do app de demonstração). Ver `context/descobertas/limitacoes-conhecidas.md`
  › "App fecha ao abrir o produto da 2ª posição do catálogo".
