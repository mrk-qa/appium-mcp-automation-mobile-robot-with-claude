# Template de cenário

Copie para `context/cenarios/<funcionalidade>/<id-curto>.md`. O agente aceita texto livre,
mas cenários neste formato são convertidos sem ambiguidade.

```markdown
# <ID> <Título curto>

- **ID:** CART-001                      # prefixo da funcionalidade + número; abre o nome do teste
- **Tags:** carrinho, adicionar-um-item  # funcionalidade + objetivo do teste; viram tags Robot
- **Suíte:** cart                       # diretório/arquivo: tests/robot/carrinho/carrinho.robot

## Objetivo
Uma frase sobre o que está sendo validado.

## Pré-condições
- Estado inicial: app limpo (carrinho vazio) e usuário autenticado   # padrão: Iniciar App Autenticado
- Outras condições, se houver

## Dados
- produto: Sauce Labs Backpack ($ 29.99)   # vira VAR no caso de teste; nunca escrever senhas

## Passos
1. Abrir o produto "Sauce Labs Backpack".
2. Tocar em "Add to cart".             📸 contador_carrinho
3. Abrir o carrinho.

## Resultado esperado (critérios verificáveis)
- [ ] O contador do carrinho mostra 1.
- [ ] O carrinho lista o produto com o preço "$ 29.99".   📸 item_no_carrinho
```

## Convenções

- `📸 <nome>` marca o ponto de evidência e vira `Registrar Evidência    <nome>`.
- Todo critério de "Resultado esperado" deve virar **uma asserção** (keyword `Validar ...`).
  Critério sem asserção possível → o agente pergunta antes de executar.
- Falhas sempre geram screenshot automático (`falha`) pelo Test Teardown.
- Os dados do cenário viram `VAR` no próprio caso de teste (`.robot`); não existe arquivo de dados separado.
- Tags: a da funcionalidade (`produtos`, `carrinho`, `compra`) vem do `Test Tags` da suíte; a do objetivo, do `[Tags]` do teste.
- O login não é um cenário: é o step de setup de todos os testes (`Iniciar App Autenticado`).
