*** Settings ***
Documentation     Configurações comuns a todas as suítes de tests/robot/.
...               Test Timeout: nenhum teste pode passar de 5 minutos; ao estourar, o teste falha com a
...               mensagem de timeout do Robot e o Test Teardown (Encerrar Aplicativo) ainda roda.
Test Timeout      5 minutes
