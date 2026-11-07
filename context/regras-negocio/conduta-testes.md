# Regras de conduta dos testes (business rules)

This is a learning and testing project using a demonstration
application and fictional test data.

- Do not use production accounts or real customer data.
- Use only explicitly configured test environments.
- Validate expected results with deterministic assertions
  whenever possible.
- Do not report a scenario as passed without checking its
  acceptance criteria.
- Stop if the current application state is unexpected
  or a required precondition cannot be satisfied.

## Convenções deste projeto

- O login **não é objeto de teste**: todo teste começa autenticado (`Test Setup    Iniciar App Autenticado`).
- Credenciais vêm só das massas de `tests/massas/users.yaml` (padrão: `padrao`); a senha é digitada com `Input Password`.
  Cenário que precise de outro usuário escolhe a massa no setup do teste; massa nova é adicionada nesse arquivo.
- Os **dados de cada teste ficam no próprio `.robot`**: produto, preço e valores esperados no caso de teste
  (`VAR`); dados compartilhados pela suíte (ex.: endereço e cartão fictícios) na seção `*** Variables ***`.
- Use apenas dados fictícios ou públicos do app de demonstração.
- Comportamento divergente do esperado → reportar e registrar em `context/descobertas/limitacoes-conhecidas.md`;
  defeito confirmado e persistente → tag `defeito-conhecido` nos testes afetados (SKIP com o motivo).
- Todo teste aponta para o seu cenário (`[Documentation]    Cenário: context/cenarios/...`); `.md` e `.robot` mudam juntos.

