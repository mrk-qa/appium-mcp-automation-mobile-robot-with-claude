*** Settings ***
Documentation     Carrinho: adicionar um ou vários produtos e remover.
...               Cenários: context/cenarios/carrinho/*.md
Resource          ../../resources/suite.resource
Test Setup        Iniciar App Autenticado
Test Teardown     Encerrar Aplicativo
Test Tags         carrinho


*** Test Cases ***
CART-001 Adicionar um produto ao carrinho
    [Documentation]    Cenário: context/cenarios/carrinho/adicionar-um-produto.md
    [Tags]    adicionar-um-item
    VAR    ${produto}    Sauce Labs Backpack
    VAR    ${preco}      $ 29.99
    Validar Carrinho Vazio No Cabeçalho
    Selecionar Produto No Catálogo    ${produto}
    Validar Tela De Detalhes Do Produto    ${produto}    ${preco}
    Adicionar Produto Ao Carrinho
    Validar Quantidade No Ícone Do Carrinho    1
    Registrar Evidência    contador_carrinho
    Abrir Carrinho
    Validar Item No Carrinho    ${produto}    ${preco}    1
    Validar Totais Do Carrinho    1    ${preco}
    Registrar Evidência    item_no_carrinho

CART-002 Adicionar vários produtos ao carrinho
    [Documentation]    Cenário: context/cenarios/carrinho/adicionar-varios-produtos.md
    ...                SKIP enquanto existir o defeito "app fecha ao abrir o produto da 2ª posição do catálogo"
    ...                (context/descobertas/limitacoes-conhecidas.md). Volta a PASS quando o app for corrigido.
    [Tags]    adicionar-varios-itens    defeito-conhecido
    VAR    ${produto_1}          Sauce Labs Onesie
    VAR    ${preco_1}            $ 7.99
    VAR    ${produto_2}          Sauce Labs Bike Light
    VAR    ${preco_2}            $ 9.99
    VAR    ${total_esperado}     $ 17.98
    Ordenar Catálogo Por    Price - Ascending
    Selecionar Produto No Catálogo    ${produto_1}
    Adicionar Produto Ao Carrinho
    Voltar Para O Catálogo
    Selecionar Produto No Catálogo    ${produto_2}
    Adicionar Produto Ao Carrinho
    Validar Quantidade No Ícone Do Carrinho    2
    Registrar Evidência    contador_carrinho
    Abrir Carrinho
    Validar Produto Listado    ${produto_1}    ${preco_1}
    Validar Produto Listado    ${produto_2}    ${preco_2}
    Validar Totais Do Carrinho    2    ${total_esperado}
    Registrar Evidência    itens_no_carrinho

CART-003 Remover produto do carrinho
    [Documentation]    Cenário: context/cenarios/carrinho/remover-produto.md
    [Tags]    remover-item
    VAR    ${produto}    Sauce Labs Backpack
    VAR    ${preco}      $ 29.99
    Selecionar Produto No Catálogo    ${produto}
    Adicionar Produto Ao Carrinho
    Abrir Carrinho
    Validar Item No Carrinho    ${produto}    ${preco}    1
    Registrar Evidência    carrinho_com_item
    Remover Produto Do Carrinho
    Validar Carrinho Vazio
    Registrar Evidência    carrinho_vazio

CART-004 Carrinho vazio exibe a mensagem de carrinho sem itens
    [Documentation]    Cenário: context/cenarios/carrinho/carrinho-vazio.md
    [Tags]    carrinho-vazio
    VAR    ${produto}    Sauce Labs Backpack
    VAR    ${preco}      $ 29.99
    Selecionar Produto No Catálogo    ${produto}
    Adicionar Produto Ao Carrinho
    Abrir Carrinho
    Validar Item No Carrinho    ${produto}    ${preco}    1
    Remover Produto Do Carrinho
    Validar Tela De Carrinho Sem Itens
    Registrar Evidência    carrinho_sem_itens
    Voltar Às Compras
    Validar Carrinho Vazio No Cabeçalho
    Registrar Evidência    catalogo
