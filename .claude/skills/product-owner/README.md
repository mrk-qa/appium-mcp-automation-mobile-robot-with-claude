# Skill `product-owner`

Skill do Claude Code que atua como **Product Owner** do app sob teste: mantém as **regras de negócio** do app e
refina cenários até a **Definition of Ready (DoR)**, antes de qualquer linha de Robot.

> O Claude lê o `SKILL.md`. Este README é a documentação para quem usa, mantém ou adapta a skill.

## Quando ela roda

- **Automaticamente** no passo 1 do `/testar-cenarios`: o cenário só segue para automação com a DoR cumprida.
- **Sob demanda:** `/product-owner <texto livre>` ou peça "escreva/refine o cenário ...", "documente a regra ...".

## O que ela produz

| Artefato | Onde | Formato |
|---|---|---|
| Regras de negócio | `context/regras-negocio/<func>.md` | `### RN-<PREFIXO>-NN` + Regra, Fonte, Status |
| Cenários prontos | `context/cenarios/<func>/<id-curto>.md` | `context/cenarios/_modelo.md`, com `- **Regras:**` |

A rastreabilidade fica **regra → cenário → teste → evidência**:
`- **Regras:**` no cenário, `[Documentation]    Cenário: ...` no teste e `Registrar Evidência` nos `📸`.

## Portão determinístico

`.claude/scripts/validar_cenarios.py` confere a estrutura (também roda pelo hook `validar_apos_edicao` a cada edição):

| Código | Verifica |
|---|---|
| C01 · C13 | Título `# <ID> <Título>` igual ao `- **ID:**`; ID único |
| C03 · C04 | Tags `<funcionalidade>, <objetivo>` (kebab-case, sem `smoke`/ID); suíte `tests/robot/<func>/` |
| C05 | `- **Regras:**` com RN existentes (aviso se `a confirmar`/`obsoleta`) |
| C06 · C07 · C15 | Seções do modelo, ao menos um critério `- [ ]`, passos numerados |
| C08 | Termo vago em critério (`correto`, `esperado`, `adequado`, `funciona`...) — aviso |
| C09 · C10 · C11 | Ao menos um `📸`; nenhuma senha de massa; status válido |
| N01–N06 | Regras: título `### RN-...`, Regra/Fonte/Status, ID único, status válido, termo vago |

A parte de julgamento (critério prova a regra? cenário independente? duplicado?) é o checklist do passo 4 do `SKILL.md`.

## Como adaptar

- **Termos vagos:** `TERMOS_VAGOS` em `validar_cenarios.py` (inclua os do vocabulário do seu time).
- **Status:** `STATUS_CENARIO` e `STATUS_REGRA` no mesmo script, e a legenda em `context/regras-negocio/produtos.md`.
- **Outro app:** recomece `context/regras-negocio/<func>.md` com os prefixos das novas funcionalidades.
