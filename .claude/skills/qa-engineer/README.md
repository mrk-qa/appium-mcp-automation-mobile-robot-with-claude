# Skill `qa-engineer`

Skill do Claude Code que avalia, como um QA Engineer, o resultado da **última execução Robot** do projeto:
classifica cada falha, confere evidências e rastreabilidade, emite um **veredito** e **registra as
descobertas** no `context/`.

> O Claude lê o `SKILL.md` (instruções e frontmatter). Este README é a documentação para quem vai usar,
> manter ou adaptar a skill.

## Quando ela roda

- **Automaticamente** no passo 6 do comando `/testar`.
- **Sob demanda**: peça "analise o resultado dos testes" ou digite `/qa-engineer` depois de qualquer
  `python -m robot -A tests/robot.args ...`.

## Arquivos

| Arquivo | Papel |
|---|---|
| `SKILL.md` | Instruções da skill (frontmatter `name`/`description` + passos 1 a 7). |
| `scripts/coletar_resultados.py` | Coleta os fatos da última execução em JSON (somente leitura). |
| `README.md` | Este guia. |

## O que ela faz, passo a passo

1. **Coleta os fatos**: `python .claude/skills/qa-engineer/scripts/coletar_resultados.py`, na raiz.
   Lê `tests/reports/.last-run.xml` (a última execução, não o consolidado) e devolve, por teste: status,
   mensagem, tags, duração, evidências geradas × planejadas (contando os `Registrar Evidência` do `.robot`),
   presença do screenshot `falha` e o cenário `.md` ligado pelo `[Documentation]`. Lista também avisos,
   testes que não rodaram e seletores `# NÃO VALIDADO`.
2. **Classifica** cada FAIL/SKIP abrindo o screenshot `falha`:
   `FAIL-ambiente`, `FAIL-automação`, `Timeout` ou `FAIL-divergência`; SKIP só é aceito se bater com um
   defeito documentado (tag `defeito-conhecido`).
3. **Confere qualidade**: evidências completas, última evidência de cada PASS condizente com o teste,
   rastreabilidade com o cenário, cobertura, testes lentos (> 2× a mediana), avisos e seletores a validar.
4. **Emite o veredito**: `APROVADO`, `APROVADO COM RESSALVAS`, `REPROVADO` ou `BLOQUEADO`.
5. **Decide o que registrar** (só fatos com evidência; hipótese marcada como `Hipótese:`).
6. **Escreve as descobertas**, atualizando em vez de duplicar:

   | Achado | Destino |
   |---|---|
   | Comportamento novo do app | `context/descobertas/comportamentos-observados.md` |
   | Defeito ou limitação (nova ou repetida) | `context/descobertas/limitacoes-conhecidas.md` |
   | Cenário afetado | seção "Observações da execução" no `.md` do cenário |
   | Comportamento sem cobertura | novo cenário **proposto** em `context/cenarios/<func>/` |

7. **Responde** com veredito, tabela por teste, achados, descobertas registradas, ações recomendadas e links.

## Permissões

- **Pode alterar:** apenas `context/descobertas/*.md` e `context/cenarios/**/*.md`.
- **Não altera:** testes, páginas, keywords, configuração e relatórios. Correções de automação são
  recomendadas; quem aplica é o agente no `/testar` (ou você).

## Saída do script (resumo do JSON)

```json
{
  "execucao": {"inicio": "...", "total": 9, "pass": 7, "fail": 0, "skip": 2, "mediana_pass_s": 41.4},
  "testes": [{"id": "CART-004", "status": "PASS", "evidencias": ["tests/reports/screenshots/CART-004/01_..."],
              "evidencias_planejadas": 2, "evidencia_falha": false,
              "cenario": "context/cenarios/carrinho/carrinho-vazio.md", "cenario_existe": true, "...": "..."}],
  "lentos": [], "avisos": [], "nao_executados": [], "seletores_nao_validados": []
}
```

## Dependências do projeto (contrato)

A skill é genérica, mas assume as convenções deste repositório. Ao reutilizar em outro app, mantenha:

- Execução com `-A tests/robot.args` (gera `tests/reports/.last-run.xml` e `screenshots/<ID>/`).
- Nome do teste começando pelo ID (`<ID> <Título>`) e evidências via `Registrar Evidência`.
- `[Documentation]    Cenário: context/cenarios/<func>/<arquivo>.md` em todo teste.
- Locators em `tests/pages/*.resource`, com `# NÃO VALIDADO` nos ainda não exercitados.
- Arquivos `context/descobertas/comportamentos-observados.md` e `limitacoes-conhecidas.md` existentes.

## Como adaptar

- **Sinais de classificação** (tabela do passo 2 do `SKILL.md`): inclua mensagens típicas do novo app ou
  da nova plataforma (ex.: XCUITest no iOS).
- **Regras do veredito** (passo 4): ajuste o que conta como ressalva para o seu time.
- **Formato dos registros** (passo 6): os modelos em Markdown podem ser trocados, mas mantenha data,
  ID do teste e caminho da evidência em cada linha.
- **Novos fatos no JSON**: acrescente campos em `coletar_resultados.py` (ex.: tempo de setup) e cite-os
  no passo 3 do `SKILL.md`.
