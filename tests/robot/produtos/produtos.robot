*** Settings ***
Documentation     Página de produtos: catálogo, detalhes e ordenação.
...               Cenários: context/cenarios/produtos/*.md
Resource          ../../resources/suite.resource
Test Setup        Iniciar App Autenticado
Test Teardown     Encerrar Aplicativo
Test Tags         produtos


*** Test Cases ***
PROD-001 Catálogo exibe os produtos com nome e preço
    [Documentation]    Cenário: context/cenarios/produtos/catalogo.md
    [Tags]    listagem-de-produtos
    VAR    ${backpack}       Sauce Labs Backpack
    VAR    ${backpack_preco}    $ 29.99
    VAR    ${bike_light}     Sauce Labs Bike Light
    VAR    ${bike_light_preco}    $ 9.99
    VAR    ${onesie}         Sauce Labs Onesie
    VAR    ${onesie_preco}    $ 7.99
    Validar Tela De Produtos
    Validar Produto No Catálogo    ${backpack}    ${backpack_preco}
    Registrar Evidência    catalogo
    Validar Produto No Catálogo    ${bike_light}    ${bike_light_preco}
    Validar Produto No Catálogo    ${onesie}    ${onesie_preco}
    Registrar Evidência    catalogo_rolado

PROD-002 Detalhes do produto exibem nome, preço e quantidade
    [Documentation]    Cenário: context/cenarios/produtos/detalhes-produto.md
    [Tags]    detalhes-do-produto
    VAR    ${produto}    Sauce Labs Backpack
    VAR    ${preco}      $ 29.99
    Selecionar Produto No Catálogo    ${produto}
    Validar Tela De Detalhes Do Produto    ${produto}    ${preco}
    Registrar Evidência    detalhes_produto

PROD-003 Ordenar catálogo por preço crescente
    [Documentation]    Cenário: context/cenarios/produtos/ordenacao-por-preco.md
    [Tags]    ordenacao-por-preco
    VAR    ${mais_barato}          Sauce Labs Onesie
    VAR    ${mais_barato_preco}    $ 7.99
    Ordenar Catálogo Por    Price - Ascending
    Validar Primeiro Produto Do Catálogo    ${mais_barato}    ${mais_barato_preco}
    Validar Preços Em Ordem Crescente
    Registrar Evidência    ordenado_preco_crescente
