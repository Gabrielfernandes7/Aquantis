# Aquantis
### Risk-Aware Hybrid Quantum Optimization for Water Allocation under Hydrological Uncertainty

> [!NOTE]
> Pesquisa experimental sobre otimização híbrida clássica-quântica aplicada à > alocação de recursos hídricos sob incerteza hidrológica.

**Status:** Em desenvolvimento — fase de estruturação e validação do modelo clássico.

**Estudo de caso:** Reservatório Orós, Bacia do Jaguaribe, Ceará, Brasil.

---

## 1. Sobre o projeto

O Aquantis investiga a aplicação de métodos de otimização híbrida clássica-quântica na alocação de recursos hídricos em cenários de escassez e incerteza hidrológica.

O estudo considera a necessidade de distribuir a disponibilidade hídrica entre diferentes setores, especialmente abastecimento urbano e irrigação, levando em conta demandas, restrições físicas do reservatório e riscos de atendimento.

A pesquisa utiliza o Reservatório Orós, no Ceará, como estudo de caso inicial.

A proposta é desenvolver uma formulação matemática do problema, implementar métodos clássicos de referência, converter a formulação para QUBO e avaliar algoritmos quânticos variacionais, especialmente QAOA.

O objetivo não é presumir vantagem quântica, mas investigar em quais condições métodos híbridos podem oferecer soluções competitivas e quais são suas limitações.

## 2. Problema de pesquisa

Como formular e resolver um problema de alocação de água que equilibre eficiência, prioridades setoriais e risco hidrológico utilizando métodos de otimização híbrida clássica-quântica?

A pesquisa considera três desafios principais:

- **Escassez hídrica:** disponibilidade de água variável ao longo do tempo.
- **Conflito de demandas:** necessidade de atender diferentes setores com prioridades distintas.
- **Incerteza:** dificuldade de prever afluências e garantir atendimento em cenários hidrológicos adversos.

## 3. Objetivos

### Objetivo geral

Desenvolver e avaliar uma abordagem de otimização híbrida baseada em QUBO e QAOA para alocação de recursos hídricos sob incerteza, utilizando o Reservatório Orós como estudo de caso.

### Objetivos específicos

1. Obter e validar dados históricos hidrológicos do Reservatório Orós.
2. Desenvolver um modelo clássico de balanço hídrico.
3. Construir cenários de disponibilidade hídrica.
4. Formular matematicamente o problema de alocação entre setores.
5. Incorporar medidas de aversão ao risco, especialmente Conditional Value at Risk (CVaR).
6. Implementar métodos clássicos de otimização como referência.
7. Converter o problema discretizado para uma formulação QUBO.
8. Implementar e avaliar QAOA e variantes híbridas.
9. Comparar desempenho, qualidade das soluções, viabilidade e custo computacional.

## 4. Estudo de caso

O estudo inicial utiliza o Reservatório Orós, localizado na Bacia do Jaguaribe, no Ceará.

Os setores considerados inicialmente são:

- Abastecimento urbano.
- Irrigação agrícola.

O modelo utilizará dados históricos para representar diferentes condições hidrológicas, incluindo cenários de escassez.

Os parâmetros de demanda, operação e disponibilidade deverão ser documentados com suas respectivas fontes e hipóteses.

**Referência metodológica inicial:**

Silva, S. M. O.; Souza Filho, F. A.; Aquino, S. H. S. (2017). Avaliação do risco da alocação de água em período de escassez hídrica: o caso do Sistema Jaguaribe-Metropolitano. *Engenharia Sanitária e Ambiental*, 22(4).

DOI: https://doi.org/10.1590/S1413-41522017161303

## 5. Metodologia

A arquitetura da pesquisa será organizada em quatro componentes.

### 5.1. Modelagem hidrológica

Implementação clássica do balanço hídrico do reservatório:

$$
V_{t+1,s} = V_{t,s} + I_{t,s} - E_{t,s} - R_{t,s} - Z_{t,s}
$$

Onde:

- \(V\): volume armazenado.
- \(I\): afluência.
- \(E\): perdas por evaporação.
- \(R\): retirada controlada.
- \(Z\): vertimento.
- \(t\): período.
- \(s\): cenário hidrológico.

### 5.2. Otimização clássica

Desenvolvimento de modelos de referência para avaliar a qualidade das soluções:

- Rateio linear.
- Rateio prioritário.
- Programação linear inteira mista (MILP).
- Formulação com CVaR.
- Enumeração exaustiva em instâncias pequenas.
- Simulated Annealing.

### 5.3. Formulação QUBO

Discretização das decisões de alocação e transformação da função objetivo e das restrições em uma função quadrática de variáveis binárias.

A formulação incorporará penalidades para restrições, variáveis auxiliares e componentes de risco.

### 5.4. Otimização quântica

Implementação experimental de:

- Quantum Approximate Optimization Algorithm (QAOA).
- Warm-start QAOA.
- CVaR-QAOA.
- Simulação ideal e com ruído.

Os métodos serão avaliados em instâncias de diferentes tamanhos e resoluções.

## 6. Avaliação

A comparação entre métodos utilizará métricas hidrológicas e computacionais.

**Métricas hidrológicas:**

- Déficit de atendimento urbano.
- Déficit de atendimento agrícola.
- Volume total atendido.
- Garantia de atendimento.
- Garantia volumétrica.
- CVaR das perdas.

**Métricas computacionais:**

- Optimality gap.
- Taxa de soluções viáveis.
- Tempo total de execução.
- Número de variáveis e qubits.
- Profundidade do circuito.
- Número de portas de dois qubits.
- Número de avaliações do otimizador.
- Sensibilidade a seeds, shots e ruído.

Os resultados serão comparados em instâncias equivalentes, com as mesmas restrições, cenários e condições experimentais.

## 7. Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python |
| Manipulação de dados | Pandas, NumPy |
| Otimização clássica | Pyomo, HiGHS |
| Computação quântica | Qiskit |
| Simulação quântica | Qiskit Aer |
| Otimização QUBO | Qiskit Optimization |
| Análise estatística | SciPy |
| Visualização | Matplotlib |
| Testes | pytest |

## 8. Estrutura do projeto

```text
Aquantis/
├── data/
│   ├── raw/
│   │   ├── reservoir/
│   │   ├── inflow/
│   │   ├── evaporation/
│   │   └── demand/
│   ├── processed/
│   └── scenarios/
├── src/
│   ├── data/
│   ├── hydrology/
│   ├── scenarios/
│   ├── optimization/
│   │   ├── classical/
│   │   ├── qubo/
│   │   └── quantum/
│   ├── evaluation/
│   └── visualization/
├── experiments/
├── tests/
├── configs/
├── results/
├── requirements.txt
└── README.md
```

## 9. Plano experimental

| ID | Experimento | Status |
|---|---|---|
| E01 | Rateio linear | Concluído (exp. 06), sob hipóteses declaradas |
| E02 | Rateio prioritário | Concluído (exp. 06), sob hipóteses declaradas |
| E03 | MILP com CVaR | Concluído (exp. 06), sob hipóteses declaradas |
| E04 | Validação da formulação QUBO | Concluído como **aproximação** (exp. 07); MILP discreto = enumeração |
| E05 | QAOA padrão | Concluído em simulação ideal, 8 qubits (exp. 08) |
| E06 | Warm-start QAOA | Concluído em simulação ideal, 8 qubits (exp. 08) |
| E07 | CVaR-QAOA | Concluído em simulação ideal, 8 qubits (exp. 08) |
| E08 | Comparação de discretizações | Parcial: 1, 2 e 3 bits no ótimo clássico (exp. 07); QAOA só com 2 bits |
| E09 | Avaliação de ruído | Concluído com ruído despolarizante sintético (exp. 08) |
| E10 | Avaliação fora da amostra | Parcial: leave-one-year-out (exp. 06) e bootstrap não independente (exp. 08) |

### Como reproduzir

```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
./venv/bin/python -m pytest -q                              # 47 testes
./venv/bin/python -m src.data.fetch_nasa_power              # meteorologia (NASA POWER), opcional
./venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 experiments/0N_*.ipynb
```

Os notebooks `01` a `08` rodam em ordem (os resultados ficam em `results/` e `data/processed/scenarios/`). Os dados brutos ficam em `data/`; o relatório técnico é `docs/relatorio_validacao_hidrologica_oros.md`.

## 10. Fontes de dados

- [Portal Hidrológico do Ceará — FUNCEME/COGERH](https://www.hidro.ce.gov.br/)
- [ANA — Sistema de Acompanhamento de Reservatórios](https://www.ana.gov.br/sar/nordeste-e-semiarido/nordeste-e-semiarido/ceara)
- [ANA — Consulta histórica](https://www.ana.gov.br/sar0/Medicao)
- [INMET — Dados meteorológicos](https://portal.inmet.gov.br/)

Os dados utilizados deverão manter informações de origem, período, unidade, transformações e limitações.

## 11. Princípios científicos

O projeto seguirá os seguintes princípios:

- Não presumir vantagem quântica.
- Não confundir simulações com resultados operacionais.
- Documentar hipóteses e parâmetros.
- Preservar a rastreabilidade dos dados.
- Validar modelos matemáticos antes de executar experimentos quânticos.
- Comparar algoritmos em condições equivalentes.
- Reportar resultados negativos e limitações.

## 12. Estado atual e próximos passos

A cadeia completa (dados → cenários → MILP + CVaR → QUBO → QAOA) foi implementada e executada em escala reduzida. **Os resultados não validam o balanço hídrico nem constituem recomendação operacional**: demandas, pesos, volume morto e os parâmetros de B e C são hipóteses. Em 8 qubits **não há evidência de vantagem quântica**; o QUBO é um substituto aproximado do problema. Ver seções 4.5–4.9 do relatório técnico.

**Marco concluído: M1 — Classical-to-QUBO Validation (com ressalvas)**

1. Coletar dados históricos do Reservatório Orós.
2. Validar a qualidade e consistência das séries.
3. Implementar o balanço hídrico.
4. Construir cenários hidrológicos.
5. Implementar a otimização clássica com CVaR.
6. Validar a formulação discretizada.
7. Construir e testar o QUBO.
8. Comparar o ótimo QUBO com o modelo clássico.

A implementação de QAOA em instâncias maiores será iniciada após a validação dos componentes anteriores.

## 13. Referências técnicas

- [Qiskit Optimization — Converters](https://qiskit-community.github.io/qiskit-optimization/tutorials/02_converters_for_quadratic_programs.html)
- [QAOA — IBM Quantum](https://qiskit.qotlabs.org/docs/tutorials/quantum-approximate-optimization-algorithm)
- [Warm-start QAOA — Qiskit](https://qiskit-community.github.io/qiskit-optimization/tutorials/10_warm_start_qaoa.html)
- [Advanced QAOA Techniques — IBM Quantum](https://quantum.cloud.ibm.com/docs/en/tutorials/advanced-techniques-for-qaoa)

## Licença

