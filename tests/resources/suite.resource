*** Settings ***
Documentation     Ponto único de import das suítes: recursos de execução, todas as páginas e o login como step de setup.
Resource          infraestrutura.resource
Resource          ../pages/catalogo.resource
Resource          ../pages/menu.resource
Resource          ../pages/login.resource
Resource          ../pages/produto.resource
Resource          ../pages/carrinho.resource
Resource          ../pages/finalizacao-compra.resource


*** Keywords ***
Iniciar App Autenticado
    [Documentation]    Test Setup padrão: sessão nova (app limpo pelas capabilities) + login com uma massa de
    ...                tests/massas/users.yaml. Termina na tela Products. O login é pré-requisito, não objeto de teste.
    ...                Outra massa num teste: [Setup]    Iniciar App Autenticado    <massa>
    [Arguments]    ${massa}=padrao
    Abrir Aplicativo
    Validar Tela De Produtos
    Abrir Menu Lateral
    Selecionar Login No Menu
    Validar Tela De Login
    Preencher Usuário    ${USUARIOS}[${massa}][usuario]
    Preencher Senha    ${USUARIOS}[${massa}][senha]
    Submeter Login
    Validar Tela De Produtos
