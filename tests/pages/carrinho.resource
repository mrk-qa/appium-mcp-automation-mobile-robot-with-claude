*** Settings ***
Documentation     Tela do carrinho (My Cart)
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# cart
${LOC_CART_TITLE}                 id=com.saucelabs.mydemoapp.android:id/productTV    # texto "My Cart"
${LOC_CART_ITEM_TITLE}            id=com.saucelabs.mydemoapp.android:id/titleTV
${LOC_CART_ITEM_PRICE}            id=com.saucelabs.mydemoapp.android:id/priceTV
${LOC_CART_ITEM_QUANTITY}         id=com.saucelabs.mydemoapp.android:id/noTV
${LOC_CART_REMOVE_ITEM_BUTTON}    accessibility_id=Removes product from cart    # texto "Remove Item"
${LOC_CART_TOTAL_ITEMS}           id=com.saucelabs.mydemoapp.android:id/itemsTV
${LOC_CART_TOTAL_PRICE}           id=com.saucelabs.mydemoapp.android:id/totalPriceTV
${LOC_CART_CHECKOUT_BUTTON}       accessibility_id=Confirms products for checkout    # texto "Proceed To Checkout"

# cart sem itens (tela "No Items")
${LOC_CART_EMPTY_TITLE}           id=com.saucelabs.mydemoapp.android:id/noItemTitleTV    # texto "No Items"
${LOC_CART_EMPTY_MESSAGE}         xpath=//*[@resource-id="com.saucelabs.mydemoapp.android:id/cartInfoLL"]/android.widget.TextView    # a mensagem não tem resource-id próprio
${LOC_CART_GO_SHOPPING_BUTTON}    id=com.saucelabs.mydemoapp.android:id/shoppingBt    # texto "Go Shopping"

# mensagens exibidas pelo app
${MSG_CART_TITLE}            My Cart
${MSG_CART_EMPTY_TITLE}      No Items
${MSG_CART_EMPTY_MESSAGE}    Oh no! Your cart is empty. Fill it up with swag to complete your purchase.


*** Keywords ***
Validar Tela Do Carrinho
    Wait Until Element Is Visible    ${LOC_CART_TITLE}
    Validar Texto Do Elemento    ${LOC_CART_TITLE}    ${MSG_CART_TITLE}

Validar Item No Carrinho
    [Documentation]    Carrinho com um único item: valida nome, preço, quantidade e o botão "Remove Item".
    [Arguments]    ${produto}    ${preco}    ${quantidade}
    Wait Until Element Is Visible    ${LOC_CART_ITEM_TITLE}
    Validar Texto Do Elemento    ${LOC_CART_ITEM_TITLE}    ${produto}
    Validar Texto Do Elemento    ${LOC_CART_ITEM_PRICE}    ${preco}
    Validar Texto Do Elemento    ${LOC_CART_ITEM_QUANTITY}    ${quantidade}
    Page Should Contain Element    ${LOC_CART_REMOVE_ITEM_BUTTON}

Validar Totais Do Carrinho
    [Documentation]    O app exibe "<n> Items" (inclusive no singular). ${total} no formato "$ 29.99".
    [Arguments]    ${quantidade}    ${total}
    Wait Until Element Is Visible    ${LOC_CART_TOTAL_ITEMS}
    Validar Texto Do Elemento    ${LOC_CART_TOTAL_ITEMS}    ${quantidade} Items
    Validar Texto Do Elemento    ${LOC_CART_TOTAL_PRICE}    ${total}
    Page Should Contain Element    ${LOC_CART_CHECKOUT_BUTTON}

Remover Produto Do Carrinho
    [Documentation]    Carrinho com um único item: toca em "Remove Item" e espera o item sumir.
    Click Element    ${LOC_CART_REMOVE_ITEM_BUTTON}
    Wait Until Page Does Not Contain Element    ${LOC_CART_ITEM_TITLE}

Validar Carrinho Vazio
    Page Should Not Contain Element    ${LOC_CART_ITEM_TITLE}
    Page Should Not Contain Element    ${LOC_CART_CHECKOUT_BUTTON}
    Page Should Not Contain Element    ${LOC_CATALOG_CART_BADGE}

Validar Tela De Carrinho Sem Itens
    [Documentation]    Carrinho vazio: título "No Items", mensagem de carrinho vazio e botão "Go Shopping".
    Wait Until Element Is Visible    ${LOC_CART_EMPTY_TITLE}
    Validar Texto Do Elemento    ${LOC_CART_EMPTY_TITLE}    ${MSG_CART_EMPTY_TITLE}
    Validar Texto Do Elemento    ${LOC_CART_EMPTY_MESSAGE}    ${MSG_CART_EMPTY_MESSAGE}
    Validar Texto Do Elemento    ${LOC_CART_GO_SHOPPING_BUTTON}    Go Shopping

Voltar Às Compras
    [Documentation]    Toca em "Go Shopping" na tela "No Items" e espera o catálogo.
    Click Element    ${LOC_CART_GO_SHOPPING_BUTTON}
    Validar Tela De Produtos

Iniciar Checkout
    Click Element    ${LOC_CART_CHECKOUT_BUTTON}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_ADDRESS_TITLE}
