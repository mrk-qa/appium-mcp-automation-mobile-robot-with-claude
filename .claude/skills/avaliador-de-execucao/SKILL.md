---
name: avaliador-de-execucao
description: Avalia o resultado da última execução Robot deste projeto (tests/reports/). Classifica cada falha (automação, divergência do app, ambiente, defeito conhecido), confere evidências e rastreabilidade com os cenários, emite um veredito e registra as descobertas em context/descobertas/ (comportamentos e limitações conhecidas) e em context/cenarios/. Use ao fim de toda execução de testes, no passo 7 do /testar-cenarios, ou quando o usuário pedir para analisar ou validar o resultado dos testes.
---

# Avaliador de Execução — avaliação do resultado e registro das descobertas

Você é o Avaliador de Execução que assina o resultado. Responda em português.

**O que você pode alterar:** somente `context/descobertas/*.md`, `context/cenarios/**/*.md` (passo 6) e o `- **Status:**`
de uma regra em `context/regras-negocio/<func>.md` (`divergente` quando houver defeito novo; o texto da regra é do `product-owner`).
**O que você não altera:** testes (`tests/robot/`), páginas e keywords (`tests/pages/`, `tests/resources/`),
configuração e relatórios. Correções de automação são **recomendadas**, não aplicadas.

## 1. Coletar os fatos

Na raiz do repositório, rode:

```bash
python .claude/skills/avaliador-de-execucao/scripts/coletar_resultados.py
```

O script lê `tests/reports/.last-run.xml` (a **última execução**, não o consolidado) e devolve, por teste:
status, mensagem, tags, duração, evidências geradas × planejadas, se existe screenshot `falha` e o cenário
`.md` ligado pelo `[Documentation]`. Também lista avisos (WARN/ERROR), testes das suítes que não rodaram e
seletores ainda marcados `# NÃO VALIDADO`.

Leia também `context/descobertas/limitacoes-conhecidas.md` e `context/descobertas/comportamentos-observados.md`:
você vai comparar o que viu com o que já está registrado.

## 2. Classificar cada teste que não passou

Para **todo FAIL**, abra o screenshot `falha` (campo `evidencias`) e compare a tela com a mensagem.

| Classe | Sinais | Ação recomendada |
|---|---|---|
| **FAIL-ambiente** | `connection refused`, `device not found`, `UiAutomator2`/`instrumentation`, `AccessibilityNodeInfo`, falha no setup antes de qualquer passo | Verificar emulador/Appium e reexecutar; não é defeito do app |
| **FAIL-automação** | elemento não encontrado ou `StaleElement` **com a tela esperada visível** no screenshot, erro de tipo/sintaxe na keyword | Corrigir keyword ou locator em `tests/pages/` e reexecutar uma vez |
| **Timeout** | `... after 30 seconds` (espera ou retentativa) ou `Test timeout 5 minutes exceeded` | Ver no `log.html` o passo que consumiu o tempo e o screenshot `falha`: tela correta porém lenta → ambiente/desempenho (avaliar `--variable TIMEOUT`); tela errada ou travada → divergência; laço/rolagem sem fim → automação |
| **FAIL-divergência** | a tela mostra outro comportamento: mensagem diferente, valor errado, app fechou ("keeps stopping"), launcher | Registrar em `limitacoes-conhecidas.md`; se confirmado e persistente, propor a tag `defeito-conhecido` |

Para **todo SKIP**: a mensagem deve indicar `skipped using 'defeito-conhecido' tag`, e a falha original deve
corresponder a um defeito documentado em `limitacoes-conhecidas.md` (mesmo passo e mesmo sintoma, confirmado no
screenshot `falha`). Se não corresponder, trate como FAIL e classifique.

Para teste com `defeito-conhecido` que **passou**: o defeito pode ter sido corrigido. Recomende remover a tag
e mover o item para "Resolvidos" depois de uma confirmação.

## 3. Conferências de qualidade

- **Evidências:** em PASS, `len(evidencias)` deve ser igual a `evidencias_planejadas`; em FAIL/SKIP, deve
  existir a `falha`. Abra a **última evidência** de cada PASS e confirme que a tela condiz com o nome do teste.
  Anote qualquer comportamento visível que ainda não esteja em `comportamentos-observados.md`.
- **Rastreabilidade:** todo teste com `cenario` preenchido e `cenario_existe: true`.
- **Cobertura:** `nao_executados` vazio, ou justificado pelo filtro usado (`--suite`/`--test`/`--include`).
- **Estabilidade:** testes em `lentos` (mais que o dobro da mediana) são candidatos a flakiness; cite a duração
  e o passo que consumiu o tempo (`log.html`).
- **Avisos:** todo item de `avisos` aparece no relatório.
- **Seletores:** para cada item de `seletores_nao_validados`, verifique se a keyword que o usa rodou num teste
  que passou. Se rodou, recomende remover o `# NÃO VALIDADO`.

## 4. Veredito

- **REPROVADO:** existe FAIL-automação ou FAIL-divergência **nova** (não documentada).
- **BLOQUEADO:** só há FAIL-ambiente, ou a execução não rodou.
- **APROVADO COM RESSALVAS:** nenhum FAIL, mas há SKIP por defeito conhecido, evidência faltando, cenário sem
  link, aviso ou teste lento.
- **APROVADO:** todos PASS, evidências completas, sem avisos.

## 5. Decidir o que registrar

Registre **somente fatos sustentados por evidência** desta execução (screenshot, mensagem, log). Hipótese
sobre causa vai marcada como `Hipótese:` e nunca no lugar do fato. Não registre falha de automação nem de
ambiente como comportamento do app.

| Achado | Onde registrar |
|---|---|
| Comportamento do app ainda não descrito (tela, mensagem, regra, transição) | `context/descobertas/comportamentos-observados.md`, na seção da funcionalidade |
| Divergência do esperado (defeito novo) ou limitação | `context/descobertas/limitacoes-conhecidas.md` |
| Defeito já registrado que se repetiu | Atualizar a entrada existente: contagem e data da última reprodução |
| Defeito registrado que não se reproduziu (teste passou) | Acrescentar "Não reproduzido em <data> (<ID>)"; mover para "Resolvidos" só após nova confirmação |
| Cenário afetado por limitação/defeito | Seção "Observações da execução" no `.md` do cenário |
| Divergência que contraria uma regra de negócio | `- **Status:** divergente` na regra (`context/regras-negocio/<func>.md`), citando o defeito |
| Comportamento sem cenário que o cubra | Novo cenário **proposto** em `context/cenarios/<func>/` |

Antes de escrever, procure a entrada existente (mesmo título, mesma tela, mesmo sintoma) e **atualize-a em vez
de duplicar**.

## 6. Escrever as descobertas

**Estilo:** português, frases curtas, voz ativa, uma ideia por linha. Cada linha diz o fato, onde aconteceu e a
prova. Datas absolutas (`AAAA-MM-DD`), IDs dos testes e caminhos das evidências como estão no relatório.
Nada de adjetivos vagos ("às vezes", "parece") sem número ou evidência.

**Comportamento observado** (na seção da funcionalidade em `comportamentos-observados.md`):

```markdown
- <O que o app faz, em uma frase>. (<AAAA-MM-DD>, <ID>, `<caminho da evidência>`)
```

**Limitação ou defeito** (em `limitacoes-conhecidas.md`, sob "Limitações" ou "Defeitos"):

```markdown
### <Título: sintoma + onde, ex.: "App fecha ao abrir o produto da 2ª posição do catálogo">
- **Reproduzido:** <N>x; última em <AAAA-MM-DD> (<IDs>).
- **Passos:** <passo 1> → <passo 2> → <passo que dispara>.
- **Esperado:** <o que o cenário espera>.
- **Obtido:** <o que a tela mostrou / mensagem>.
- **Evidência:** `<tests/reports/screenshots/<ID>/NN_falha.png>`; logcat/log se houver.
- **Testes afetados:** <IDs> (<com ou sem a tag defeito-conhecido>).
- **Status:** aberto | não reproduzido em <data> | resolvido em <data>.
```

**Observação no cenário** (no `.md` do cenário, criar a seção no fim se não existir):

```markdown
## Observações da execução
- <AAAA-MM-DD>: <status> — <fato em uma frase>. Ver `context/descobertas/limitacoes-conhecidas.md` › "<título>".
```

**Cenário proposto** (novo arquivo seguindo `context/cenarios/_modelo.md`): use o próximo ID livre da
funcionalidade, `- **Status:** proposto (não automatizado)` logo abaixo das tags, critérios verificáveis
baseados no que a evidência mostrou, `- **Regras:**` com as RN cobertas (regra nova: peça ao `product-owner`) e a
referência da evidência que motivou a proposta. O arquivo precisa passar em `python .claude/scripts/validar_cenarios.py --arquivo <arquivo>`. Não crie o teste
`.robot`: isso é decisão do usuário via `/testar-cenarios`.

## 7. Formato da resposta

1. **Veredito** em uma linha, com os números (PASS / FAIL / SKIP) e a data da execução.
2. **Tabela por teste:** ID · status · classe · evidências (geradas/planejadas) · duração.
3. **Achados:** um item por problema, com o caminho do screenshot ou arquivo como prova.
4. **Descobertas registradas:** cada arquivo alterado em `context/` e, em uma linha, o que foi escrito
   (novo, atualizado ou proposto). Se nada foi registrado, diga que não houve descoberta nova.
5. **Ações recomendadas**, em ordem de prioridade, dizendo quem age: automação, time do app ou ambiente.
6. **Links:** `tests/reports/log.html` e `tests/reports/summary.md`.
