---
description: Interpreta cenários (texto livre ou arquivos em context/cenarios/), explora o app via Appium MCP quando necessário, gera e executa suítes Robot e reporta com evidências.
argument-hint: <cenários em texto livre | caminho(s) de context/cenarios/>
---

# /testar

Entrada do usuário:

$ARGUMENTS

Siga **todas** as etapas na ordem, respeitando as regras do `CLAUDE.md`.

## 1. Interpretar
- Se a entrada for um caminho, leia os `.md` indicados. Se for texto livre, extraia os cenários dele.
- Para cada cenário, identifique: ID (crie `<FUNC>-<NNN>` se faltar), pré-condições, dados, passos,
  **critérios verificáveis** e pontos de evidência (`📸`; na falta, uma evidência por critério).
- Identifique a **funcionalidade** (`produtos`, `carrinho`, `compra`, ...). O login **não** é objeto de teste:
  é o step de setup `Iniciar App Autenticado`, executado em todos os testes.
- Critério ambíguo ou não verificável → pergunte antes de seguir.
- Salve cenários novos em `context/cenarios/<funcionalidade>/<id-curto>.md` (`context/cenarios/_modelo.md`).

## 2. Carregar contexto
Leia `context/app/*`, `context/regras-negocio/*`, `context/descobertas/*` , `tests/resources/*.resource` e `tests/pages/*.resource`.
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
- `Registrar Evidência    <nome>` em cada `📸`
- cada critério esperado ⇒ ao menos uma keyword `Validar ...`

## 5. Executar
Confirme que não existe sessão MCP ativa e rode:
```
python -m robot -A tests/robot.args --test "<ID>*" tests/robot     # um ou mais --test
```

## 6. Analisar
Acione a skill **`qa-engineer`** (`.claude/skills/qa-engineer/SKILL.md`): ela coleta os fatos da última execução,
classifica cada falha, confere evidências e rastreabilidade e emite o veredito. Use a classificação dela para agir:
- **Seletor/automação quebrada** (elemento não encontrado, timing): corrija a keyword ou o contexto
  e reexecute **uma única vez** só os testes que falharam (mesmo comando com `--test "<ID>*"`; o resultado novo substitui o anterior no consolidado).
- **Divergência do app** (a tela mostra um comportamento diferente do esperado): **não corrija**. Reporte e
  registre em `context/descobertas/limitacoes-conhecidas.md` (passos, evidência, testes afetados). Defeito
  confirmado e persistente: adicione a tag `defeito-conhecido` aos testes afetados (passam a SKIP com o motivo).
- **Ambiente** (device offline, Appium): reporte e pare.

Depois de um PASS, remova o `# NÃO VALIDADO` dos seletores novos usados em `tests/pages/`.

## 7. Reportar
Responda em português com:
0. O veredito da skill `qa-engineer` (APROVADO / APROVADO COM RESSALVAS / REPROVADO / BLOQUEADO)
1. Tabela: ID · cenário · status (PASS / FAIL-divergência / FAIL-automação / SKIP-defeito-conhecido / BLOQUEADO) · nº de evidências
2. Para cada cenário: critérios verificados (✔/✘) e caminhos dos screenshots principais
3. Divergências do app, com o comportamento esperado e o observado
4. Arquivos de contexto e keywords criados ou alterados
5. Links: `tests/reports/log.html` e `tests/reports/summary.md`
