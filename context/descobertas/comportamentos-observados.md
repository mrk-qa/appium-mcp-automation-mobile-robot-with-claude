# Comportamentos observados — Sauce Labs My Demo App 2.3.0

Como o app **realmente** se comporta, por funcionalidade. Registre aqui cada comportamento novo
descoberto na exploração (Appium MCP) ou confirmado numa execução Robot, com a data e a origem.
Comportamentos que contrariam o esperado vão para `limitacoes-conhecidas.md`.

## Login (usado como step de setup: `Iniciar App Autenticado`)

Explorado em 2026-11-07 (a antiga suíte de login foi removida; o login não é objeto de teste).

| Caso | Resultado observado |
|---|---|
| Usuário válido + senha válida | Vai para **Products**; o menu lateral mostra "Log Out" |
| Usuário vazio | Permanece no Login; "Username is required" (`nameErrorTV`) |
| Senha vazia | Permanece no Login; "Enter Password" (`passwordErrorTV`) |
| `alice@example.com` | Permanece no Login; "Sorry this user has been locked out." (`passwordErrorTV`) |
| Logout | Diálogo de confirmação → LOGOUT → abre a tela **Login** |

- Os usuários de demonstração (`bod@example.com`, `alice@example.com (locked out)`, `visual@example.com`)
  aparecem na própria tela de login; tocar em um deles preenche usuário e senha.
- O checkout exige login: deslogado, "Proceed To Checkout" redireciona para a tela Login.

## Catálogo (PROD-001..003)

- Título `productTV` = "Products". Cada card tem imagem (`productIV`, clicável), título (`titleTV`,
  **não clicável**) e preço (`priceTV`, formato `$ 29.99`).
- Ordenação (`sortIV`): "Name - Ascending/Descending", "Price - Ascending/Descending".
  Com "Price - Ascending", o 1º item é "Sauce Labs Onesie" ($ 7.99). A ordenação se mantém ao voltar dos detalhes.
- O ícone de ordenação no cabeçalho mostra a ordem ativa: "↑AB" na ordem padrão (nome crescente) e "↑$" após
  "Price - Ascending". (2026-11-07, PROD-003, `tests/reports/screenshots/PROD-003/01_ordenado_preco_crescente.png`)
- Na ordem padrão, "Sauce Labs Onesie" fica perto do fim da lista, depois das jaquetas "Fleece Jacket" ($ 49.99).
  (2026-11-07, PROD-001, `tests/reports/screenshots/PROD-001/02_catalogo_rolado.png`)
- O resource-id `productTV` é reutilizado como título em Catalog ("Products"), Product Details
  (nome do produto) e Cart ("My Cart").

## Carrinho (CART-001..003)

- Carrinho vazio: o contador `cartTV` **não existe** no cabeçalho.
- Após "Add to cart", o contador soma 1 a cada produto adicionado.
- Totais: `itemsTV` = "<n> Items" (mesmo no singular) e `totalPriceTV` = soma dos preços.
- "Remove Item" no único item esvazia o carrinho: somem o item, o botão de checkout e o contador.
- Carrinho vazio exibe a tela **"No Items"** com o texto "Oh no! Your cart is empty. Fill it up with swag to
  complete your purchase." e o botão **"Go Shopping"** (evidência do CART-003 em 2026-11-07). Seletores: título `noItemTitleTV`, mensagem sem
  resource-id (dentro de `cartInfoLL`), botão `shoppingBt`. Abrir o carrinho vazio pelo cabeçalho mostra a mesma tela.
- O resource-id `cartBt` é reutilizado em "Add to cart" e "Proceed To Checkout": use os accessibility ids.

## Checkout (BUY-001..002)

Explorado em 2026-11-07; validado no BUY-001.

- Fluxo: Cart → Endereço → Pagamento → Revisão → **Checkout Complete** → "Continue Shopping" → Catalog.
- Os campos de endereço e pagamento exibem placeholders (ex.: "Rebecca Winter") que **não** são valores.
- Validade do cartão: digitar só números (MMAA); o app formata como MM/AA.
- A revisão soma **frete de $ 5.99** ao total ($ 29.99 → $ 35.98).
- "Checkout Complete" mostra "Thank you for your order"; "Continue Shopping" volta ao catálogo com o
  carrinho **esvaziado**.
