# BUY-002 Compra de vários produtos com sucesso

- **ID:** BUY-002
- **Tags:** compra, compra-de-varios-itens
- **Suíte:** compra (`tests/robot/compra/compra.robot`)

## Objetivo
Garantir que a compra de vários produtos é concluída com sucesso.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produtos: Sauce Labs Onesie ($ 7.99) e Sauce Labs Bike Light ($ 9.99)
- endereço e cartão fictícios: seção `*** Variables ***` de `tests/robot/compra/compra.robot`
- frete: $ 5.99

## Passos
1. Ordenar por "Price - Ascending" e adicionar os dois produtos.
2. Abrir o carrinho e tocar em "Proceed To Checkout".
3. Preencher endereço e pagamento.
4. Tocar em "Review Order".
5. Tocar em "Place Order".
6. Tocar em "Continue Shopping".

## Resultado esperado (critérios verificáveis)
- [ ] A revisão lista os dois produtos, "2 Items" e total $ 23.97 (produtos + frete).  📸 revisao_pedido
- [ ] A tela "Checkout Complete" mostra "Thank you for your order".  📸 pedido_concluido
- [ ] Ao continuar comprando, volta ao catálogo com o carrinho vazio.  📸 catalogo_apos_compra

## Observações da execução
- 2026-11-07: SKIP (defeito-conhecido) — após ordenar por preço, o "Sauce Labs Bike Light" fica na 2ª posição, e
  tocar nela fecha o app (bug proposital do app de demonstração). Ver `context/descobertas/limitacoes-conhecidas.md`
  › "App fecha ao abrir o produto da 2ª posição do catálogo".
