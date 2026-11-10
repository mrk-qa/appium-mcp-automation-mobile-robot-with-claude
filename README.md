# Automation Mobile Appium MCP

Automação mobile Android guiada por IA. Você descreve cenários de teste em linguagem
natural, e o **Claude Code** interpreta, consulta o contexto do app, explora telas novas
com o **Appium MCP**, gera e executa suítes **Robot Framework** e devolve o resultado com
**screenshots como evidência**.

App de exemplo: **Sauce Labs My Demo App 2.3.0** (`com.saucelabs.mydemoapp.android`).

## Como funciona

![Fluxo do /testar-cenarios: você descreve o cenário; o Claude interpreta, carrega o contexto, explora telas novas com o Appium MCP quando falta keyword, gera a suíte e executa o Robot Framework, que faz login com a massa, valida, captura evidências e consolida o relatório; o Claude analisa as falhas e reporta.](context/fluxo-testar-cenarios.excalidraw.png)

O desenho tem uma raia por participante: você, o agente (`/testar-cenarios`), o Appium MCP com o emulador, o
Robot Framework e os arquivos do projeto. Ele segue os 8 passos do comando. As setas tracejadas são as únicas
interações com você no meio do fluxo: uma pergunta quando o critério é ambíguo e um aviso quando o cenário
esbarra numa limitação conhecida.

**Para editar o desenho:** abra [excalidraw.com](https://excalidraw.com) e arraste o arquivo
`context/fluxo-testar-cenarios.excalidraw.png` para a tela (ou use a extensão Excalidraw do VS Code). O PNG
carrega a cena do Excalidraw embutida, então abre editável. Depois de editar, exporte de novo como PNG com
**"Embed scene"** marcado e salve com o mesmo nome.

- **Appium MCP** = exploração (descobrir telas e seletores). **Robot** = validação determinística.
- Três **portões** garantem a qualidade: a **Definition of Ready** do `product-owner` antes de automatizar, a
  **revisão** do `revisor-robot` antes de executar e a **análise** do `avaliador-de-execucao` depois da execução.
- `tests/pages/<pagina>.resource` concentra locators e mensagens (`*** Variables ***`) e as keywords de cada página: é a fonte única de seletores. Os testes nunca usam locators crus.

## Estrutura

```
context/                              conhecimento do app e cenários (lido pela IA)
  app/
    app-profile.yaml                  metadados de referência do app
    navegacao.md                      mapa de telas e transições
  regras-negocio/
    conduta-testes.md                 regras de conduta e convenções dos testes
    produtos.md, carrinho.md, compra.md  regras de negócio do app (RN-*), citadas pelos cenários
  descobertas/                        alimentados a cada nova descoberta
    comportamentos-observados.md      comportamentos observados, por funcionalidade
    limitacoes-conhecidas.md          limitações e defeitos conhecidos do app
  cenarios/                           cenários em linguagem natural (mesmas pastas de tests/robot/)
    _modelo.md, produtos/, carrinho/, compra/
  fluxo-testar-cenarios.excalidraw.png  desenho do fluxo do /testar-cenarios (PNG com a cena do Excalidraw)
tests/                                tudo que é executado ou gerado pelos testes
  config/
    capabilities.json                 capabilities Appium (MCP + Robot)
  massas/users.yaml                   massas de login (usuário/senha) usadas pelos cenários
  pages/<pagina>.resource             locators + mensagens + keywords de cada página
  resources/                          recursos necessários para a execução
    suite.resource                    import único das suítes + login como setup
    infraestrutura.resource           sessão por teste, evidências, ${TIMEOUT}, leitura com retentativa
  libs/
    app_context.py                    variable file: capabilities e massas
    summary_listener.py               listener: consolida execuções e gera summary.md
  robot/                              suítes por funcionalidade (dados de teste dentro do .robot)
    __init__.robot                    configurações comuns: Test Timeout de 5 minutos
    produtos/produtos.robot           catálogo, detalhes e ordenação   (PROD-*)
    carrinho/carrinho.robot           adicionar, remover e carrinho vazio (CART-*)
    compra/compra.robot               compra com sucesso                (BUY-*)
  reports/                            relatório consolidado de todas as execuções (não versionado)
  apk/                                APK do app (não versionado; pasta mantida pelo .gitkeep)
  robot.args                          argument file do Robot
  requirements.txt                    dependências Python (versões fixas)
CLAUDE.md                             regras do agente (lido pelo Claude Code em toda sessão)
.claude/commands/testar-cenarios.md   comando /testar-cenarios
.claude/skills/product-owner/         skill Product Owner: regras de negócio e Definition of Ready
.claude/skills/analista-de-testes/    skill Analista de Testes: matriz de cobertura e cenários propostos
.claude/skills/avaliador-de-execucao/ skill Avaliador de Execução (SKILL.md, script de coleta e README)
.claude/agents/revisor-robot.md       subagente Revisor Robot: code review dos testes antes de executar
.claude/scripts/                      lint_robot.py (convenções + Robocop + dry-run), validar_cenarios.py (DoR)
.claude/hooks/                        proteger_senhas, validar_apos_edicao, portao_execucao
.claude/settings.json                 libera o servidor appium-mcp e registra os hooks (compartilhado)
robocop.toml                          configuração do Robocop (lint Robot)
.mcp.json                             registro do servidor Appium MCP no Claude Code (obrigatório)
.gitignore, .gitattributes            o que não é versionado; fins de linha e binários
```

## Agente: comando, personas e guardrails

O `/testar-cenarios` conduz o fluxo e aciona quatro personas, cada uma com um papel e um limite do que pode alterar:

| Persona | Tipo · arquivo | Quando | Decide | Escreve em |
|---|---|---|---|---|
| **Product Owner** | skill · `.claude/skills/product-owner/` ([guia](.claude/skills/product-owner/README.md)) | passo 1, ou `/product-owner` | **O que** é verdade: regras de negócio e cenário pronto (DoR) | `context/regras-negocio/`, `context/cenarios/` |
| **Analista de Testes** | skill · `.claude/skills/analista-de-testes/` ([guia](.claude/skills/analista-de-testes/README.md)) | funcionalidade nova, ou `/analista-de-testes` | **Quanto** testar: matriz, lacunas, cenários propostos | `context/cenarios/` (só `proposto`) |
| **Revisor Robot** (Dev/SDET) | subagente · `.claude/agents/revisor-robot.md` | passo 5, antes de executar | Se o `.robot` prova o cenário e segue as convenções | nada (só grava a aprovação) |
| **Avaliador de Execução** | skill · `.claude/skills/avaliador-de-execucao/` ([guia](.claude/skills/avaliador-de-execucao/README.md)) | passo 7, depois de executar | Se o resultado é confiável: veredito e descobertas | `context/descobertas/`, `context/cenarios/` |

O revisor é um **subagente** (contexto próprio) de propósito: ele não escreveu o código que revisa.

**Guardrails determinísticos** (hooks em `.claude/settings.json`, valem para o agente, não para o seu terminal):

| Hook | Evento | Faz |
|---|---|---|
| `proteger_senhas` | antes de escrever ou rodar comando | Bloqueia conteúdo com a senha de uma massa fora de `tests/massas/users.yaml` (regra 4) |
| `validar_apos_edicao` | depois de editar | `.robot`/`.resource` → `lint_robot.py`; cenário/regra `.md` → `validar_cenarios.py`; erro volta ao agente na hora |
| `portao_execucao` | antes de rodar comando | Bloqueia `python -m robot` se os `.robot`/`.resource` mudaram desde a última aprovação do `revisor-robot` |

Validações que você também pode rodar à mão:

```bash
python .claude/scripts/lint_robot.py                                  # R01–R18 + Robocop + dry-run do Robot
python .claude/scripts/validar_cenarios.py                            # estrutura de cenários e regras (DoR)
python .claude/skills/analista-de-testes/scripts/matriz_cobertura.py  # regra × cenário × teste × último resultado
```

As regras que todos seguem estão no `CLAUDE.md` (regras invioláveis e convenções de código Robot).

## Pré-requisitos

- Android SDK (`ANDROID_HOME` definido) e emulador rodando (`adb devices` → `emulator-5554 device`)
- My Demo App 2.3.0 instalado: baixe `mda-2.3.0-27.apk` da
  [release oficial](https://github.com/saucelabs/my-demo-app-android/releases/tag/2.3.0) para `tests/apk/` e
  rode `adb install tests/apk/mda-2.3.0-27.apk`
- Node.js 22.14.0, Appium 2.16.2 e driver UiAutomator2 4.0.3
- Python 3.11.9 e Claude Code

Os testes rodam sempre neste ambiente; use exatamente estas versões.

## Configuração

```bash
npm install -g appium@2.16.2
appium driver install uiautomator2@4.0.3
pip install -r tests/requirements.txt
```

Antes de executar, deixe o emulador online e o servidor Appium rodando em outro terminal:

```bash
appium
```

Abra o Claude Code na pasta do projeto, aprove o servidor `appium-mcp` do `.mcp.json` e
confira com `/mcp` se ele está conectado.
Os hooks de `.claude/settings.json` usam o `python` do PATH (o mesmo do Robot e do Robocop); confira com `/hooks`.

Não há `.env`: as massas de login estão em `tests/massas/users.yaml` e o device em
`tests/config/capabilities.json`. Para outro servidor Appium: `--variable APPIUM_URL:<url>`.

## Uso

**Pela IA (fluxo principal):**

```
/testar-cenarios context/cenarios/carrinho/
/testar-cenarios Adicionar "Sauce Labs Backpack" ao carrinho e validar que o badge mostra 1
```

**Execução direta das suítes** (Robot puro, a partir da raiz do repositório):

```bash
python -m robot -A tests/robot.args tests/robot                         # tudo
python -m robot -A tests/robot.args --suite carrinho tests/robot            # uma funcionalidade
python -m robot -A tests/robot.args --test "BUY-001*" tests/robot       # um teste
python -m robot -A tests/robot.args --include remover-item tests/robot  # por objetivo (tag)
python -m robot -A tests/robot.args --variable TIMEOUT:60s tests/robot  # app mais lento
```

Todo teste começa autenticado (`Test Setup    Iniciar App Autenticado`): o login é um step, não um
cenário. Por padrão o login usa a massa `padrao` de `tests/massas/users.yaml`; para outra massa num teste:
`[Setup]    Iniciar App Autenticado    <massa>`. Cada teste abre uma sessão nova e, com `appium:noReset=false`, o app
começa limpo (deslogado, carrinho vazio). Testes com a tag `defeito-conhecido` que falharem aparecem como **SKIP** com o motivo.

**Timeouts:** um único `${TIMEOUT}` de 30s (`tests/resources/infraestrutura.resource`) vale para todas as esperas
e para a retentativa das leituras de texto (`Validar Texto Do Elemento`). Para um app mais lento, sobrescreva na
linha de comando (`--variable TIMEOUT:60s`). Cada teste tem teto de 5 minutos (`tests/robot/__init__.robot`).

**Relatório consolidado** em `tests/reports/` (não versionado): cada execução é mesclada às anteriores
(`rebot --merge`, via `tests/libs/summary_listener.py`), e o teste reexecutado substitui o resultado antigo.

- `log.html` (screenshots inline), `report.html`, `output.xml`: todos os testes já executados
- `summary.md` / `summary.json`: último resultado de cada teste + seção "Última execução"
- `screenshots/<ID>/NN_<evidencia>.png` (ex.: `screenshots/BUY-001/03_revisao_pedido.png`)

Para zerar o histórico, apague `tests/reports/`. Sempre execute a pasta `tests/robot`
(filtrando com `--suite`/`--test`/`--include`) para manter a hierarquia do consolidado.
No Windows, se o console mostrar acentos quebrados, defina `PYTHONUTF8=1`.

## Cobertura atual

| ID | Funcionalidade | Objetivo (tag) | Último resultado |
|---|---|---|---|
| PROD-001 | produtos | `listagem-de-produtos` | PASS |
| PROD-002 | produtos | `detalhes-do-produto` | PASS |
| PROD-003 | produtos | `ordenacao-por-preco` | PASS |
| CART-001 | carrinho | `adicionar-um-item` | PASS |
| CART-002 | carrinho | `adicionar-varios-itens` | SKIP (`defeito-conhecido`) |
| CART-003 | carrinho | `remover-item` | PASS |
| CART-004 | carrinho | `carrinho-vazio` | PASS |
| BUY-001 | compra | `compra-de-um-item` | PASS |
| BUY-002 | compra | `compra-de-varios-itens` | SKIP (`defeito-conhecido`) |

Cada teste aponta para o seu cenário em `context/cenarios/` pelo `[Documentation]`, e cada cenário cita as regras de
negócio que prova (`- **Regras:**`). A cobertura por regra sai de `matriz_cobertura.py`: hoje 14 de 19 regras têm cenário.

## Reutilizar em outro app (novo case)

O projeto separa o **framework**, que é reaproveitado como está, do **conhecimento do app**, que é
trocado a cada case.

**Framework (manter):**

| Item | Por que é genérico |
|---|---|
| `CLAUDE.md` | Regras do agente; troque só o mapa de pastas de funcionalidade e os exemplos |
| `.claude/commands/testar-cenarios.md` | Fluxo de 8 passos com três portões, independente do app |
| `.claude/skills/product-owner/`, `.claude/skills/analista-de-testes/` | Personas de requisito e cobertura; trocam-se só as regras em `context/regras-negocio/` |
| `.claude/agents/revisor-robot.md`, `.claude/scripts/`, `.claude/hooks/`, `robocop.toml` | Revisão, lint e guardrails; ajuste os ids reutilizados citados no revisor |
| `.claude/skills/avaliador-de-execucao/` | Avaliação e registro de descobertas; ver "Como adaptar" no [guia](.claude/skills/avaliador-de-execucao/README.md) |
| `tests/resources/infraestrutura.resource` | Sessão por teste, evidências, `${TIMEOUT}`, leitura com retentativa |
| `tests/libs/` | Variable file (capabilities + massas) e listener do relatório consolidado |
| `tests/robot.args`, `tests/robot/__init__.robot` | Saída consolidada, `defeito-conhecido` → SKIP, teto de 5 min |
| `context/cenarios/_modelo.md`, `context/regras-negocio/conduta-testes.md` | Formato de cenário e conduta dos testes |
| `.mcp.json`, `.claude/settings.json`, `.gitignore`, `.gitattributes` | Infraestrutura do repositório |

**Conhecimento do app (trocar), nesta ordem:**

1. `tests/config/capabilities.json`: `appPackage`, `appActivity`, `udid`, `platformVersion` (o Robot e o MCP leem daqui).
2. `tests/apk/`: o binário do novo app e o link de download no README.
3. `tests/massas/users.yaml`: as massas de login do novo app (apenas dados fictícios).
4. `tests/pages/`: apague as páginas do My Demo App; o `/testar-cenarios` cria as novas ao explorar as telas.
5. `tests/resources/suite.resource`: liste as novas páginas e reescreva `Iniciar App Autenticado` com o login do novo app.
6. `context/app/`, `context/descobertas/`: recomece `navegacao.md`, `app-profile.yaml` e os dois arquivos de descobertas (mantenha os cabeçalhos).
   Em `context/regras-negocio/`, apague `produtos.md`, `carrinho.md` e `compra.md` e escreva as regras do novo app com `/product-owner`.
7. `context/cenarios/<func>/` e `tests/robot/<func>/`: apague os do My Demo App e escreva os novos cenários.
8. Apague `tests/reports/` e rode `/testar-cenarios context/cenarios/<func>/`.

Para um app mais lento, ajuste só o `${TIMEOUT}` (`--variable TIMEOUT:60s`). Para outra plataforma (iOS),
troque o `automationName` e os locators; as regras, a skill e o relatório continuam valendo.

## Limitações conhecidas do app

A versão 2.3.0 **não valida a senha**, fecha ao usar Back logo após o login e trava ao abrir um
produto da 2ª posição do catálogo, um bug proposital do app de demonstração (CART-002 e BUY-002 ficam em SKIP pela tag `defeito-conhecido`). Detalhes em
`context/descobertas/limitacoes-conhecidas.md`.

## Segurança

- `tests/massas/users.yaml` é versionado: use apenas credenciais fictícias ou públicas do app de demonstração.
- Senhas são digitadas com `Input Password` e não aparecem nos logs do Robot.
- Execute somente em ambientes autorizados.
