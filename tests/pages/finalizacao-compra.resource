*** Settings ***
Documentation     Checkout: endereço, pagamento, revisão e conclusão
...               Os dados (endereço, cartão, totais esperados) vêm dos arquivos .robot.
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# checkout_address
${LOC_CHECKOUT_ADDRESS_TITLE}                        id=com.saucelabs.mydemoapp.android:id/enterShippingAddressTV    # texto "Enter a shipping address"
${LOC_CHECKOUT_ADDRESS_FULL_NAME}                    id=com.saucelabs.mydemoapp.android:id/fullNameET
${LOC_CHECKOUT_ADDRESS_ADDRESS_LINE1}                id=com.saucelabs.mydemoapp.android:id/address1ET
${LOC_CHECKOUT_ADDRESS_CITY}                         id=com.saucelabs.mydemoapp.android:id/cityET
${LOC_CHECKOUT_ADDRESS_ZIP}                          id=com.saucelabs.mydemoapp.android:id/zipET
${LOC_CHECKOUT_ADDRESS_COUNTRY}                      id=com.saucelabs.mydemoapp.android:id/countryET
${LOC_CHECKOUT_ADDRESS_TO_PAYMENT_BUTTON}            accessibility_id=Saves user info for checkout    # texto "To Payment"

# checkout_payment
${LOC_CHECKOUT_PAYMENT_TITLE}                        id=com.saucelabs.mydemoapp.android:id/enterPaymentMethodTV    # texto "Enter a payment method"
${LOC_CHECKOUT_PAYMENT_CARD_HOLDER}                  id=com.saucelabs.mydemoapp.android:id/nameET
${LOC_CHECKOUT_PAYMENT_CARD_NUMBER}                  id=com.saucelabs.mydemoapp.android:id/cardNumberET
${LOC_CHECKOUT_PAYMENT_EXPIRATION_DATE}              id=com.saucelabs.mydemoapp.android:id/expirationDateET    # Digitar só números (MMAA): o app formata como MM/AA.
${LOC_CHECKOUT_PAYMENT_SECURITY_CODE}                id=com.saucelabs.mydemoapp.android:id/securityCodeET
${LOC_CHECKOUT_PAYMENT_REVIEW_ORDER_BUTTON}          accessibility_id=Saves payment info and launches screen to review checkout data    # texto "Review Order"

# checkout_review
${LOC_CHECKOUT_REVIEW_TITLE}                         id=com.saucelabs.mydemoapp.android:id/enterShippingAddressTV    # texto "Review your order"; Mesmo resource-id do título da tela de endereço; aqui o texto é "Review your order".
${LOC_CHECKOUT_REVIEW_DELIVERY_NAME}                 id=com.saucelabs.mydemoapp.android:id/fullNameTV
${LOC_CHECKOUT_REVIEW_DELIVERY_ADDRESS}              id=com.saucelabs.mydemoapp.android:id/addressTV
${LOC_CHECKOUT_REVIEW_DELIVERY_COUNTRY}              id=com.saucelabs.mydemoapp.android:id/countryTV    # Formato: "<país>, <CEP>"
${LOC_CHECKOUT_REVIEW_CARD_HOLDER}                   id=com.saucelabs.mydemoapp.android:id/cardHolderTV
${LOC_CHECKOUT_REVIEW_TOTAL_ITEMS}                   id=com.saucelabs.mydemoapp.android:id/itemNumberTV
${LOC_CHECKOUT_REVIEW_TOTAL_AMOUNT}                  id=com.saucelabs.mydemoapp.android:id/totalAmountTV    # Inclui o frete de $ 5.99 (validado no BUY-001: $ 29.99 → $ 35.98).
${LOC_CHECKOUT_REVIEW_PLACE_ORDER_BUTTON}            accessibility_id=Completes the process of checkout    # texto "Place Order"

# checkout_complete
${LOC_CHECKOUT_COMPLETE_TITLE}                       id=com.saucelabs.mydemoapp.android:id/completeTV    # texto "Checkout Complete"
${LOC_CHECKOUT_COMPLETE_THANK_YOU}                   id=com.saucelabs.mydemoapp.android:id/thankYouTV
${LOC_CHECKOUT_COMPLETE_CONTINUE_SHOPPING_BUTTON}    accessibility_id=Tap to open catalog    # texto "Continue Shopping"

# mensagens exibidas pelo app
${MSG_CHECKOUT_REVIEW_TITLE}      Review your order
${MSG_CHECKOUT_COMPLETE_TITLE}    Checkout Complete
${MSG_CHECKOUT_THANK_YOU}         Thank you for your order


*** Keywords ***
Preencher Endereço De Entrega
    [Arguments]    ${nome}    ${endereco}    ${cidade}    ${cep}    ${pais}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_ADDRESS_FULL_NAME}
    Input Text    ${LOC_CHECKOUT_ADDRESS_FULL_NAME}    ${nome}
    Input Text    ${LOC_CHECKOUT_ADDRESS_ADDRESS_LINE1}    ${endereco}
    Input Text    ${LOC_CHECKOUT_ADDRESS_CITY}    ${cidade}
    Input Text    ${LOC_CHECKOUT_ADDRESS_ZIP}    ${cep}
    Input Text    ${LOC_CHECKOUT_ADDRESS_COUNTRY}    ${pais}
    Ocultar Teclado

Ir Para Pagamento
    Click Element    ${LOC_CHECKOUT_ADDRESS_TO_PAYMENT_BUTTON}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_PAYMENT_TITLE}

Preencher Dados De Pagamento
    [Documentation]    ${validade} só com números (MMAA): o app formata como MM/AA.
    [Arguments]    ${titular}    ${numero}    ${validade}    ${cvv}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_PAYMENT_CARD_HOLDER}
    Input Text    ${LOC_CHECKOUT_PAYMENT_CARD_HOLDER}    ${titular}
    Input Text    ${LOC_CHECKOUT_PAYMENT_CARD_NUMBER}    ${numero}
    Input Text    ${LOC_CHECKOUT_PAYMENT_EXPIRATION_DATE}    ${validade}
    Input Text    ${LOC_CHECKOUT_PAYMENT_SECURITY_CODE}    ${cvv}
    Ocultar Teclado

Revisar Pedido
    Click Element    ${LOC_CHECKOUT_PAYMENT_REVIEW_ORDER_BUTTON}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_REVIEW_PLACE_ORDER_BUTTON}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_TITLE}    ${MSG_CHECKOUT_REVIEW_TITLE}

Validar Dados De Entrega E Pagamento
    [Arguments]    ${nome}    ${endereco}    ${cep}    ${pais}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_DELIVERY_NAME}    ${nome}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_DELIVERY_ADDRESS}    ${endereco}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_DELIVERY_COUNTRY}    ${pais}, ${cep}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_CARD_HOLDER}    ${nome}

Validar Totais Do Pedido
    [Documentation]    ${total} inclui o frete de $ 5.99 (context/descobertas/comportamentos-observados.md).
    [Arguments]    ${quantidade}    ${total}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_TOTAL_ITEMS}    ${quantidade} Items
    Validar Texto Do Elemento    ${LOC_CHECKOUT_REVIEW_TOTAL_AMOUNT}    ${total}

Finalizar Pedido
    Click Element    ${LOC_CHECKOUT_REVIEW_PLACE_ORDER_BUTTON}
    Wait Until Element Is Visible    ${LOC_CHECKOUT_COMPLETE_TITLE}

Validar Pedido Concluído
    Validar Texto Do Elemento    ${LOC_CHECKOUT_COMPLETE_TITLE}    ${MSG_CHECKOUT_COMPLETE_TITLE}
    Validar Texto Do Elemento    ${LOC_CHECKOUT_COMPLETE_THANK_YOU}    ${MSG_CHECKOUT_THANK_YOU}
    Page Should Contain Element    ${LOC_CHECKOUT_COMPLETE_CONTINUE_SHOPPING_BUTTON}

Continuar Comprando
    Click Element    ${LOC_CHECKOUT_COMPLETE_CONTINUE_SHOPPING_BUTTON}
    Wait Until Element Is Visible    ${LOC_CATALOG_TITLE}
