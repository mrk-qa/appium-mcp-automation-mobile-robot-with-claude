*** Settings ***
Documentation     Tela de login
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# login
${LOC_LOGIN_TITLE}               id=com.saucelabs.mydemoapp.android:id/loginTV    # texto "Login"
${LOC_LOGIN_USERNAME}            id=com.saucelabs.mydemoapp.android:id/nameET
${LOC_LOGIN_PASSWORD}            id=com.saucelabs.mydemoapp.android:id/passwordET
${LOC_LOGIN_SUBMIT_BUTTON}       id=com.saucelabs.mydemoapp.android:id/loginBtn    # texto "Login"
${LOC_LOGIN_USERNAME_ERROR}      id=com.saucelabs.mydemoapp.android:id/nameErrorTV
${LOC_LOGIN_PASSWORD_ERROR}      id=com.saucelabs.mydemoapp.android:id/passwordErrorTV    # Também exibe o erro de usuário bloqueado.
${LOC_LOGIN_DEMO_USER_BOD}       id=com.saucelabs.mydemoapp.android:id/username1TV    # NÃO VALIDADO
${LOC_LOGIN_DEMO_USER_LOCKED}    id=com.saucelabs.mydemoapp.android:id/username2TV    # NÃO VALIDADO

# mensagens exibidas pelo app
${MSG_USERNAME_REQUIRED}    Username is required
${MSG_PASSWORD_REQUIRED}    Enter Password
${MSG_USER_LOCKED}          Sorry this user has been locked out.


*** Keywords ***
Validar Tela De Login
    Wait Until Element Is Visible    ${LOC_LOGIN_TITLE}
    Validar Texto Do Elemento    ${LOC_LOGIN_TITLE}    Login
    Wait Until Element Is Visible    ${LOC_LOGIN_USERNAME}
    Wait Until Element Is Visible    ${LOC_LOGIN_PASSWORD}

Preencher Usuário
    [Arguments]    ${usuario}
    Clear Text    ${LOC_LOGIN_USERNAME}
    Run Keyword If    $usuario    Input Text    ${LOC_LOGIN_USERNAME}    ${usuario}
    Ocultar Teclado

Preencher Senha
    [Documentation]    Usa Input Password: o valor não aparece no log.
    [Arguments]    ${senha}
    Clear Text    ${LOC_LOGIN_PASSWORD}
    Run Keyword If    $senha    Input Password    ${LOC_LOGIN_PASSWORD}    ${senha}
    Ocultar Teclado

Submeter Login
    Click Element    ${LOC_LOGIN_SUBMIT_BUTTON}

Validar Erro De Usuário
    [Arguments]    ${mensagem}
    Wait Until Element Is Visible    ${LOC_LOGIN_USERNAME_ERROR}
    Validar Texto Do Elemento    ${LOC_LOGIN_USERNAME_ERROR}    ${mensagem}

Validar Erro De Senha
    [Documentation]    O campo de erro de senha também exibe a mensagem de usuário bloqueado.
    [Arguments]    ${mensagem}
    Wait Until Element Is Visible    ${LOC_LOGIN_PASSWORD_ERROR}
    Validar Texto Do Elemento    ${LOC_LOGIN_PASSWORD_ERROR}    ${mensagem}

Validar Permanência Na Tela De Login
    Wait Until Element Is Visible    ${LOC_LOGIN_TITLE}
    Page Should Not Contain Element    ${LOC_CATALOG_TITLE}
