# satveg-api

**satveg-api** é uma biblioteca Python que requisita aos servidores da Embrapa a série NDVI ou EVI de uma localidade (latitude, longitude). Tem capacidade de fazer múltiplas requisições dado um arquivo `.csv`, retornando um Pandas.DataFrame.

## Utilização

```python
>>> import satveg_api
>>> serie = satveg_api.Series('SEU_TOKEN_DA_API_SATVEG')
>>> serie.get_json(-18.92803, -40.09281)
{
  'success': True,
  'status_code': 200,
  'message': 'Sucesso.',
  'data': {
    'listaSerie': [0.6923, ..., 0.6638],
    'listaDatas': ['2000-02-18', ..., '2022-06-26']
  }
}

>>> serie.get(-18.92803, -40.09281, label='Café')
'pandas.core.frame.DataFrame'

>>> df = serie.from_csv('input.csv')
'pandas.core.frame.DataFrame'

>>> satveg_api.to_learn(df)
'pandas.core.frame.DataFrame'
```

Exemplo de `input.csv`:

| label | latitude  | longitude |
|-------|-----------|-----------|
| Café  | -18.92803 | -40.09281 |

## Instalando a biblioteca satveg-api

satveg-api está disponível no PyPI:

```console
$ python -m pip install satveg-api
```