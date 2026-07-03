# SeniorRx Monitor — Análise Técnica Aprofundada

> Documento de referência que escrevi para explicar, de ponta a ponta, **por que**
> cada parte deste sistema existe e **como** ela funciona. Serve tanto como memória
> técnica do projeto quanto como base para apresentá-lo em entrevistas.
>
> Aviso: projeto de pesquisa/educação. Não substitui julgamento clínico e usa
> exclusivamente dados sintéticos.

---

## 1. O problema que decidi resolver

Pacientes idosos (≥65 anos) concentram a maior carga de **polifarmácia** — o uso
simultâneo de vários medicamentos — e, com ela, de **reações adversas a
medicamentos (RAM)**. Boa parte dessas reações é previsível e evitável, porque a
literatura geriátrica já catalogou quais fármacos têm relação risco-benefício
desfavorável nessa população. O instrumento de referência para isso é o
**AGS Beers Criteria® 2023**, publicado pela American Geriatrics Society.

O problema prático é que essa checagem raramente é feita de forma sistemática no
momento da prescrição. Eu quis construir um sistema que faça exatamente isso:
receber o perfil farmacoterapêutico de um paciente idoso e devolver, de forma
auditável e explicável, os **Medicamentos Potencialmente Inapropriados (PIM)**,
as **interações perigosas**, a **polifarmácia** e um **nível de risco**
consolidado — cada alerta rastreável à sua fonte científica.

Defini desde o início três princípios inegociáveis:

1. **Transparência total.** Nada de "caixa-preta": todo alerta aponta para a
   regra e a referência que o gerou.
2. **Segurança e privacidade por construção.** Sem PII no modelo de dados; tudo
   sintético; segredos fora do código.
3. **Honestidade científica.** O sistema é apoio à decisão, não diagnóstico, e eu
   marco explicitamente o que é regra validada versus o que é sinal estatístico
   exploratório.

---

## 2. Por que arquitetura limpa (e o que isso me deu)

Organizei o código em quatro camadas concêntricas, com a regra de dependência
apontando sempre para dentro:

```
interface  →  application  →  domain  ←  infrastructure
(FastAPI/     (serviços      (regras     (SQLAlchemy,
 Streamlit)    de caso de     clínicas    modelo de ML)
               uso)           puras)
```

- **`domain/`** é o coração e não importa **nada** de framework — nem SQLAlchemy,
  nem FastAPI, nem pandas. São `dataclasses` imutáveis (`Patient`, `Prescription`,
  `BeersCriterion`, `Alert`) e os três motores de regra. Isso me permite testar
  100% da lógica clínica em milissegundos, sem subir banco nem servidor.
- **`application/`** orquestra os motores e devolve DTOs — objetos de saída que
  não vazam os enums internos do domínio para o mundo externo.
- **`infrastructure/`** implementa o "como": mapeamento ORM, repositórios que
  traduzem linhas de banco em entidades de domínio, e o modelo de ML.
- **`interface/`** expõe tudo via HTTP (FastAPI) e visualização (Streamlit).

O ganho concreto dessa separação apareceu na prática: quando validei o sistema,
consegui rodar os 16 testes de regra sem nenhuma dependência externa, e mais tarde
exercitei a stack inteira contra PostgreSQL real sem tocar **uma linha** de lógica
clínica. Se amanhã eu trocar Postgres por outro banco ou a API por gRPC, o
`domain/` permanece intacto.

---

## 3. O motor de regras clínicas (o núcleo de valor)

Dividi a avaliação em três motores independentes, todos operando sobre entidades
de domínio:

### 3.1 `BeersRulesEngine` — PIM
Cobre as duas primeiras categorias dos Beers 2023:
- **PIM independente de diagnóstico**: fármacos a evitar em qualquer idoso
  (benzodiazepínicos, anti-histamínicos de 1ª geração, glibenclamida, AINEs
  crônicos, relaxantes musculares, etc.). O casamento é por **prefixo ATC** —
  assim um único critério `N05BA` cobre a classe inteira dos benzodiazepínicos.
- **PIM por condição específica**: fármacos seguros em geral, mas contraindicados
  numa comorbidade (ex.: AINE em insuficiência cardíaca `I50`). Aqui cruzo o ATC
  do medicamento com os códigos **ICD-10** ativos do paciente.

Um detalhe que cuidei: certos critérios só valem acima de um **limiar de uso
crônico** (IBP > 8 semanas, metoclopramida > 12 semanas). Modelei isso comparando
`prescription.duration_days` com o limiar, para não gerar falso-positivo em uso
agudo legítimo.

### 3.2 `PolypharmacyRulesEngine`
Aplica os limiares de consenso da literatura: **≥5** medicamentos ativos =
polifarmácia (severidade moderada); **≥10** = hiperpolifarmácia (crítica, sugere
revisão estruturada / deprescrição).

### 3.3 `InteractionRulesEngine`
Faz duas coisas reusando a mesma tabela de critérios:
- **Interações medicamento-medicamento** par-a-par (`itertools.combinations`),
  cobrindo casos clássicos: opioide + benzodiazepínico, varfarina + AINE, o
  *"triple whammy"* (IECA/BRA + diurético + AINE), IECA/BRA + espironolactona.
- **Ajuste por função renal**: quando o eGFR do paciente cai abaixo do limiar de
  um critério (ex.: metformina em DRC avançada), emito alerta de ajuste.

Todos os motores respeitam o escopo do Beers: só avaliam pacientes **≥65 anos** e
**prescrições ativas**.

---

## 4. Do dado à decisão: o fluxo completo

```
Prescrição/cadastro (CSV sintético ou origem anonimizada)
        │  scripts/etl_pipeline.py
        ▼
PostgreSQL normalizado (patients, medications, prescriptions, comorbidities)
        │  PatientRepository + BeersCriteriaRepository  (infra → domínio)
        ▼
RiskScoringService.assess(patient)
   ├─ BeersRulesEngine        → alertas de PIM
   ├─ InteractionRulesEngine  → interações + ajuste renal
   ├─ PolypharmacyRulesEngine → poli/hiperpolifarmácia
   └─ (opcional) modelo de ML → probabilidade de RAM (sinal complementar)
        ▼
RiskAssessmentDTO  (nível de risco + lista de alertas explicáveis)
        ├─→ API FastAPI  (GET /patients/{id}/risk-assessment)
        ├─→ Dashboard Streamlit (visualização por paciente)
        └─→ Relatório R/Quarto (epidemiologia agregada da coorte)
```

O `RiskScoringService` converte a lista de alertas em um nível
(`BAIXO/MODERADO/ALTO/CRÍTICO`) por uma heurística transparente: qualquer alerta
**crítico** eleva a crítico; dois ou mais **altos** elevam a alto; e assim por
diante. É deliberadamente simples e auditável — a sofisticação fica na base de
critérios, não numa fórmula opaca.

---

## 5. A camada de dados

Modelei sete tabelas em PostgreSQL (`sql/schema.sql`). Escolhas que fiz de
propósito:

- **Sem PII.** `patients` guarda apenas ano de nascimento, sexo, dados
  antropométricos e um **pseudônimo não reversível** — nunca nome, CPF ou
  endereço. Idade é derivada, não armazenada.
- **UUID como chave** (extensão `uuid-ossp`), evitando o vazamento de volume que
  IDs sequenciais expõem.
- **Codificação padronizada**: medicamentos por **ATC** (OMS), comorbidades por
  **ICD-10** — o que torna o casamento de regras robusto e internacionalizável.
- **`beers_pim_criteria` como tabela dirigida por dados**: adicionar um critério
  clínico novo é inserir uma linha com sua fonte, não alterar código.
- **`JSONB`** em `risk_scores.explanation` para guardar explicabilidade
  semiestruturada sem uma tabela extra.

Um aprendizado real veio daqui. Eu havia modelado `prescriptions.is_active` como
**coluna gerada** (`GENERATED ALWAYS AS (end_date IS NULL OR end_date >=
CURRENT_DATE)`). Isso passou nos testes com SQLite, mas o PostgreSQL **rejeitou**
na subida real: expressões de coluna gerada precisam ser **imutáveis**, e
`CURRENT_DATE` não é. Corrigi movendo o cálculo de "ativa" para a view
`v_active_prescriptions` (avaliada em tempo de consulta) e para a propriedade de
domínio `Prescription.is_active`. Foi um lembrete de que só validação contra a
tecnologia-alvo real pega esse tipo de incompatibilidade.

---

## 6. O componente de Machine Learning (e sua honestidade)

Adicionei um `RandomForestClassifier` que estima a probabilidade de evento
adverso, com engenharia de features derivada apenas de dados de domínio (idade,
contagens de PIM/interações/comorbidades, eGFR — nada de PII). Escolhi Random
Forest **de propósito**: `feature_importances_` dá explicabilidade suficiente
para o contexto, e prefiro isso à performance marginal de um modelo opaco em
cenário clínico. O treino registra parâmetros, ROC-AUC e o artefato no **MLflow**.

O ponto mais importante — e que faço questão de deixar explícito — é que o
**rótulo de treino é uma proxy sintética**, não um desfecho clínico observado.
Ele existe para demonstrar o *pipeline* de MLOps de ponta a ponta, não para
afirmar capacidade preditiva real. Em `docs/clinical_validation.md` descrevo o que
seria necessário para validar com dados reais (rótulo como reinternação por RAM em
30 dias, métricas AUPRC/calibração/fairness, validação externa). O modelo é sempre
**complementar** às regras determinísticas, nunca substituto.

---

## 7. Segurança — o que fortifiquei

Tratei segurança como requisito, não como enfeite:

- **Autenticação de API** com comparação de key em **tempo constante**
  (`hmac.compare_digest`, contra timing attacks) e **fail-closed em produção**:
  com `SENIORRX_ENV=production`, a ausência de key retorna 503 em vez de abrir a
  API silenciosamente.
- **Cabeçalhos de segurança** em toda resposta (CSP, HSTS em produção, `nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy`, `Cache-Control: no-store`).
- **Rate limiting** por IP (`slowapi`), mitigando força-bruta contra a key.
- **`.dockerignore`** impedindo que `.env`, `.git` e dados entrem nas imagens;
  containers rodam como **usuário não-root**.
- **Varredura automatizada no CI**: `bandit` (SAST), `pip-audit` (CVEs) e
  `gitleaks` (segredos vazados).
- **Sem segredos no código**: tudo por variável de ambiente; `.env` nunca é
  commitado (só `.env.example`).

Deixei fora de escopo (e documentei) o que pertence à infraestrutura de deploy:
terminação TLS em proxy reverso, criptografia em repouso e WAF.

---

## 8. Privacidade e compliance

O sistema foi desenhado para **LGPD/GDPR** desde a modelagem: nenhum dado real de
paciente é usado; o schema não tem campos de PII; pacientes são referenciados por
UUID e pseudônimo. Documentei em `data/README.md` e `SECURITY.md` o que mudaria
numa adaptação para dados reais (anonimização prévia, RBAC, versionamento de dados
via DVC em storage criptografado, board de ética).

---

## 9. Qualidade: testes, tipagem e CI

- **Testes** (`pytest`): unitários cobrem cada motor de regra e o serviço de risco
  sem tocar banco; integração exercita a API contra PostgreSQL e é pulada
  automaticamente quando o banco não está disponível — o que mantém o loop de
  desenvolvimento rápido e offline.
- **Tipagem**: `mypy --strict` em todo o `src/`.
- **Lint/format**: `ruff` com um conjunto de regras deliberado.
- **CI** (GitHub Actions): lint, type-check, `security-scan`, testes com serviço
  Postgres e build das imagens Docker — mais um job agendado de *drift* com
  Evidently AI.
- Cobertura mínima configurada em **80%** (`--cov-fail-under=80`).

---

## 10. Como validei que funciona de verdade

Não me contentei com "compila". A validação foi empírica e em camadas:

1. **Lógica clínica**: 16 testes unitários verdes, cobrindo casos conhecidos da
   literatura (glibenclamida sempre PIM; benzodiazepínico + histórico de queda;
   varfarina + AINE; ajuste renal por eGFR).
2. **Integração API↔banco**: exercitei a API contra um banco SQL real, confirmando
   que ORM → repositórios → serviço de risco → rotas funcionam juntos.
3. **Stack completa com Docker**: subi `docker compose up --build` e validei a
   orquestração de ponta a ponta — Postgres saudável, serviço `init` aplicando
   schema + os critérios Beers, API respondendo e o dashboard servindo. Foi nessa
   etapa que descobri e corrigi o bug da coluna gerada não-imutável.
4. **Endpoints reais**: com 50 pacientes sintéticos carregados via ETL, a API
   classificou corretamente um paciente como risco **ALTO** — 3 PIM (AINEs, IBP),
   2 interações "triple whammy" e polifarmácia — e retornou **401** sem API key.

---

## 11. Limitações que reconheço

- A base de critérios é um **subconjunto ilustrativo** dos Beers 2023, não a
  tabela oficial completa (que é propriedade da AGS). Adicionar critérios é
  trivial e documentado.
- O modelo de ML usa **rótulo sintético**; não há, ainda, validação clínica
  prospectiva.
- A análise epidemiológica do relatório R/Quarto é **descritiva**, não causal.
- A autenticação por API Key é adequada para o escopo atual; produção real pediria
  OAuth2/OIDC.

Tudo isso está mapeado no `docs/roadmap.md` (v0.1 → v1.0).

---

## 12. Se eu tivesse mais tempo

Priorizaria, nesta ordem: (1) um *golden dataset* revisado por farmacêutico
clínico para medir concordância das regras; (2) integração **HL7 FHIR** para
ingerir prontuários reais anonimizados; (3) rótulo clínico real para o modelo de
ML; (4) explicabilidade por instância (SHAP) e OAuth2/OIDC. O sistema já foi
construído para receber essas evoluções sem reescrita do núcleo.
