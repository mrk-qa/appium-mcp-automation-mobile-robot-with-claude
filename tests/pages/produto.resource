*** Settings ***
Documentation     Detalhes do produto e itens de lista
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# product_details
${LOC_PRODUCT_DETAILS_TITLE}                 id=com.saucelabs.mydemoapp.android:id/productTV    # Mesmo resource-id do título do catálogo/carrinho; aqui exibe o nome do produto.
${LOC_PRODUCT_DETAILS_PRICE}                 id=com.saucelabs.mydemoapp.android:id/priceTV
${LOC_PRODUCT_DETAILS_QUANTITY}              id=com.saucelabs.mydemoapp.android:id/noTV
${LOC_PRODUCT_DETAILS_ADD_TO_CART_BUTTON}    accessibility_id=Tap to add product to cart    # texto "Add to cart"; resource-id cartBt é reutilizado no botão "Proceed To Checkout" do carrinho.

# product_item
${LOC_PRODUCT_ITEM_IMAGE_BY_NAME}            xpath=//android.widget.TextView[@resource-id="com.saucelabs.mydemoapp.android:id/titleTV" and @text="{nome}"]/preceding-sibling::android.widget.ImageView[@resource-id="com.saucelabs.mydemoapp.android:id/productIV"]    # Imagem clicável do item no catálogo (o título não é clicável).
${LOC_PRODUCT_ITEM_TITLE_BY_NAME}            android=new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().resourceId("com.saucelabs.mydemoapp.android:id/titleTV").text("{nome}"))    # Rola a lista até o item (UiScrollable) e o localiza pelo nome.
${LOC_PRODUCT_ITEM_PRICE_BY_NAME}            xpath=//android.widget.TextView[@resource-id="com.saucelabs.mydemoapp.android:id/titleTV" and @text="{nome}"]/following-sibling::android.widget.TextView[@resource-id="com.saucelabs.mydemoapp.android:id/priceTV"][1]
${LOC_PRODUCT_ITEM_ALL_PRICES}               id=com.saucelabs.mydemoapp.android:id/priceTV    # Preços dos itens visíveis (ordem de exibição).


*** Keywords ***
Validar Tela De Detalhes Do Produto
    [Arguments]    ${produto}    ${preco}
    Wait Until Element Is Visible    ${LOC_PRODUCT_DETAILS_ADD_TO_CART_BUTTON}
    Validar Texto Do Elemento    ${LOC_PRODUCT_DETAILS_TITLE}    ${produto}
    Validar Texto Do Elemento    ${LOC_PRODUCT_DETAILS_PRICE}    ${preco}
    Validar Texto Do Elemento    ${LOC_PRODUCT_DETAILS_QUANTITY}    1

Adicionar Produto Ao Carrinho
    [Documentation]    Toca em "Add to cart" e espera o contador do carrinho aumentar em 1.
    ${antes}=    Obter Quantidade No Ícone Do Carrinho
    Click Element    ${LOC_PRODUCT_DETAILS_ADD_TO_CART_BUTTON}
    ${esperado}=    Evaluate    str(int(${antes}) + 1)
    Validar Texto Do Elemento    ${LOC_CATALOG_CART_BADGE}    ${esperado}

Obter Quantidade No Ícone Do Carrinho
    ${existe}=    Run Keyword And Return Status    Page Should Contain Element    ${LOC_CATALOG_CART_BADGE}
    IF    not ${existe}    RETURN    ${0}
    ${texto}=    Get Text    ${LOC_CATALOG_CART_BADGE}
    RETURN    ${texto}

Validar Produto Listado
    [Documentation]    Item de lista (catálogo, carrinho ou revisão): rola até o nome e valida o preço do item.
    [Arguments]    ${produto}    ${preco}
    ${titulo}=    Format String    ${LOC_PRODUCT_ITEM_TITLE_BY_NAME}    nome=${produto}
    ${preco_item}=    Format String    ${LOC_PRODUCT_ITEM_PRICE_BY_NAME}    nome=${produto}
    Wait Until Page Contains Element    ${titulo}
    Wait Until Element Is Visible    ${preco_item}
    Validar Texto Do Elemento    ${preco_item}    ${preco}
