# Fator Valor no Ibovespa — Backtest (mar/2024 a jul/2026)

Trabalho de Análise de Dados com Python. Carteira de 10 ações do Ibovespa escolhidas pelo **fator valor**,
comprada em 28/03/2024 e mantida até 01/07/2026, sem rebalanceamento.

## Metodologia
- **Universo:** ações do Ibovespa de jan-abr/2024 que continuam no índice hoje (uma classe por empresa).
- **Indicadores:** E/P (lucro / valor de mercado), B/M (patrimônio líquido / valor de mercado) e
  EBIT/EV (EBIT / valor da firma). Bancos e holdings financeiras usam só E/P e B/M.
- **Nota:** média dos percentis dos indicadores. As 10 melhores entram com pesos iguais.
- **Sem olhar o futuro:** cada balanço só é usado se já tinha sido entregue à CVM na data da compra.
- **Comparação:** Ibovespa no mesmo período, com dividendos reinvestidos nos dois lados.

## Fontes de dados (gratuitas)
- Balanços anuais (DFP) — [Portal de Dados Abertos da CVM](https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp)
- Preços diários — Yahoo Finance

## Resultado
| | Carteira Value | Ibovespa |
|---|---|---|
| Retorno total | +36,3% | +34,0% |
| Retorno ao ano | +14,9% | +14,0% |
| Volatilidade anual | 16,0% | 15,5% |
| Maior queda | −12,8% | −15,3% |

Carteira: GOAU4, ALOS3, GGBR4, PETR4, BRAP4, BBAS3, CMIG4, ISAE4, VALE3, BBDC4.
Detalhes em `resultados/carteira_unica.csv` e evolução diária em `resultados/carteira_unica_serie.csv`.

## Limitações
- Ações que estavam no Ibovespa em 2024 e saíram depois (ex.: AZUL4, GOLL4, BHIA3, PCAR3) ficam fora,
  o que provavelmente deixa o resultado otimista. A Natura ficou fora por falta de histórico de preços.
- Uma única carteira, num único período de pouco mais de dois anos.
- Sem custos de corretagem e impostos.

## Como rodar
Requer Python 3.10+ e as bibliotecas `pandas`, `numpy` e `requests`:

```
pip install pandas numpy requests
python backtest_value_carteira_unica.py
```

Na primeira execução o código baixa os balanços da CVM (cerca de 26 MB) para a pasta `cvm/`.
Os resultados podem variar um pouco se o Yahoo Finance revisar os preços históricos.
