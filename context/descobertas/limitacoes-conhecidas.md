# Limitações conhecidas e defeitos — Sauce Labs My Demo App 2.3.0

Comportamentos do app que **divergem do esperado**. Não são falhas da automação: um teste que
esbarrar num item desta lista deve ser reportado como **divergência (possível defeito)**, e a
asserção **não** deve ser relaxada nem contornada. Antes de executar um cenário, confira se ele
bate com algum item abaixo e avise que o resultado provavelmente vai divergir.

Registre cada item novo com: data, como reproduzir, evidência e testes afetados. Defeito confirmado e
persistente: marque os testes afetados com a tag `defeito-conhecido`. Com `--skiponfailure defeito-conhecido`
(`tests/robot.args`) eles aparecem como **SKIP** com o motivo e voltam a **PASS** sozinhos quando o app for
corrigido; ao confirmar a correção, remova a tag e mova o item para "Resolvidos".

## Limitações

### Login: a senha não é validada
- `bod@example.com` com senha errada autentica normalmente.
- Qualquer usuário não bloqueado autentica (ex.: `nobody@example.com`).
- Um cenário "login com senha inválida deve falhar" **vai falhar nesta versão**.
- O estado autenticado não identifica a conta ativa na interface.

### Back logo após o login fecha o app
- 2026-11-07: com o menu lateral aberto logo após o login, `Go Back` (`Fechar Menu Lateral`)
  **fecha o app** e volta ao launcher.
- Na automação: não use `Fechar Menu Lateral` depois do login.

### O app não aceita deep links
- **Reproduzido:** 1x; última em 2026-11-07 (verificação de configuração, sem teste Robot).
- **Passos:** `adb shell am start -a android.intent.action.VIEW -d "<url>" com.saucelabs.mydemoapp.android`
  com `swaglabs://swag-overview/0,2`, `mydemoapp://store-overview`, `mydemoapp://cart`,
  `mydemoapp://product-details/1` e `mydemoapp://checkout-address`.
- **Esperado:** abrir a tela direto, sem navegar pela interface.
- **Obtido:** `Error: Activity not started, unable to resolve Intent` em todos; `pm query-activities` não encontra
  nenhuma atividade para o esquema.
- **Evidência:** o manifesto do APK `tests/apk/mda-2.3.0-27.apk` só tem o `intent-filter` MAIN/LAUNCHER da
  `SplashActivity`, sem `<data android:scheme>`; a `MainActivity` não é exportada.
- **Observação:** os deep links do artigo da Sauce Labs ("How to automate deep link testing") são do app
  **Swag Labs** (`swaglabs://`, `com.swaglabsmobileapp`), não do My Demo App.
- **Repositório oficial** (`github.com/saucelabs/my-demo-app-android`, verificado em 2026-11-07):
  - README sem deep links; 2.3.0 é a release mais recente (a que usamos).
  - `app/src/main/AndroidManifest.xml` da `main` e das tags 1.0.14, 1.0.17, 2.0.0 e 2.2.0: zero `android:scheme`/`BROWSABLE`.
  - Código-fonte (57 arquivos Java/Kotlin em `src/main`): nenhum trata URL recebida (`getData()`, `Uri.parse`, `ACTION_VIEW`).
  - O `my-demo-app-rn` (React Native) está descontinuado em favor deste app e também não documenta deep links.
- **Conclusão:** não existe versão do My Demo App Android com deep links. Habilitar exigiria alterar o app
  (declarar `intent-filter` com `<data android:scheme>` na `MainActivity` e tratar a URL), fora do escopo de QA.
- **Testes afetados:** nenhum; impede usar deep link como atalho de navegação nos testes.
- **Status:** aberto.

## Defeitos

### 🐞 App fecha ao abrir o produto da 2ª posição do catálogo
- **Reproduzido:** em todas as execuções da suíte desde 2026-11-07; última em 2026-11-07 17:11 (CART-002, BUY-002).
  Confirmado sem ordenar em 2026-11-07 20:26 (Appium MCP): tocar no "Sauce Labs Backpack (green)", 2º item da
  ordem padrão, gera o mesmo crash.
- **Passos (mínimo):** na tela Products, tocar no produto da **2ª posição** da lista, em qualquer ordenação.
  Nos testes: ordenar por "Price - Ascending" deixa o "Sauce Labs Bike Light" na 2ª posição.
- **Causa (código-fonte da 2.3.0):** `ProductCatalogFragment.java`, `setAdapter()`:
  `final Integer[] meta = new Integer[] { 0, null, 2, 3, 4, 5 }; // null is an intentionally introduced bug for demos`
  e, na linha 156, `meta[position].intValue()`. A posição 1 (2º item) é `null`.
- **Defeito proposital:** o My Demo App é um app de demonstração da Sauce Labs com bugs plantados. Não há issue
  aberta no repositório e não há expectativa de correção.
- **Hipótese (pelo código, não reproduzida):** produtos a partir da 7ª posição também devem fechar o app
  (`ArrayIndexOutOfBoundsException`), porque o vetor `meta` só tem 6 itens.
- **Esperado:** abrir os detalhes do produto tocado.
- **Obtido:** "My Demo App keeps stopping"; o app fecha e o device volta ao launcher. O botão "Add to cart" não
  aparece em 30s (`Element locator 'accessibility_id=Tap to add product to cart' did not match any elements`).
- **Evidência:** `tests/reports/screenshots/CART-002/01_falha.png` e `tests/reports/screenshots/BUY-002/01_falha.png`
  (launcher); logcat: `java.lang.NullPointerException: ... Integer.intValue() on a null object reference`
  `at ...view.fragments.ProductCatalogFragment.lambda$setAdapter$0(ProductCatalogFragment.java:156)`.
- **Testes afetados:** CART-002 e BUY-002, com a tag `defeito-conhecido` (SKIP até a correção; não contornar).
- **Status:** aberto.

## Resolvidos

_Nenhum até o momento._
