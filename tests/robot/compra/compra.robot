*** Settings ***
Documentation     Compra com sucesso: checkout completo com um e com vários produtos.
...               Cenários: context/cenarios/compra/*.md
Resource          ../../resources/suite.resource
Test Setup        Iniciar App Autenticado
Test Teardown     Encerrar Aplicativo
Test Tags         compra


*** Variables ***
# Dados FICTÍCIOS de entrega e pagamento, comuns a todas as compras (o app não processa pagamento real).
${NOME}              QA Tester
${ENDERECO}          Rua de Teste 100
${CIDADE}            Sao Paulo
${CEP}               01000-000
${PAIS}              Brazil
${CARTAO_NUMERO}     4111111111111111
${CARTAO_VALIDADE}   1230
${CARTAO_CVV}        123


*** Test Cases ***
BUY-001 Compra de um produto com sucesso
    [Documentation]    Cenário: context/cenarios/compra/compra-um-produto.md
    [Tags]    compra-de-um-item
    VAR    ${produto}            Sauce Labs Backpack
    VAR    ${preco}              $ 29.99
    VAR    ${total_esperado}     $ 35.98    # $ 29.99 + frete $ 5.99
    Selecionar Produto No Catálogo    ${produto}
    Adicionar Produto Ao Carrinho
    Abrir Carrinho
    Validar Item No Carrinho    ${produto}    ${preco}    1
    Iniciar Checkout
    Preencher Endereço De Entrega    ${NOME}    ${ENDERECO}    ${CIDADE}    ${CEP}    ${PAIS}
    Registrar Evidência    endereco_entrega
    Ir Para Pagamento
    Preencher Dados De Pagamento    ${NOME}    ${CARTAO_NUMERO}    ${CARTAO_VALIDADE}    ${CARTAO_CVV}
    Registrar Evidência    pagamento
    Revisar Pedido
    Validar Produto Listado    ${produto}    ${preco}
    Validar Dados De Entrega E Pagamento    ${NOME}    ${ENDERECO}    ${CEP}    ${PAIS}
    Validar Totais Do Pedido    1    ${total_esperado}
    Registrar Evidência    revisao_pedido
    Finalizar Pedido
    Validar Pedido Concluído
    Registrar Evidência    pedido_concluido
    Continuar Comprando
    Validar Carrinho Vazio No Cabeçalho
    Registrar Evidência    catalogo_apos_compra

BUY-002 Compra de vários produtos com sucesso
    [Documentation]    Cenário: context/cenarios/compra/compra-varios-produtos.md
    ...                SKIP enquanto existir o defeito "app fecha ao abrir o produto da 2ª posição do catálogo"
    ...                (context/descobertas/limitacoes-conhecidas.md). Volta a PASS quando o app for corrigido.
    [Tags]    compra-de-varios-itens    defeito-conhecido
    VAR    ${produto_1}          Sauce Labs Onesie
    VAR    ${preco_1}            $ 7.99
    VAR    ${produto_2}          Sauce Labs Bike Light
    VAR    ${preco_2}            $ 9.99
    VAR    ${total_esperado}     $ 23.97    # $ 7.99 + $ 9.99 + frete $ 5.99
    Ordenar Catálogo Por    Price - Ascending
    Selecionar Produto No Catálogo    ${produto_1}
    Adicionar Produto Ao Carrinho
    Voltar Para O Catálogo
    Selecionar Produto No Catálogo    ${produto_2}
    Adicionar Produto Ao Carrinho
    Abrir Carrinho
    Validar Produto Listado    ${produto_1}    ${preco_1}
    Validar Produto Listado    ${produto_2}    ${preco_2}
    Iniciar Checkout
    Preencher Endereço De Entrega    ${NOME}    ${ENDERECO}    ${CIDADE}    ${CEP}    ${PAIS}
    Ir Para Pagamento
    Preencher Dados De Pagamento    ${NOME}    ${CARTAO_NUMERO}    ${CARTAO_VALIDADE}    ${CARTAO_CVV}
    Revisar Pedido
    Validar Totais Do Pedido    2    ${total_esperado}
    Registrar Evidência    revisao_pedido
    Validar Produto Listado    ${produto_1}    ${preco_1}
    Validar Produto Listado    ${produto_2}    ${preco_2}
    Finalizar Pedido
    Validar Pedido Concluído
    Registrar Evidência    pedido_concluido
    Continuar Comprando
    Validar Carrinho Vazio No Cabeçalho
    Registrar Evidência    catalogo_apos_compra
