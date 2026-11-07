# Navigation Context — Sauce Labs My Demo App 2.3.0

Seletores no `*** Variables ***` de `tests/pages/<pagina>.resource` (variáveis Robot `${LOC_<TELA>_<ELEMENTO>}`).

## Mapa de telas

```
[Splash] ──► [Catalog / Products] ◄──────────────────────────┐
                 │  menuIV                                    │
                 ▼                                            │
          [Navigation Drawer]                                 │
            │ "Log In" (deslogado)      │ "Log Out" (logado)  │
            ▼                           ▼                     │
         [Login] ── login OK ───────────┼─────────────────────┘
            ▲                           ▼
            │                     [Logout Dialog]
            └──── LOGOUT confirmado ────┘   (CANCEL → volta ao app)
```

## Estado inicial (determinístico)

- Cada teste abre uma sessão nova (`Abrir Aplicativo`, chamado por `Iniciar App Autenticado`).
- Com `appium:noReset=false` (`tests/config/capabilities.json`), o UiAutomator2 para o app e limpa os dados ao
  criar a sessão. Resultado: tela **Products**, usuário **deslogado**, carrinho vazio.
- A mesma capability vale para o Appium MCP: toda sessão de exploração também começa com o app limpo.

## Transições validadas

| De | Ação | Para | Verificação |
|---|---|---|---|
| Catalog | toque `menuIV` | Drawer | `menuRV` visível |
| Drawer (deslogado) | `Login Menu Item` | Login | `loginTV` = "Login" |
| Login | submit com usuário válido | Catalog | `productTV` = "Products" |
| Drawer (logado) | `Logout Menu Item` | Logout Dialog | mensagem "Are you sure you want to logout" |
| Logout Dialog | `LOGOUT` (`android:id/button1`) | **Login** (não volta ao catálogo) | `loginTV` visível |
| Drawer | Back | tela anterior | `menuRV` ausente (⚠️ logo após o login fecha o app: ver `limitacoes-conhecidas.md`) |
| Catalog | toque na imagem `productIV` do item (o `titleTV` **não** é clicável) | Product Details | `productTV` = nome do produto; botão "Add to cart" |
| Product Details | "Add to cart" (`Tap to add product to cart`) | Product Details | contador `cartTV` no cabeçalho = quantidade |
| Qualquer tela com cabeçalho | `cartRL` | Cart (My Cart) | `productTV` = "My Cart"; `itemsTV` visível |
| Catalog | `sortIV` → opção (ex.: "Price - Ascending") | Catalog reordenado | 1º item = "Sauce Labs Onesie" ($ 7.99) |
| Cart (deslogado) | "Proceed To Checkout" | **Login** | `loginTV` visível |
| Cart (logado) | "Proceed To Checkout" | Checkout: endereço | "Enter a shipping address" |
| Checkout: endereço | "To Payment" | Checkout: pagamento | "Enter a payment method" |
| Checkout: pagamento | "Review Order" | Checkout: revisão | "Review your order"; total = itens + $ 5.99 |
| Checkout: revisão | "Place Order" | Checkout Complete | "Thank you for your order" |
| Checkout Complete | "Continue Shopping" | Catalog | carrinho esvaziado (sem `cartTV`) |
| Cart (sem itens) | "Go Shopping" (`shoppingBt`) | Catalog | `productTV` = "Products" |

## Acesso ao login (step de setup)

1. Catálogo: abrir o menu (`menuIV`).
2. Selecionar `Login Menu Item` (texto "Log In").
3. Confirmar o título `loginTV` = "Login", preencher usuário/senha de uma massa de `tests/massas/users.yaml` e tocar em `loginBtn`.

Keyword: `Iniciar App Autenticado` (`tests/resources/suite.resource`).

Comportamentos de cada tela: `context/descobertas/comportamentos-observados.md`.
Limitações e defeitos que afetam a navegação: `context/descobertas/limitacoes-conhecidas.md`.

## Itens do menu lateral (não explorados)

Catalog, WebView, QR Code Scanner, Geo Location, Drawing, About, Reset App State,
FingerPrint, Virtual USB, Crash app (debug). Todos usam `resource-id itemTV` e só se
distinguem pelo texto. Para usar algum, explore com o Appium MCP e registre aqui.

## Regras de navegação

1. Inspecionar a tela atual antes de agir.
2. Priorizar `resource_id` e depois `accessibility_id`. Usar texto só quando não houver ID.
3. Verificar a tela resultante após cada ação importante.
4. Não assumir que uma ação funcionou só porque foi enviada.
5. O teclado pode cobrir o botão Login: chamar `Ocultar Teclado` após digitar.
