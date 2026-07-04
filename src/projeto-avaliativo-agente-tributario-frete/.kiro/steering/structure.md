---
inclusion: always
---

# Project Structure

## Estrutura de pastas do projeto

```
/src
  /graph          # definição do StateGraph, nós e edges
  /rag            # ingestão, chunking, indexação e retrieval
  /tools          # lookup determinístico de cClassTrib/alíquota
  /schemas        # modelos Pydantic (State, outputs estruturados)
/data
  /docs_regulatorios   # LC 214/2025, Notas Técnicas, cronograma (fonte do RAG)
  /golden_set          # cenários de teste com resultado esperado
/tests
README.md
requirements.txt (ou pyproject.toml)
```

## Convenções de nomenclatura

- Nomes de nós do grafo em `snake_case` e verbo no infinitivo/imperativo descrevendo a ação
  (ex.: `parse_operacao`, `retrieve_context`, `classify_scenario`).
- Chaves do `State` em português, alinhadas ao domínio de negócio (ex.: `regime_tributario`,
  `cclasstrib_sugerido`), já que o domínio (Reforma Tributária brasileira) é em português.
- Testes seguem o padrão `test_<nome_do_nó_ou_função>.py`.

## Padrões de arquitetura

- Cada nó do grafo deve fazer apenas uma coisa (single responsibility), seguindo a prática
  recomendada de manter nós pequenos e focados para facilitar teste e manutenção independente.
- Edges condicionais devem ser usadas para ramificar por regime tributário, modal e fase da
  transição — evitar lógica condicional dentro de um único nó "faz tudo".
