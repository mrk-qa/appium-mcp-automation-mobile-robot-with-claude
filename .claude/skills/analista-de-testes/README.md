# Skill `analista-de-testes`

Skill do Claude Code que atua como **Analista de Testes**: mede a cobertura das regras de negócio, aponta lacunas e
redundâncias e propõe cenários com técnicas formais de desenho de testes.

> O Claude lê o `SKILL.md`. Este README é a documentação para quem usa, mantém ou adapta a skill.

## Quando ela roda

- **Sob demanda:** `/analista-de-testes`, ou peça "qual a cobertura?", "o que falta testar no carrinho?", "monte a matriz".
- **No `/testar-cenarios`**, quando a funcionalidade é nova, para propor o conjunto inicial de cenários.

## Arquivos

| Arquivo | Papel |
|---|---|
| `SKILL.md` | Instruções (medir, analisar, priorizar, propor, responder) |
| `scripts/matriz_cobertura.py` | Matriz regra × cenário × teste × último resultado, e lacunas (somente leitura; `--func`, `--json`) |

## Divisão de papéis

| Persona | Decide | Escreve em |
|---|---|---|
| `product-owner` | **O que** é verdade (regras) e quando um cenário está pronto | `context/regras-negocio/`, `context/cenarios/` |
| `analista-de-testes` | **Quanto** testar: lacunas, prioridade, cenários propostos | `context/cenarios/` (só `proposto`) |
| `revisor-robot` (subagente) | Se o `.robot` prova o cenário e segue as convenções | nada (só aprova) |
| `avaliador-de-execucao` | Se o resultado da execução é confiável | `context/descobertas/`, `context/cenarios/` |

## Como adaptar

- **Fontes:** caminhos no topo de `matriz_cobertura.py` (`REGRAS`, `CENARIOS`, `ROBOT`, `SUMMARY`).
- **Critérios de risco:** seção 3 do `SKILL.md` (ajuste ao domínio do novo app).
