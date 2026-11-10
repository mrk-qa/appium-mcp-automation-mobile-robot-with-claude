*** Settings ***
Documentation     Recursos de execução: sessão Appium por teste e evidências.
...               O que é configuração fica fora das keywords:
...               - app limpo (deslogado, carrinho vazio): appium:noReset=false em tests/config/capabilities.json,
...                 aplicado pelo UiAutomator2 a cada sessão nova (uma por teste);
...               - timeout único: ${TIMEOUT} (30s) vale para todas as esperas do AppiumLibrary e para as
...                 retentativas; para outro app, rode com --variable TIMEOUT:<valor>;
...               - pasta de evidências: <outputdir>/screenshots/<ID do teste>/, preparada pelo listener
...                 (tests/libs/summary_listener.py, registrado em tests/robot.args).
Library           Collections
Library           String
Library           AppiumLibrary    timeout=${TIMEOUT}    run_on_failure=No Operation
Variables         ../libs/app_context.py


*** Variables ***
# Timeout único do projeto: esperas do AppiumLibrary (Wait Until ...) e retentativas de leitura.
# Sobrescreva na linha de comando para apps mais lentos: --variable TIMEOUT:60s
${TIMEOUT}    30s


*** Keywords ***
Abrir Aplicativo
    [Documentation]    Abre uma sessão nova. Com appium:noReset=false o UiAutomator2 para o app e limpa os dados
    ...                antes de abrir, então todo teste começa deslogado e com o carrinho vazio.
    Open Application    ${APPIUM_URL}    &{CAPABILITIES}

Encerrar Aplicativo
    [Documentation]    Test Teardown: registra a evidência "falha" se o teste não passou e encerra a sessão.
    ...                Usa ${TEST STATUS} != PASS (e não "Run Keyword If Test Failed") porque, com
    ...                --skiponfailure defeito-conhecido, o status já é SKIP quando o teardown roda.
    IF    $TEST_STATUS != 'PASS'
        Run Keyword And Ignore Error    Registrar Evidência    falha
    END
    Close All Applications

Registrar Evidência
    [Documentation]    Screenshot numerado em <outputdir>/screenshots/<ID>/NN_<nome>.png, exibido inline no log.html.
    ...                O caminho relativo é resolvido pelo AppiumLibrary a partir do --outputdir.
    [Arguments]    ${nome}
    ${anterior}=    Get Variable Value    ${EVIDENCIA_NUMERO}    ${0}
    VAR    ${EVIDENCIA_NUMERO}    ${anterior + 1}    scope=TEST    # robocop: off=VAR06  numeração das evidências precisa durar o teste inteiro
    Capture Page Screenshot    screenshots/${TEST NAME.split()[0]}/${{ str($EVIDENCIA_NUMERO).zfill(2) }}_${nome}.png

Validar Texto Do Elemento
    [Documentation]    Element Text Should Be com retentativa a cada 500ms até ${TIMEOUT}. Cobre a transição de tela:
    ...                texto ainda da tela anterior (ids reutilizados entre telas) e elemento recriado (stale).
    [Arguments]    ${locator}    ${texto}
    Wait Until Keyword Succeeds    ${TIMEOUT}    500ms    Element Text Should Be    ${locator}    ${texto}

Ocultar Teclado
    Run Keyword And Ignore Error    Hide Keyboard
