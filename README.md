# pyaqi
Módulo para cálculo do IQAr - Índice de Qualidade do Ar (AQI - Air Quality Index).

## Install

```bash
pip install pyapi
```

## Usage

A atual versão comporta somente o algoritmo brasileiro. Para saber mais
sobre a metodologia brasileira, [consulte
aqui](https://www.gov.br/mma/pt-br/centrais-de-conteudo/mma-guia-tecnico-qualidade-do-ar-pdf).

Com o pacote você pode converter a concentração média de um único poluente
para o seu índice intermediário de qualidade (IQAI):

```python
import aqi
myaqi = aqi()
myaqi.get_iaqi(210, "pm10_24h", algo=myaqi.aqi_brazil)
# out: 168
```

Ou obter o índice de qualidade do ar dadas as concentrações de múltiplos
poluentes. Abaixo utilizamos o exemplo do capítulo 9 da metodologia brasileira:

```python
import aqi
myaqi = aqi()
# Calculando cada um dos poluentes
myaqi.get_iaqi(210, "pm10_24h", algo=myaqi.aqi_brazil)
myaqi.get_iaqi(135, "o3_8h", algo=myaqi.aqi_brazil)
myaqi.get_iaqi(220, "no2_1h", algo=myaqi.aqi_brazil)
myaqi.get_aqi() # por padrão usa o algo brasileiro
# out: 168
# Ou passando todas as concentracoes num unico dicionario
myaqi.get_aqi({"pm10_24h": 210}, {"o3_8h": 135}, {"no2_1h": 220}, algo=myaqi.aqi_brazil)
# out: 168
```