*** Settings ***
Documentation     Tela de catálogo (Products)
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# catalog
${LOC_CATALOG_TITLE}            id=com.saucelabs.mydemoapp.android:id/productTV    # texto "Products"
${LOC_CATALOG_MENU_BUTTON}      id=com.saucelabs.mydemoapp.android:id/menuIV
${LOC_CATALOG_SORT_BUTTON}      id=com.saucelabs.mydemoapp.android:id/sortIV
${LOC_CATALOG_SORT_OPTION}      android=new UiSelector().text("{opcao}")    # Template {opcao}: "Name - Ascending" | "Name - Descending" | "Price - Ascending" | "Price - Descending"
${LOC_CATALOG_CART}             id=com.saucelabs.mydemoapp.android:id/cartRL
${LOC_CATALOG_PRODUCT_LIST}     id=com.saucelabs.mydemoapp.android:id/productRV
${LOC_CATALOG_PRODUCT_TITLE}    id=com.saucelabs.mydemoapp.android:id/titleTV    # Repetido por item da lista; combinar com texto para um produto específico.
${LOC_CATALOG_PRODUCT_PRICE}    id=com.saucelabs.mydemoapp.android:id/priceTV    # NÃO VALIDADO
${LOC_CATALOG_CART_BADGE}       id=com.saucelabs.mydemoapp.android:id/cartTV    # Só existe com carrinho não vazio; texto = quantidade total de itens.


*** Keywords ***
Validar Tela De Produtos
    Wait Until Element Is Visible    ${LOC_CATALOG_TITLE}
    Validar Texto Do Elemento    ${LOC_CATALOG_TITLE}    Products

Validar Produto No Catálogo
    [Documentation]    Rola até o produto e valida o preço exibido no card.
    [Arguments]    ${produto}    ${preco}
    Validar Produto Listado    ${produto}    ${preco}

Validar Primeiro Produto Do Catálogo
    [Documentation]    Com retentativa até ${TIMEOUT}: logo após ordenar, a lista ainda pode estar sendo redesenhada.
    [Arguments]    ${produto}    ${preco}
    Wait Until Keyword Succeeds    ${TIMEOUT}    500ms    Conferir Primeiro Produto Do Catálogo    ${produto}    ${preco}

Conferir Primeiro Produto Do Catálogo
    [Arguments]    ${produto}    ${preco}
    Wait Until Element Is Visible    ${LOC_CATALOG_PRODUCT_TITLE}
    @{titulos}=    Get Webelements    ${LOC_CATALOG_PRODUCT_TITLE}
    @{precos}=    Get Webelements    ${LOC_PRODUCT_ITEM_ALL_PRICES}
    ${titulo}=    Get Text    ${titulos}[0]
    ${valor}=    Get Text    ${precos}[0]
    Should Be Equal    ${titulo}    ${produto}
    Should Be Equal    ${valor}    ${preco}

Validar Preços Em Ordem Crescente
    [Documentation]    Com retentativa até ${TIMEOUT}: logo após ordenar, a lista ainda pode estar sendo redesenhada.
    Wait Until Keyword Succeeds    ${TIMEOUT}    500ms    Conferir Preços Em Ordem Crescente

Conferir Preços Em Ordem Crescente
    [Documentation]    Uma tentativa: compara os preços visíveis na ordem em que aparecem (ao menos 2).
    @{elementos}=    Get Webelements    ${LOC_PRODUCT_ITEM_ALL_PRICES}
    VAR    @{textos}    @{EMPTY}
    FOR    ${elemento}    IN    @{elementos}
        ${texto}=    Get Text    ${elemento}
        Append To List    ${textos}    ${texto}
    END
    ${valores}=    Evaluate    [float(t.replace('$', '').strip()) for t in $textos]
    Should Be True    len($valores) >= 2    Menos de 2 preços visíveis: ${textos}
    Should Be True    $valores == sorted($valores)    Preços fora de ordem crescente: ${textos}

Ordenar Catálogo Por
    [Documentation]    ${opcao}: "Name - Ascending" | "Name - Descending" | "Price - Ascending" | "Price - Descending".
    [Arguments]    ${opcao}
    ${locator}=    Format String    ${LOC_CATALOG_SORT_OPTION}    opcao=${opcao}
    Click Element    ${LOC_CATALOG_SORT_BUTTON}
    Wait Until Element Is Visible    ${locator}
    Click Element    ${locator}
    Wait Until Page Does Not Contain Element    ${locator}
    Validar Tela De Produtos

Selecionar Produto No Catálogo
    [Documentation]    Abre os detalhes do produto pelo nome (toca na imagem do card; o título não é clicável).
    [Arguments]    ${produto}
    ${titulo}=    Format String    ${LOC_PRODUCT_ITEM_TITLE_BY_NAME}    nome=${produto}
    ${imagem}=    Format String    ${LOC_PRODUCT_ITEM_IMAGE_BY_NAME}    nome=${produto}
    Wait Until Page Contains Element    ${titulo}
    Wait Until Element Is Visible    ${imagem}
    Click Element    ${imagem}
    Wait Until Element Is Visible    ${LOC_PRODUCT_DETAILS_ADD_TO_CART_BUTTON}

Voltar Para O Catálogo
    [Documentation]    Back a partir dos detalhes do produto (não usar com o menu lateral aberto).
    Go Back
    Validar Tela De Produtos

Validar Carrinho Vazio No Cabeçalho
    [Documentation]    Sem itens, o contador do carrinho não é exibido.
    Wait Until Element Is Visible    ${LOC_CATALOG_CART}
    Page Should Not Contain Element    ${LOC_CATALOG_CART_BADGE}

Validar Quantidade No Ícone Do Carrinho
    [Arguments]    ${quantidade}
    Wait Until Element Is Visible    ${LOC_CATALOG_CART_BADGE}
    Validar Texto Do Elemento    ${LOC_CATALOG_CART_BADGE}    ${quantidade}

Abrir Carrinho
    [Documentation]    O título (productTV) também existe na tela de origem (Products/detalhes): espera pelo
    ...                TEXTO "My Cart", com retry, para não pegar o elemento da tela anterior (stale).
    Click Element    ${LOC_CATALOG_CART}
    Validar Texto Do Elemento    ${LOC_CART_TITLE}    ${MSG_CART_TITLE}
