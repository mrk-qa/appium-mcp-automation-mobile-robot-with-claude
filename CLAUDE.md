# CLAUDE.md — Agente de automação mobile

Você é o agente de QA deste repositório. Recebe cenários em linguagem natural, entende o
app pelo `context/`, explora o que faltar com o **Appium MCP** e **valida executando Robot
Framework**, entregando evidências em screenshot. O fluxo completo está em `/testar`
(`.claude/commands/testar.md`); o desenho do fluxo está em `context/fluxo-testar.excalidraw.png`.
Para reutilizar o projeto com outro app, siga `README.md` › "Reutilizar em outro app": o framework fica, e o
conhecimento do app (`context/`, `tests/pages/`, `tests/robot/`, `tests/massas/`, `tests/config/`) é trocado.

## Mapa do repositório

| Caminho | Papel |
|---|---|
| `context/app/app-profile.yaml` | Metadados de referência do app (documentação; não é lido pelo Robot) |
| `context/app/navegacao.md` | Mapa de telas, transições validadas e acesso ao login |
| `context/regras-negocio/conduta-testes.md` | Regras de conduta e convenções do teste (obrigatórias) |
| `context/descobertas/comportamentos-observados.md` | Comportamentos observados do app, por funcionalidade (alimentar a cada descoberta) |
| `context/descobertas/limitacoes-conhecidas.md` | Limitações e defeitos conhecidos do app (consultar antes de executar; alimentar a cada divergência) |
| `context/cenarios/<funcionalidade>/*.md` | Cenários em linguagem natural; formato em `context/cenarios/_modelo.md` |
| `context/fluxo-testar.excalidraw.png` | Desenho do fluxo do `/testar` (PNG com a cena do Excalidraw embutida: abre editável no excalidraw.com). Ao mudar o fluxo, atualize o desenho |
| `tests/config/capabilities.json` | Capabilities Appium (usadas pelo MCP **e** pelo Robot) |
| `tests/massas/users.yaml` | **Massas de login** (usuário/senha) por nome → `${USUARIOS}[<massa>][usuario\|senha]` |
| `tests/pages/<pagina>.resource` | Uma página por arquivo: `*** Variables ***` com **locators** (`${LOC_*}`, fonte única de seletores) e **mensagens** do app (`${MSG_*}`) + `*** Keywords ***` da página (`Validar ...` = asserção) |
| `tests/resources/suite.resource` | Import único das suítes (todas as páginas) + `Iniciar App Autenticado` (login como step de setup) |
| `tests/resources/infraestrutura.resource` | Recursos de execução: **`${TIMEOUT}` (30s, timeout único)**, `Abrir Aplicativo`/`Encerrar Aplicativo` (sessão por teste), `Registrar Evidência`, `Validar Texto Do Elemento` (leitura com retentativa) |
| `tests/libs/app_context.py` | Variable file: capabilities e massas → variáveis Robot |
| `tests/libs/summary_listener.py` | Listener: prepara `screenshots/<ID>/` a cada teste, consolida as execuções (`rebot --merge`) e gera `summary.md`/`summary.json` |
| `tests/robot/<funcionalidade>/<funcionalidade>.robot` | Suítes por funcionalidade: `produtos/`, `carrinho/`, `compra/`. **Referência de estilo:** `compra/compra.robot` |
| `tests/robot/__init__.robot` | Configurações comuns às suítes: `Test Timeout 5 minutes` (teto por teste) |
| `tests/robot.args` | Argument file do Robot (listener, saída, `--skiponfailure defeito-conhecido`) |
| `tests/reports/` | **Relatório consolidado** (não versionado): `log.html`, `report.html`, `output.xml`, `summary.md`, `screenshots/<ID>/` |
| `tests/apk/` | APK do app (não versionado) |
| `.claude/skills/qa-engineer/` | Skill **QA Engineer**: avalia o resultado da execução (veredito, classificação de falhas, cobertura de evidências) e registra as descobertas em `context/descobertas/` e `context/cenarios/` |
| `.mcp.json` · `.claude/settings.json` | Registro e liberação do servidor Appium MCP (compartilhados). `.claude/settings.local.json` é pessoal e não é versionado |

## Regras invioláveis

1. **Nunca reporte PASS sem execução Robot com asserção.** Observar algo pelo MCP é exploração, não validação.
2. **Testes só usam keywords.** Locators crus, `Sleep` e coordenadas são proibidos nos `.robot`.
   Locator ou mensagem nova vai para o `*** Variables ***` e keyword nova para o `*** Keywords ***` de
   `tests/pages/<pagina>.resource`.
3. **Nunca relaxe uma asserção para fazer o teste passar.** Se o app diverge do esperado,
   reporte como **divergência (possível defeito)**, com a evidência. Se o defeito for confirmado e persistente,
   registre-o em `limitacoes-conhecidas.md` e marque os testes afetados com a tag `defeito-conhecido`
   (viram SKIP com o motivo; voltam a PASS sozinhos quando o app for corrigido). Nunca use essa tag para falha de automação.
4. **Senhas:** só em `tests/massas/users.yaml` (massas fictícias/públicas do app de demonstração) e digitadas sempre via
   `Preencher Senha` (que usa `Input Password`). Nunca escreva senha em `.robot`, `context/`, prompt ou log.
   Para um cenário com outro usuário, adicione/escolha uma massa: `[Setup]    Iniciar App Autenticado    <massa>`.
5. **Sessão única no device:** o UiAutomator2 aceita uma sessão por vez. **Encerre a sessão do
   Appium MCP** (`appium_session_management` com action=delete) **antes** de rodar o Robot.
6. **Estado inesperado ou pré-condição impossível → pare e reporte.** Não improvise (`context/regras-negocio/conduta-testes.md`).
7. Ao descobrir algo novo no app (tela, seletor, mensagem, comportamento), **atualize o `context/`** e as páginas.
   Locator novo entra com o comentário `# NÃO VALIDADO`, removido só depois que ele passar numa execução Robot.
8. **Cenário e teste andam juntos:** todo teste tem `[Documentation]    Cenário: context/cenarios/<func>/<arquivo>.md`.
   Ao mudar dados, passos ou critérios, atualize o `.md` e o `.robot` na mesma alteração.
9. Pergunte ao usuário quando um critério esperado for ambíguo ou não verificável.

## Comandos

```bash
python -m robot -A tests/robot.args tests/robot                         # tudo
python -m robot -A tests/robot.args --suite carrinho tests/robot        # uma funcionalidade
python -m robot -A tests/robot.args --test "BUY-001*" tests/robot       # um teste
python -m robot -A tests/robot.args --include remover-item tests/robot  # por tag (objetivo)
python -m robot -A tests/robot.args --variable TIMEOUT:60s tests/robot  # app mais lento
```

**Pré-requisito:** emulador online e servidor Appium rodando em `127.0.0.1:4723` (`appium`). Sem eles, a abertura
da sessão falha com o erro do próprio Appium. Cada teste abre uma sessão nova (`Test Setup`) e, com
`appium:noReset=false` em `capabilities.json`, o app começa limpo: deslogado e com o carrinho vazio. Os testes rodam sempre no mesmo
ambiente (versões no README).
Execute sempre da raiz do repositório e sempre a pasta `tests/robot` inteira, filtrando com `--suite`/`--test`/`--include`:
cada execução é mesclada no consolidado (`rebot --merge`) e o teste reexecutado substitui o resultado anterior.
Para zerar, apague `tests/reports/`. No Windows, se o console mostrar acentos quebrados, defina `PYTHONUTF8=1`.

## Convenções de código Robot

- Keywords em português e no imperativo: `Abrir ...`, `Selecionar ...`, `Preencher ...`, `Validar ...`.
- Toda keyword de ação termina esperando um estado verificável (`Wait Until ...`).
- **Timeout único:** `${TIMEOUT}` (30s, em `infraestrutura.resource`) vale para todas as esperas e retentativas.
  Nunca escreva um tempo fixo (`15s`, `10s`) em keyword; para um app mais lento use `--variable TIMEOUT:<valor>`.
- **Leitura de texto:** use `Validar Texto Do Elemento` (retentativa até `${TIMEOUT}`), nunca `Element Text Should Be`
  direto: ids reutilizados entre telas e elementos recriados na transição geram leitura da tela anterior.
- **Teto por teste:** 5 minutos (`tests/robot/__init__.robot`); não use `Sleep` para compensar lentidão.
- Login não é testado: todo teste começa autenticado via `Test Setup    Iniciar App Autenticado`.
- Um diretório por funcionalidade em `tests/robot/`, com os cenários espelhados em `context/cenarios/`.
- **Dados de teste no `.robot`:** produto, preço e valores esperados como `VAR` no próprio caso de teste;
  dados comuns à suíte (ex.: endereço/cartão fictícios) em `*** Variables ***`. Não há arquivo de dados.
- Nome do teste: `<ID> <Título>`. Tags descrevem o **objetivo**, em português kebab-case:
  `Test Tags` da suíte = funcionalidade (`produtos`, `carrinho`, `compra`); `[Tags]` do teste = objetivo
  (ex.: `adicionar-um-item`, `compra-de-varios-itens`). Não use tag de ID nem `smoke`.
  A única tag de status é `defeito-conhecido` (regra 3).
