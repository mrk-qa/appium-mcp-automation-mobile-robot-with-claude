---
description: Interpreta cenários (texto livre ou arquivos em context/cenarios/), refina até a Definition of Ready, explora o app via Appium MCP quando necessário, gera, revisa e executa suítes Robot e reporta com evidências.
argument-hint: <cenários em texto livre | caminho(s) de context/cenarios/>
---

# /testar-cenarios

Entrada do usuário:

$ARGUMENTS

Siga **todas** as etapas na ordem, respeitando as regras do `CLAUDE.md`. Três portões não podem ser pulados:
**DoR** (passo 1, skill `product-owner`), **revisão** (passo 5, subagente `revisor-robot`) e **análise** (passo 7,
skill `avaliador-de-execucao`). Os hooks de `.claude/settings.json` reforçam os dois primeiros: validam cada arquivo editado e
bloqueiam o Robot sem revisão aprovada.

## 1. Interpretar e refinar (portão: Definition of Ready)
- Se a entrada for um caminho, leia os `.md` indicados. Se for texto livre, extraia os cenários dele.
- Acione a skill **`product-owner`** (`.claude/skills/product-owner/SKILL.md`). Ela identifica as regras de negócio
  envolvidas (`context/regras-negocio/<func>.md`), cria ou ajusta as que faltam, escreve/ajusta o cenário em
  `context/cenarios/<func>/<id-curto>.md` com `- **Regras:**` e confere a DoR (`validar_cenarios.py` + checklist).
- Funcionalidade nova ou pedido de cobertura → acione também a skill **`analista-de-testes`** para propor o conjunto de cenários.
- O login **não** é objeto de teste: é o step de setup `Iniciar App Autenticado`, executado em todos os testes.
- DoR **PENDENTE** (critério ambíguo, regra `a confirmar`, pré-condição impossível) → pergunte ao usuário e **pare** aqui.

## 2. Carregar contexto
Leia `context/app/*`, `context/regras-negocio/*`, `context/descobertas/*`, `tests/resources/*.resource` e `tests/pages/*.resource`.
Confira se o cenário bate com algum item de `context/descobertas/limitacoes-conhecidas.md` (ex.: senha não
validada, crash ao abrir o 2º produto do catálogo). Se bater, avise antes de executar que o resultado esperado
provavelmente vai divergir.

## 3. Mapear passos → keywords
Monte uma tabela `passo/critério → keyword existente`. Para cada lacuna:
1. Explore com o **Appium MCP**: crie a sessão (capabilities de `tests/config/capabilities.json`) e navegue
   até a tela. Use page source e screenshot para identificar seletores estáveis
   (resource-id > accessibility id > texto).
2. Registre os seletores (com `# NÃO VALIDADO`) e as mensagens do app (`${MSG_*}`) no `*** Variables ***` de
   `tests/pages/<pagina>.resource`, as transições em `context/app/navegacao.md` e os comportamentos em `context/descobertas/comportamentos-observados.md`.
3. Crie as keywords no `*** Keywords ***` da mesma página; leituras de texto usam `Validar Texto Do Elemento`
   e esperas usam o `${TIMEOUT}` padrão. Use `catalogo.resource` como modelo ou crie uma
   página nova (e importe-a em `tests/resources/suite.resource`).
4. **Encerre a sessão do MCP** (`appium_session_management` com action=delete) ao terminar a exploração.

## 4. Gerar a suíte
Adicione o teste no `.robot` de `tests/robot/<funcionalidade>/` (ex.: `compra/compra.robot`; crie o diretório e o
arquivo se a funcionalidade for nova), seguindo **exatamente** o estilo de `tests/robot/compra/compra.robot`:
- um único `Resource    ../../resources/suite.resource`
- mesmos `Test Setup` (`Iniciar App Autenticado`) e `Test Teardown` (`Encerrar Aplicativo`)
- se o teste já existir (mesmo ID), atualize-o em vez de duplicar
- `[Documentation]    Cenário: context/cenarios/<func>/<arquivo>.md` em todo teste; ao mudar o teste, atualize o `.md` junto
- dados do cenário como `VAR` no caso de teste (produto, preço, total esperado); dados comuns em `*** Variables ***`
- `[Tags]` com o objetivo do teste em kebab-case (ex.: `remover-item`); sem tag de ID e sem `smoke`
- só keywords, nenhum locator cru, nenhum `Sleep`, nenhum tempo fixo (use `${TIMEOUT}`)
- `Registrar Evidência    <nome>` em cada `📸`, com os mesmos nomes e na mesma ordem do cenário
- cada critério esperado ⇒ ao menos uma keyword `Validar ...`

A cada edição, o hook `validar_apos_edicao` roda `lint_robot.py` no arquivo: corrija os erros que ele devolver antes de seguir.

## 5. Revisar (portão: revisão independente)
Acione o subagente **`revisor-robot`** (`.claude/agents/revisor-robot.md`) informando os cenários e os arquivos
criados/alterados em `tests/`. Ele roda o lint completo (convenções + Robocop + dry-run), revisa se cada critério
tem asserção que o prova e devolve **APROVADO** (e grava a aprovação) ou **AJUSTES NECESSÁRIOS**.
- AJUSTES NECESSÁRIOS → corrija e peça nova revisão. Depois de **duas** rodadas sem aprovação, pare e mostre os
  achados ao usuário.
- Nunca grave a aprovação você mesmo (`lint_robot.py --aprovar` é do revisor).

## 6. Executar
Confirme que não existe sessão MCP ativa e rode:
```
python -m robot -A tests/robot.args --test "<ID>*" tests/robot     # um ou mais --test
```
O hook `portao_execucao` bloqueia o comando se os `.robot`/`.resource` mudaram desde a última aprovação; nesse caso, volte ao passo 5.

## 7. Analisar
Acione a skill **`avaliador-de-execucao`** (`.claude/skills/avaliador-de-execucao/SKILL.md`): ela coleta os fatos da última execução,
classifica cada falha, confere evidências e rastreabilidade e emite o veredito. Use a classificação dela para agir:
- **Seletor/automação quebrada** (elemento não encontrado, timing): corrija a keyword ou o contexto, peça ao
  `revisor-robot` a revisão só dos arquivos alterados e reexecute **uma única vez** só os testes que falharam
  (mesmo comando com `--test "<ID>*"`; o resultado novo substitui o anterior no consolidado).
- **Divergência do app** (a tela mostra um comportamento diferente do esperado): **não corrija**. Reporte e
  registre em `context/descobertas/limitacoes-conhecidas.md` (passos, evidência, testes afetados); a regra de negócio
  afetada passa a `Status: divergente`. Defeito confirmado e persistente: adicione a tag `defeito-conhecido` aos
  testes afetados (passam a SKIP com o motivo).
- **Ambiente** (device offline, Appium): reporte e pare.

Depois de um PASS, remova o `# NÃO VALIDADO` dos seletores novos usados em `tests/pages/` (comentários não invalidam a aprovação).

## 8. Reportar
Responda em português com:
0. O veredito da skill `avaliador-de-execucao` (APROVADO / APROVADO COM RESSALVAS / REPROVADO / BLOQUEADO)
1. Tabela: ID · cenário · regras cobertas · status (PASS / FAIL-divergência / FAIL-automação / SKIP-defeito-conhecido / BLOQUEADO) · nº de evidências
2. Para cada cenário: critérios verificados (✔/✘) e caminhos dos screenshots principais
3. Divergências do app, com o comportamento esperado e o observado
4. Regras, cenários, arquivos de contexto e keywords criados ou alterados
5. Portões: DoR (product-owner) e revisão (revisor-robot: rodadas e principais ajustes)
6. Links: `tests/reports/log.html` e `tests/reports/summary.md`
