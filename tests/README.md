# Testes Automatizados - Projeto Oráculo

Este diretório contém testes automatizados para o Projeto Oráculo utilizando pytest.

## Estrutura de Diretórios

```
tests/
├── unit/          # Testes unitários
```

## Como executar os testes

Para executar todos os testes:
```
pytest
```

Para executar testes específicos:
```
pytest tests/unit/etl/nome_do_arquivo.py
```

Para executar testes com cobertura de código:
```
pytest --cov=src tests/
```
