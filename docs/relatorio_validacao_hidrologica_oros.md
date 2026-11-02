# Relatório de validação hidrológica preliminar — Reservatório Orós

**Status:** preliminar. Caracteriza os dados disponíveis e lista o que impede o balanço hídrico. **Não** valida um modelo hidrológico.
**Reprodução:** `experiments/01_data_validation.ipynb` (código em `src/data/`).

## 1. Fontes

| Fonte | Arquivo | Período | Variáveis | Observação |
|---|---|---|---|---|
| Portal Hidrológico CE | `data/reserv-ors-capac-175236-portal-hidrologico-ce.csv` | 02/11/2006–29/10/2026 (7.302 dias) | Volume (hm³) | Capacidade no nome do arquivo não verificada |
| ANA/SAR | `data/raw/Histórico_ORÓS.xls` (HTML salvo como `.xls`) | 01/01/2025–29/10/2026 (667 dias) | Capacidade, cota (m), volume útil (hm³), volume (%) | Capacidade informada: 1.940 hm³ |

Unidade de ambas: hm³, separador decimal vírgula. Conversão da ANA para CSV em `data/processed/`.

## 2. Qualidade das séries

- **Portal:** sem datas duplicadas, sem dias ausentes, ordenada. **9 valores vazios:** 14/12/2010; 30–31/07/2011; 19–21/10/2013; 07–09/12/2013. Tratamento ainda não definido.
- **ANA:** sem duplicatas, lacunas ou valores inválidos no período.

## 3. Achados e o que eles NÃO permitem concluir

### 3.1 Saturação do Portal em 1.752,36 hm³
- **Observado:** o valor máximo se repete em 489 dias (2008, 2009, 2011, 2025, 2026), com o último em 14/07/2026. Nos 168 dias do período comum, a cota da ANA nesses dias varia de 199,50 a 200,26 m.
- **Não se pode concluir** que 1.752,36 hm³ seja o limite físico ou o nível do vertedouro. Pode ser truncamento da série, volume operacional de referência ou outra definição. Falta documentação técnica.

### 3.2 Divergência Portal × ANA
- **Observado (período comum, 667 dias):** com o Portal abaixo da saturação (499 dias), Portal − ANA tem mediana de 37,5 hm³ (intervalo −82 a +63), e 107 dias são idênticos. Com o Portal saturado, a ANA chega a 2.844 hm³ (146,6 % de 1.940 hm³).
- **Não se pode concluir** que o reservatório tenha excedido sua capacidade física. A hipótese mais plausível é uma diferença de curva cota–volume ou de referência de "volume útil", **ainda não verificada**.
- **Séries idênticas desde 13/07/2026:** indica compatibilidade recente, mas não comprova equivalência histórica.

### 3.3 Saturação e balanço hídrico
Com o estoque saturado, a variação do volume não revela a afluência total, porque o excedente sai como vertimento. Sem afluência e vertimento independentes, esses períodos (cerca de 7 % da série do Portal) não podem ser reconstruídos.

## 3.4 Evidência externa sobre a divergência (atualização)

Fontes (jornalísticas, não técnicas primárias — ver limitações):
- [Diário do Nordeste, 14/04/2026](https://diariodonordeste.verdesmares.com.br/ceara/oros-vai-sangrar-cogerh-se-reune-com-dnocs-para-definir-real-volume-do-2-maior-acude-do-ce-1.3757251): em 14/04/2026 a Cogerh (Portal Hidrológico) indicava **88,93 %** e o Dnocs **99,58 %** (faltavam 4 cm para a cota de sangria). O Dnocs usa os dados do **projeto original**; a Cogerh usa **estudos batimétricos mais recentes**. Reunião Cogerh–Dnocs marcada para 16/04/2026; desfecho não encontrado.
- [O POVO, 02/05/2025](https://mais.opovo.com.br/colunistas/honorio-barbosa/2025/05/02/sangria-do-oros-revelou-erro-da-cogerh.html) (coluna de opinião): a batimetria da Cogerh diferia em mais de 10 % do volume do Dnocs; em 17/04/2025, 98,26 % (Dnocs) × 87,63 % (Cogerh).
- Cota de sangria: a Cogerh adota 199,50 m como 100 %; o Dnocs, 199,52 m (matéria antiga do Diário do Nordeste, via busca; não lida na íntegra). Capacidade nominal: 1.940 hm³.

**Cruzamento com os nossos dados (verificado):**
- Em 14/04/2026 o arquivo ANA traz 88,93 % e cota 199,48 m — **o mesmo percentual que a Cogerh divulgou**, e a cota coincide com "4 cm abaixo" de 199,52 m. Logo, o `volume_pct` e o volume útil da ANA parecem ser **% sobre 1.940 hm³ com a curva atualizada (Cogerh)** nessa data.
- O Portal marca 1.752,36 hm³ nas cotas ≈ 199,50–199,53 m (ex.: 16/04/2026, cota 199,53). Isso é **consistente com** 1.752,36 hm³ ser o volume na cota de sangria pela curva batimétrica nova (≈ 90 % de 1.940 hm³). Hipótese **bem apoiada, mas não confirmada** por documento técnico.
- Acima da cota de sangria a ANA continua a computar volume (até 2.844 hm³ a 200,26 m), enquanto o Portal fica truncado: o volume acima do vertedouro é extrapolação/definição e **não deve ser usado como armazenamento** sem a curva oficial.

**Limitações:** não foi obtida a tabela cota–área–volume (nem a antiga do Dnocs, nem a batimétrica da Cogerh), nem o volume morto, nem o resultado da reunião de 16/04/2026. As duas matérias são jornalísticas.

## 4. Lacunas que impedem o balanço V(t+1) = V(t) + I(t) − E(t) − R(t) − Z(t)

| Termo | Situação |
|---|---|
| V — volume | Duas séries inconsistentes; fonte de referência não escolhida |
| I — afluência | **Sem dados** |
| E — evaporação | **Sem dados** (candidata: INMET; exige curva cota–área) |
| R — retiradas | **Sem dados** |
| Z — vertimento | **Sem dados** |
| Demandas setoriais | **Sem dados** |
| Curva cota–área–volume | **Não obtida** |

## 4.1 Fontes candidatas para os termos faltantes (levantamento web, não verificado)

| Termo | Candidata | Situação |
|---|---|---|
| R — retiradas/liberações | Alocação negociada anualmente por Cogerh e comitês de bacia. Notícias citam vazão média **5.300 l/s** (≈ 167 hm³/ano) para o ciclo até 2027, contra 4.500 l/s em 2024 ([Diário do Nordeste](https://diariodonordeste.verdesmares.com.br/ceara/castanhao-oros-e-banabuiu-veja-como-sera-usada-a-agua-dos-maiores-acudes-do-ce-ate-2027-1.3776198), [O POVO](https://mais.opovo.com.br/jornal/cidades/2024/07/10/comites-definem-vazao-de-liberacao-das-aguas-do-castanhao-oros-e-banabuiu-ate-2025.html)) | Valores de notícia, **não** série diária; solicitar vazão operada à Cogerh |
| I — afluência | Não localizada série pública para o Orós. Hidroweb/ANA (postos fluviométricos a montante) e dados operacionais da Cogerh são os caminhos; dissertação UFC sobre a cota máxima maximorum do Orós pode citar a série usada ([UFC](https://repositorio.ufc.br/ri/handle/riufc/59631?mode=full)) | Pendente; alternativa: afluência reconstruída por balanço nos períodos **não** saturados |
| E — evaporação | Portal Hidrológico (FUNCEME/COGERH) e INMET. Estações automáticas INMET próximas (lista da [API de estações](https://apitempo.inmet.gov.br/estacoes/T), lista não lida por inteiro): A319 Iguatu (situação "Pane"), A358 Jaguaribe (operante), A332 Morada Nova, A369 Quixadá. Estações automáticas medem temperatura, umidade, vento e radiação, não evaporação direta: seria preciso **estimá-la** (ex.: Penman) | Pendente; download de dados exige BDMEP/API com cadastro (não testado; a conexão por `curl` foi recusada neste ambiente); exige curva cota–área |
| Z — vertimento | Sem fonte; só estimável após resolver curva e afluência | Pendente |

## 4.2 Reconstrução preliminar da afluência líquida

`I_net = V(t+1) − V(t) + R`, com R = 5,3 m³/s constante, Z = 0, E = 0, apenas em dias consecutivos e abaixo de 1.752,36 hm³ (`src/hydrology/water_balance.py`, `experiments/02_net_inflow_reconstruction.ipynb`).

- 6.795 de 7.302 dias válidos; **58 % dos dias e 129 de 228 meses têm I_net < 0** (σ diário ≈ 3,8 hm³). Trocar R para 4,5 m³/s quase não altera isso.
- Como a afluência não é negativa, o balanço simplificado **omite saídas** (evaporação, retiradas reais ≠ 5,3 m³/s, infiltração, erro de medição). `I_net` portanto **não é um limite inferior de afluência**: é `I − E − (R_real − R_assumido)`.
- Só os meses de cheia dão informação útil sobre afluência. Os dias saturados (≈ 7 %), os de maior afluência, ficam de fora, o que enviesa a série.
- **Forma completa:** `I_net = I − E − (R_real − R_assumido) − Z`, válida se não houver outras perdas relevantes (ex.: infiltração). Valores negativos são evidência de que o modelo simplificado não explica a variação do armazenamento; não são afluência negativa e não devem ser descartados.
- **Ressalva:** em meses secos, −I_net só estima as saídas não modeladas se a afluência for desprezível ou conhecida; caso contrário mede a diferença entre entradas e saídas desconhecidas.
- **Conclusão:** esta reconstrução é uma **linha de base experimental** e não substitui dados de afluência.

## 4.3 Evaporação estimada e teste de consistência (`experiments/03_evaporation_estimation.ipynb`)

- **Dados:** NASA POWER (satélite/reanálise) no ponto da barragem, 2006–2026 (`data/raw/meteo/`), **não** INMET. Penman de água livre, sem armazenamento de calor.
- **Área do espelho:** curva cota–área não obtida; usada `A = A_full·(V/1940)^k` como **suposição** (faixa A_full 150–250 km², k 0,5–0,8). Os valores de E em hm³ dependem dela e são apenas ilustrativos.
- **Sanidade:** lâmina média de **≈ 2.980 mm/ano**, provavelmente alta para o semiárido (referência típica não verificada); tratar E como limite superior.
- **Teste (ago–nov, assumindo afluência ≈ 0):** o resíduo `−I_net − E` é **negativo em 19 de 21 anos** (mediana ≈ −0,38 hm³/dia ≈ −4,4 m³/s; intervalo −9,7 a +0,9). Ou seja, `E + 5,3 m³/s` explica **mais** queda de volume do que a observada. Em 2017–2019 (seca severa) o volume cai praticamente só no ritmo de R (I_net ≈ 0), apesar de E estimada ≈ 0,4 hm³/dia.
- **Interpretação possível, não identificável:** (a) E superestimada; (b) retirada real bem menor que 5,3 m³/s (plausível em seca; a vazão de 5,3 é do ciclo 2026–27); (c) afluência/aporte residual; (d) erro de A(V) ou da série de volume. Os dados atuais não separam essas causas.
- **Implicação:** 5,3 m³/s não pode ser usada como retirada histórica. Retiradas reais (Cogerh) e curva cota–área são pré-requisito para fechar o balanço.

## 4.4 Análise de sensibilidade (`experiments/04_hydrological_sensitivity_analysis.ipynb`)

Grade de 560 combinações: A_full ∈ {150…250} km², k ∈ {0,5…0,8}, escala de E ∈ {0,7…1,3}, R ∈ {0; 2,65; 4,5; 5,3} m³/s; saída em `results/sensitivity_grid.csv`. Entradas classificadas como observação / estimativa / hipótese em `src/hydrology/sensitivity.py::PROVENANCE`.

- **Conferência de Penman:** unidades do NASA POWER verificadas (radiação em MJ m⁻² dia⁻¹, etc.); teste unitário da conversão mm→hm³. Limitações restantes: dados de grade, sem armazenamento de calor.
- **Portal × ANA (499 dias não saturados):** diferença mediana de 37,5 hm³ (p5–p95: 0 a 61,6).
- **Restrição I ≥ 0 só dá limite inferior:** equivale a E + R ≥ −ΔV. Nos meses secos (ago–nov), as saídas totais foram **pelo menos ≈ 15,7 m³/s** (mediana; 10–90 %: 5,6–22,5), supondo afluência ≥ 0. Com R ≤ 5,3, isso exige E ≳ 10 m³/s. Valores baixos de E (escala 0,7) deixam 61 % dos dias secos com afluência implícita negativa (21 % com escala 1,0; 13 % com 1,3).
- **O que a análise não faz:** não fixa um teto para E nem para R; "menos negativos" com E maior não valida E.
- **Cenários A–C (Z = 0):** A gera afluência implícita negativa em anos secos (2013, 2015–2017); B e C não. Totais anuais diferem por fator 2–4 entre cenários. Cenário D (vertimento) não implementado: Z não é identificável nos dias saturados.
- **Uso:** resultados são cenários condicionados a hipóteses, não afluências observadas; manter separados "histórico observado" e "cenários sintéticos".

## 4.5 Geração de cenários hidrológicos (`experiments/05_hydrological_scenario_generation.ipynb`)

**Estado:** implementação concluída e testada; **não há validação científica** do balanço hídrico nem dos cenários.

### Metodologia
- Código em `src/scenarios/` (`schema`, `historical`, `synthetic`, `temporal`, `generator`). Horizonte **jul–dez** (6 passos mensais), unidades hm³/mês, saída em `data/processed/scenarios/` (`scenario_metadata.csv`, `scenario_months.csv`, `block_eligibility.csv`) e `results/scenario_generation_config.json` (sementes, configurações, hash).
- **Família A (`historical_storage`)** — 20 cenários: 19 anos do Portal (2007–2025) e 1 da ANA (2025), **sem mistura de fontes**. Só armazenamento observado no 1º dia do mês; sem afluência, evaporação ou retirada. Meses ausentes ou saturados são mantidos e marcados (`usable = False`, `exclusion_reason`).
- **Família B (`synthetic`)** — 128 cenários, condicionados a hipóteses: afluência **implícita** `I = ΔV + E + R` (Z = 0, meses completos não saturados). Métodos: replay condicionado de anos históricos (11 em B, 13 em C); **bootstrap sazonal em blocos de 3 meses** (50 sorteios por configuração, sementes registradas); 2 cenários de estresse por configuração (jul–dez mais seco; seca jul–set seguida de out–dez mais úmido — composição, não sequência histórica). Simulação com limites físicos explícitos (E, R, armazenamento ≥ 0; curtailment e vertimento sinalizados, **nunca** ajuste de parâmetros para fechar o balanço).
- `availability = armazenamento inicial + afluência implícita − evaporação`: disponibilidade **bruta**, antes das retiradas, sem volume morto.

### Parâmetros (provisórios; recuperados do experimento 04)
| Config | A_full (km²) | k | escala E | R (m³/s) |
|---|---|---|---|---|
| A_low | 150 | 0,8 | 0,7 | 2,65 |
| B_mid | 200 | 0,7 | 1,0 | 4,5 |
| C_high | 250 | 0,5 | 1,3 | 5,3 |

Cap de armazenamento: 1.752,36 hm³ (saturação do Portal; hipótese).

### Resultados da revisão do experimento 04
- Fatores que mais explicam a variância da afluência implícita seca: escala de E (≈ 41 %), A_full (≈ 32 %), R (≈ 21 %), k (≈ 5 %); E e A são multiplicativos e inseparáveis. A incerteza é dominada por **evaporação/geometria**.
- Viabilidade física (mês completo, afluência implícita ≥ 0): **A: 7 de 108 meses completos viáveis** (94 % negativos) — com essas hipóteses A **contradiz** a queda observada do armazenamento e **não gera cenários** (parâmetros não foram alterados). B: 103/108; C: 108/108. Isso **não** valida B nem C; ≥ 0 é condição necessária, não critério de calibração.
- A diferença entre B e C na afluência implícita jul–dez é de ≈ 117–229 hm³, bem maior que o desvio-padrão interanual dentro de B (≈ 35 hm³): a incerteza das hipóteses supera a variabilidade climática representada.

### Dependência temporal
Poucos anos viáveis (11–13) e ~80 pares mês-a-mês (± ≈ 0,22 no r) impedem calibrar um modelo de dependência. O r₁ da afluência implícita é ≈ 0,29 (B) e ≈ 0,76 (C), logo **depende da hipótese de E**. O bootstrap sazonal preserva a dependência dentro de cada bloco (jul–set, out–dez) e **não** na fronteira set/out. Não foi usado bootstrap de blocos móveis, que emendaria dezembro com julho de anos diferentes.

### Validação (técnica)
- 16 testes de cenários (23 no total) passam: reprodutibilidade com semente, continuidade, alinhamento de datas, dados ausentes e saturação, unidades, não negatividade, vertimento no cap, proveniência, ausência de mistura observado/sintético, extração jul–dez, blocos copiados intactos e escolha dos extremos nos estresses. Uma mutação deliberada (omitir R no afluente implícito) foi detectada por 2 testes.
- Regeneração com a mesma semente produz hash idêntico (`results/scenario_generation_config.json`).
- Isto verifica o **código**, não a **representatividade física**.

### Limitações
1. Afluência implícita não é medida; dias saturados (≈ 7 %), em geral de maior afluência, ficam fora. 2. E por grade; A(V) e R hipotéticos. 3. Meses com afluência implícita negativa são excluídos (pode enviesar para cima). 4. Disponibilidade bruta, sem volume morto. 5. Cenários de estresse são compostos. 6. Não são previsões.

### Implicações para a otimização (exp. 06)
Usar os cenários como **entradas sintéticas rotuladas**, nunca como afluências históricas. Tratar o intervalo B–C como incerteza estrutural a testar por sensibilidade nas decisões de alocação. Congelar `data/processed/scenarios/` antes de iniciar o MILP + CVaR.

## 5. Próximas atividades (ordem)

1. Obter a curva cota–área–volume (Dnocs/projeto original e Cogerh/batimetria) e o volume morto; confirmar a hipótese da §3.4. Pedir a Cogerh/Dnocs o resultado da reunião de 16/04/2026 e a tabela batimétrica.
2. Obter afluência independente.
3. Obter evaporação.
4. Obter retiradas e demandas.
5. Construir o balanço hídrico e testar conservação de massa.

## 6. Decisão

Não iniciar QUBO/QAOA. A otimização só faz sentido sobre uma representação física validada.
