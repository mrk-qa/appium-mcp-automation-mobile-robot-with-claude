*** Settings ***
Documentation     Menu lateral e logout
...               Locators em *** Variables *** (resource-id > accessibility id > UiSelector/xpath);
...               "# NÃO VALIDADO" = só observado na exploração; remover após passar no Robot.
Resource          ../resources/infraestrutura.resource


*** Variables ***
# navigation_drawer
${LOC_NAVIGATION_DRAWER_CONTAINER}      id=com.saucelabs.mydemoapp.android:id/drawerMenu
${LOC_NAVIGATION_DRAWER_LIST}           id=com.saucelabs.mydemoapp.android:id/menuRV
${LOC_NAVIGATION_DRAWER_LOGIN_ITEM}     accessibility_id=Login Menu Item    # texto "Log In"
${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}    accessibility_id=Logout Menu Item    # texto "Log Out"

# logout_dialog
${LOC_LOGOUT_DIALOG_TITLE}              id=com.saucelabs.mydemoapp.android:id/alertTitle    # texto "Log Out"
${LOC_LOGOUT_DIALOG_MESSAGE}            id=android:id/message    # texto "Are you sure you want to logout"
${LOC_LOGOUT_DIALOG_CONFIRM_BUTTON}     id=android:id/button1    # texto "LOGOUT"
${LOC_LOGOUT_DIALOG_CANCEL_BUTTON}      id=android:id/button2    # NÃO VALIDADO; texto "CANCEL"

# mensagens exibidas pelo app
${MSG_LOGOUT_CONFIRMATION}    Are you sure you want to logout


*** Keywords ***
Abrir Menu Lateral
    Click Element    ${LOC_CATALOG_MENU_BUTTON}
    Wait Until Element Is Visible    ${LOC_NAVIGATION_DRAWER_LIST}

Fechar Menu Lateral
    Go Back
    Wait Until Page Does Not Contain Element    ${LOC_NAVIGATION_DRAWER_LIST}

Selecionar Login No Menu
    Wait Until Element Is Visible    ${LOC_NAVIGATION_DRAWER_LOGIN_ITEM}
    Click Element    ${LOC_NAVIGATION_DRAWER_LOGIN_ITEM}

Validar Menu De Usuário Autenticado
    [Documentation]    Requer menu aberto. Critério: "Log Out" presente e "Log In" ausente.
    Wait Until Element Is Visible    ${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}
    Validar Texto Do Elemento    ${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}    Log Out
    Page Should Not Contain Element    ${LOC_NAVIGATION_DRAWER_LOGIN_ITEM}

Validar Menu De Usuário Não Autenticado
    [Documentation]    Requer menu aberto. Critério: "Log In" presente e "Log Out" ausente.
    Wait Until Element Is Visible    ${LOC_NAVIGATION_DRAWER_LOGIN_ITEM}
    Page Should Not Contain Element    ${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}

Selecionar Logout No Menu
    Wait Until Element Is Visible    ${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}
    Click Element    ${LOC_NAVIGATION_DRAWER_LOGOUT_ITEM}
    Wait Until Element Is Visible    ${LOC_LOGOUT_DIALOG_MESSAGE}
    Validar Texto Do Elemento    ${LOC_LOGOUT_DIALOG_MESSAGE}    ${MSG_LOGOUT_CONFIRMATION}

Confirmar Logout
    Click Element    ${LOC_LOGOUT_DIALOG_CONFIRM_BUTTON}
    Wait Until Page Does Not Contain Element    ${LOC_LOGOUT_DIALOG_MESSAGE}
