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
- 16 testes de cenários (23 no total na época; 47 no total atualmente, ver 4.9) passam: reprodutibilidade com semente, continuidade, alinhamento de datas, dados ausentes e saturação, unidades, não negatividade, vertimento no cap, proveniência, ausência de mistura observado/sintético, extração jul–dez, blocos copiados intactos e escolha dos extremos nos estresses. Uma mutação deliberada (omitir R no afluente implícito) foi detectada por 2 testes.
- Regeneração com a mesma semente produz hash idêntico (`results/scenario_generation_config.json`).
- Isto verifica o **código**, não a **representatividade física**.

### Limitações
1. Afluência implícita não é medida; dias saturados (≈ 7 %), em geral de maior afluência, ficam fora. 2. E por grade; A(V) e R hipotéticos. 3. Meses com afluência implícita negativa são excluídos (pode enviesar para cima). 4. Disponibilidade bruta sem volume morto *(tratado na 4.5.1: agora há disponibilidade operacional com volume morto hipotético)*. 5. Cenários de estresse são compostos. 6. Não são previsões.

### Implicações para a otimização (exp. 06)
Usar os cenários como **entradas sintéticas rotuladas**, nunca como afluências históricas. Tratar o intervalo B–C como incerteza estrutural a testar por sensibilidade nas decisões de alocação. Congelar `data/processed/scenarios/` antes de iniciar o MILP + CVaR.

## 4.5.1 Correções após a revisão visual dos gráficos 05 (e decisões sobre B e C)

- **B e C mantidas** como configurações experimentais provisórias; **A** fica no código só para sensibilidade (7 de 108 meses viáveis). Todas fisicamente admissíveis segundo a restrição testada, **não** hidrologicamente validadas.
- **Revisão visual:** (i) as 50 trajetórias do bootstrap colapsam em ~11–13 curvas distintas, porque o armazenamento inicial era atrelado ao ano do primeiro bloco: as bandas p10–p90 e os boxplots de disponibilidade refletiam sobretudo o **estado inicial**, não a hidrologia; (ii) o cenário "seca→recuperação" de B não recuperava (Jul–Set mais seco em afluência partia de 1.500 hm³): **corrigido** para exigir início em armazenamento baixo (tercil inferior); (iii) o eixo de anos exibia 2007,5 (formatação) e B tem total negativo em 2016.
- **Disponibilidade operacional:** além da disponibilidade bruta, os cenários agora trazem `dead_volume_hm3` e `operational_availability_hm3 = max(0, S + I − E − V_morto)`. O volume morto não é conhecido: usa-se **109,78 hm³ (menor volume já observado no Portal, 17/02/2020) como limite superior empírico**, com 0 como sensibilidade. Na otimização, as retiradas de cada mês alteram o armazenamento dos seguintes (dinâmica preservada).
- **Viés de seleção:** nenhum registro é descartado: `block_eligibility.csv` guarda todos os meses com motivo de exclusão; `negative_policy="floor_at_zero"` inclui os meses de afluência implícita negativa truncados em 0, **sinalizados** (`floored`), preservando `I_raw_hm3`.
- **Amostra efetiva:** os 50 sorteios de bootstrap **não** são 50 observações independentes (poucas combinações de anos de origem). Na otimização, o conjunto de incerteza são as sequências de afluência dos anos históricos viáveis com **pesos iguais por ano** (suposição, não probabilidade); o bootstrap serve apenas para avaliação de sensibilidade.
- Armazenamento inicial passou a ser **fator experimental** (estado conhecido na decisão), separado da incerteza hidrológica.

## 4.6 Alocação clássica sob incerteza: MILP + CVaR (`experiments/06_classical_allocation.ipynb`)

**Estado:** implementado, testado e executado; **sem validação hidrológica**. Resultados valem **para as hipóteses declaradas**.

### Formulação (`src/optimization/`)
- Plano mensal de alocação `a[k,t]` (urbano, irrigação), **igual em todos os cenários** (1º estágio). A entrega segue uma regra implementável, sem antecipar o futuro: urbano primeiro, depois irrigação, limitada pela água acima do volume morto. Perda `L = Σ w_k Σ_t (D_kt − y_kt)`; objetivo `(1−λ)·E[L] + λ·CVaR_α(L)`, α = 0,8, via Rockafellar–Uryasev. Os **binários** codificam o min/max exato da regra (daí MILP). Pyomo + HiGHS; 72 MILPs, todos ótimos.
- **Hipóteses (não observações):** demanda urbana 1,5 m³/s; irrigação 3–5 m³/s (sazonal); pesos urbano 3 × irrigação 1; volume morto 109,78 hm³; limite de armazenamento 1.752,36 hm³; evaporação fixa ao longo de uma trajetória de referência (não reage à decisão); pesos iguais entre anos.
- Incerteza: sequências de afluência implícita de 11 anos (B) e 13 anos (C). B e C são **resolvidas separadamente**, com a mesma formulação, sem misturá-las numa distribuição.
- **Verificações:** o objetivo do MILP coincide com o do simulador (teste automatizado) e não perde para a enumeração em grade.

### Resultados
- **Regime de escassez:** com demanda base e armazenamento inicial ≥ 300 hm³ não há déficit; o problema só é não trivial perto do estado de seca observado em 2017–2019 (Jul-1: 201–230 hm³). Níveis usados: S₀ ∈ {200, 300, 450} hm³; demanda ×1 e ×2 (estresse hipotético).
- **Config. B, S₀ = 200, demanda ×2 (λ = 0,5):** o MILP concentra o déficit na irrigação (≈ 69 % de déficit; urbano ≈ 0 %), com perda esperada 87,5 e CVaR 96,3, contra: demanda-seguindo 106,6/137,4; E01 linear 131,1/146,4; E02 prioritário 91,7/111,0. **Config. C, mesmo caso:** MILP 41,3/111,4; demanda 42,4/117,8; prioritário 51,9/111,4; linear 65,3/121,4. Ganhos modestos e dependentes do caso: a regra "pedir toda a demanda" já é boa quando a escassez é moderada.
- **Robustez B × C (λ = 0,5, S₀ = 200, ×2):** o plano ótimo de B planeja só ≈ 36 % da irrigação; o de C, ≈ 96 %. Distância entre planos: 77 de 175 hm³ de demanda. Arrependimento cruzado: plano de C avaliado em B perde 30,5; plano de B avaliado em C perde 14,7. **Sob escassez forte, a política depende da hipótese hidrológica** (B × C), e as amostras de anos também diferem entre B e C.
- **λ:** em B o plano é praticamente estável para λ ≥ 0,25; em C há **mudança de regime** entre λ = 0,5 e 0,75 (perda esperada 41 → 74; CVaR 111 → 94, com a irrigação planejada caindo): a aversão a risco altera a política de forma não contínua.
- **Seleção:** em B, incluir os 2 anos que a política `exclude` descarta (4 meses truncados em 0) eleva a perda esperada de 4,4 para 10,2 e o CVaR de 8,9 para 34,7 (S₀ = 200, ×1); **as conclusões de B dependem da seleção**. Em C não há meses truncados.
- **Volume morto:** com V_morto = 0 quase não há déficit; com 109,78 hm³ há escassez grande. **Esta é a hipótese de maior efeito**, maior que B × C.
- **Fora da amostra (leave-one-year-out; n = 11–13, exploratório):** sob escassez forte (S₀ = 200, ×2) o MILP tem a menor perda média no ano omitido em B (87,9 vs 92,4/106,6/131,8) e empata com a demanda-seguindo em C (41,4 vs 42,4); na cauda (20 % piores) vence em B (97,3 vs 109,8/137,0/144,2) e empata em C. Com escassez moderada (S₀ = 300, ×2), o MILP piora a média mas melhora a cauda (B 20,3 vs 24,8; C 31,3 vs 36,0): é o efeito esperado de um objetivo avesso a risco.

### Limites
Demandas, pesos, volume morto e evaporação de referência são hipóteses; B e C são provisórias; n pequeno; o déficit é concentrado na irrigação em boa parte pelos **pesos** impostos (3:1); resultados **não são recomendação operacional**.

## 4.7 Formulação QUBO e validação (`experiments/07_qubo_formulation.ipynb`)

- **Discretização:** 4 grupos (urbano/irrigação × jul–set/out–dez), cada um escolhe 2ᵇ níveis de fração da demanda (b = 2: {0, 1/3, 2/3, 1}; 8 qubits; 256 planos).
- **Validação independente:** o **MILP discreto coincide exatamente com a enumeração exaustiva** (J = 93,8755 em B; 79,5423 em C; diferença 0) para b = 1, 2, 3. O custo da discretização em relação ao MILP contínuo é 2,2 % (B) e 4,1 % (C) em b = 2; não é monotônico em b (níveis k/3 e k/7 não são aninhados).
- **O QUBO não é exato.** O objetivo exato (regra de racionamento + CVaR) não é quadrático nos bits; o QUBO é um **substituto ajustado por mínimos quadrados** às 256 avaliações exatas. Qualidade (sem pesos): B: R² = 0,985, Spearman 0,991, **gap de 5,4 em J**; C: R² = 0,997, Spearman 0,998, **gap de 4,2**. O mínimo do QUBO é o 2º melhor plano real em B e o 3º em C, **não o ótimo**.
- **Efeito hidrológico do erro:** em B, o plano do mínimo do QUBO eleva o déficit urbano de 0,4 % para 6,4 % (o erro realoca risco para o setor de maior peso), mesmo com gap de energia pequeno.
- **Diagnóstico:** um ajuste ponderado perto do mínimo (τ = 20) recupera o ótimo real nas duas configurações, **mas usa o conhecimento do ótimo** para definir os pesos; não está disponível num pipeline real e é apenas um limite superior de fidelidade.
- A conversão QUBO → Ising foi conferida com `qiskit-optimization` (diferença máxima 8,5·10⁻¹⁴).
- **Conclusão:** a formulação discretizada é **validada como aproximação** (e o MILP discreto como exato), mas **não** como equivalente ao ótimo clássico. A construção do QUBO exigiu enumerar o espaço, o que só é possível em instâncias pequenas.

## 4.8 Experimentos com QAOA (`experiments/08_qaoa_experiments.ipynb`)

**Escopo:** simulação **ideal** (vetor de estado exato) de QAOA padrão, warm-start e CVaR-QAOA em **8 qubits**, sobre os QUBOs do 07 (B e C; S₀ = 200 hm³, demanda ×2, λ = 0,5); COBYLA (≤ 300 avaliações), 10 sementes, p = 1, 2, 3; ruído sintético despolarizante em Aer. **Nada aqui é evidência de vantagem quântica: o espaço tem 256 estados.**

- **Custo do circuito** (base {cx, rz, sx, x}): p = 1: profundidade 48–53, 56 CX; p = 2: 78–87, 112 CX; p = 3: 108–121, 168 CX. O QUBO é denso (todos os pares).
- **Correção de métrica:** a "melhor amostra de 1024 amostras" acha o mínimo do QUBO em qualquer algoritmo (inclusive amostragem uniforme, falha ≈ 2 %), pois 1024 ≫ 256 estados; foi **descartada** como medida de desempenho. Usam-se a probabilidade por amostra (uniforme = 1/256 ≈ 0,0039), o ganho sobre o uniforme e as amostras para 99 % de confiança.
- **Desempenho computacional (média de 10 sementes):** razão de aproximação (0 = aleatório, 1 = mínimo do QUBO): B 0,56–0,72 (padrão/CVaR), 0,76–0,82 (warm); C 0,79–0,94. Probabilidade por amostra do mínimo do QUBO: 0,015–0,125, isto é, **4–32 × o uniforme**; amostras para 99 %: ≈ 32–113 (uniforme: ≈ 1.176). A variância entre sementes é grande (ex.: B, padrão, p = 2: 0,042–0,118).
- **Variantes:** o warm-start (partindo do MILP contínuo arredondado, **informação clássica explícita**) melhora a razão de aproximação (B: 0,82 × 0,70 em p = 2) mas **não** a probabilidade do mínimo, e em B reduz a do ótimo real (0,011 × 0,037), por concentrar a massa perto da solução clássica arredondada. O CVaR-QAOA (α = 0,25, p = 3) deu a maior probabilidade do mínimo em B (0,125). No QAOA padrão de C a probabilidade do mínimo **cai** com p (0,030 → 0,015) enquanto a razão de aproximação sobe: o algoritmo concentra massa em soluções boas, não no mínimo exato. Ganhos com p são modestos e não monotônicos.
- **Comparação clássica (300 avaliações, 20 sementes):** simulated annealing no J exato acha o ótimo real em 20/20; SA no QUBO acha o mínimo do QUBO em 100 % (portanto o plano subótimo); busca aleatória no J exato acha o ótimo em 70 % (esperado ≈ 69 %). Em hardware real o QAOA custaria ≈ avaliações × amostras (≈ 3·10⁵ execuções de circuito), contra 300 avaliações do SA. **Nenhum resultado sugere vantagem quântica.**
- **Qualidade hidrológica ≠ desempenho computacional:** o plano que o QAOA entregaria (mínimo do QUBO) tem gap de J de 5,4 (B) e 4,2 (C) em relação ao ótimo real e, em B, déficit urbano de 6,4 % contra 0,4 %. Mesmo que o QAOA encontre o mínimo do QUBO com certeza, o erro do substituto domina.
- **Ruído (E09):** com ruído de 2 qubits p2 nas CX (e p2/10 em 1 qubit), a razão de aproximação cai monotonicamente: B padrão 0,75 (sem ruído, amostrado) → 0,66 (p2 = 5·10⁻³) → 0,45 (2·10⁻²); C padrão 0,93 → 0,84 → 0,60. Em p2 ≥ 10⁻² o benefício sobre o aleatório se perde em grande parte. Modelo **sintético**, não calibrado em hardware.
- **Fora da amostra (E10, parcial):** 50 sequências por bootstrap sazonal sobre os **mesmos anos** (portanto **não independentes** do treino). Em B, a diferença de J entre o ótimo real e o mínimo do QUBO praticamente some (100,5 × 100,9), embora o déficit urbano continue 2,0 % × 7,6 %; E02 prioritário fica próximo do ótimo discreto em B (102,5) e C (75,4 × 74,3); E01 linear é bem pior. A validação por ano omitido está na seção 4.6.
- **Limites:** 1 instância por configuração; 8 qubits; treino com probabilidades exatas; COBYLA com ≤ 300 avaliações; sem dispositivo real.

## 4.9 Síntese e limites finais da pesquisa

**O que foi construído e testado (47 testes automatizados):** pipeline reproduzível de dados → evaporação → cenários → MILP + CVaR → QUBO → QAOA, com proveniência (observação/estimativa/hipótese) preservada.

**Conclusões que os dados sustentam**
1. Portal e ANA divergem principalmente por referência de volume (curva batimétrica); a explicação é **plausível e apoiada por notícias**, mas não confirmada por documento técnico.
2. O balanço hídrico **não é identificável** com os dados disponíveis (sem afluência, retirada, vertimento e curva cota–área). Os cenários são **condicionados a hipóteses**; afluência é implícita, nunca observada.
3. A incerteza dominante é de **modelagem**, em ordem decrescente de efeito nos resultados de alocação: volume morto, hipótese B × C (evaporação/geometria/retirada), viés de seleção dos meses viáveis, e só depois a variabilidade climática representada.
4. Com escassez forte, o MILP + CVaR reduz a cauda de perdas e a perda esperada em relação às referências, de modo modesto e dependente do caso; com escassez moderada, a regra simples "pedir toda a demanda" é competitiva na média.
5. O QUBO é um **substituto aproximado** (R² 0,985–0,997); o ótimo discreto foi validado de forma independente (MILP discreto = enumeração). O mínimo do QUBO **não** é o ótimo hidrológico.
6. O QAOA concentra probabilidade em soluções boas (4–32 × o uniforme) mas, em 8 qubits, **não** supera nem se compara em custo a métodos clássicos triviais; o ruído degrada o benefício. **Não há evidência de vantagem quântica.**

**O que NÃO está estabelecido:** que B ou C representem o Orós; que as políticas sejam adequadas à operação real (demandas, pesos e volume morto são hipóteses); que o QUBO escale (a construção exigiu enumerar o espaço); que o resultado valha em hardware real ou em instâncias maiores.

**Dados que mudariam as conclusões:** curva cota–área–volume (Dnocs e Cogerh) e volume morto; vazões operadas e retiradas por setor; afluência independente; evaporação medida; demandas reais.

**Trabalhos futuros:** formulação QUBO **exata por construção** (variáveis auxiliares, penalidades e restrições por cenário) em instâncias de 20–40 variáveis, com solvers de QUBO; modelo de decisão multiestágio; calibração com dados reais; execução em hardware/ruído calibrado; comparação em instâncias maiores onde a enumeração é inviável.

## 5. Próximas atividades (ordem)

1. Obter a curva cota–área–volume (Dnocs/projeto original e Cogerh/batimetria) e o volume morto; confirmar a hipótese da §3.4. Pedir a Cogerh/Dnocs o resultado da reunião de 16/04/2026 e a tabela batimétrica.
2. Obter afluência independente.
3. Obter evaporação.
4. Obter retiradas e demandas.
5. Construir o balanço hídrico e testar conservação de massa.

## 6. Decisão

Não iniciar QUBO/QAOA. A otimização só faz sentido sobre uma representação física validada.
