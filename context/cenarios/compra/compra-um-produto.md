# BUY-001 Compra de um produto com sucesso

- **ID:** BUY-001
- **Tags:** compra, compra-de-um-item
- **Suíte:** compra (`tests/robot/compra/compra.robot`)

## Objetivo
Garantir que a compra de um produto é concluída com sucesso.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado (`Iniciar App Autenticado`)

## Dados
- produto: Sauce Labs Backpack ($ 29.99)
- endereço e cartão fictícios: seção `*** Variables ***` de `tests/robot/compra/compra.robot`
- frete: $ 5.99

## Passos
1. Adicionar "Sauce Labs Backpack" e abrir o carrinho.
2. Tocar em "Proceed To Checkout".
3. Preencher o endereço de entrega.                  📸 endereco_entrega
4. Tocar em "To Payment" e preencher o cartão.         📸 pagamento
5. Tocar em "Review Order".
6. Tocar em "Place Order".
7. Tocar em "Continue Shopping".

## Resultado esperado (critérios verificáveis)
- [ ] A revisão mostra o produto, o endereço, o titular do cartão, "1 Items" e total $ 35.98 (produto + frete). 📸 revisao_pedido
- [ ] A tela "Checkout Complete" mostra "Thank you for your order".  📸 pedido_concluido
- [ ] Ao continuar comprando, volta ao catálogo com o carrinho vazio.  📸 catalogo_apos_compra
