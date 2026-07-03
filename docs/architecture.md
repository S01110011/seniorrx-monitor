# Arquitetura

## 1. Visao geral e contexto clinico

**SeniorRx Monitor** e uma plataforma que analisa o perfil farmacoterapeutico de
pacientes idosos (>=65 anos) para identificar:

1. **Polifarmacia/hiperpolifarmacia** (>=5 / >=10 medicamentos cronicos concomitantes);
2. **Medicamentos Potencialmente Inapropriados (PIM)** segundo os
   [AGS 2023 Updated Beers Criteria(R)](https://doi.org/10.1111/jgs.18372);
3. **Interacoes medicamento-medicamento** de alto risco (ex.: opioide + benzodiazepinico);
4. **Interacoes doenca-medicamento** (ex.: AINE em insuficiencia cardiaca);
5. **Necessidade de ajuste por funcao renal** (eGFR).

A saida e um **nivel de risco farmacoterapeutico** por paciente, com alertas
explicaveis (racional + recomendacao + fonte), consumido via API REST e
visualizado em um dashboard clinico.

> Uso exclusivo para pesquisa/educacao. Nao substitui julgamento clinico
> nem constitui dispositivo medico regulado.

## 2. Arquitetura em camadas (Clean/Hexagonal)

```
┌──────────────────────────────────────────────────────────────────┐
│ INTERFACE (interface/)                                            │
│   - api/          FastAPI: rotas HTTP, schemas Pydantic, auth      │
│   - dashboard/     Streamlit: visualizacao, consome a API          │
├──────────────────────────────────────────────────────────────────┤
│ APPLICATION (application/)                                         │
│   - services/     Orquestra motores de regra de dominio            │
│   - dto.py         Contratos de saida (nao vazam entidades internas)│
├──────────────────────────────────────────────────────────────────┤
│ DOMAIN (domain/)          <-- NUCLEO, sem dependencia de framework  │
│   - entities.py    Patient, Prescription, BeersCriterion, Alert...  │
│   - value_objects.py  Limiares clinicos (polifarmacia, eGFR, etc.)  │
│   - rules/         BeersRulesEngine, PolypharmacyRulesEngine,       │
│                     InteractionRulesEngine                          │
├──────────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE (infrastructure/)                                    │
│   - db/           SQLAlchemy models + repositories (traducao ORM<->domínio)│
│   - ml/           Feature engineering, RandomForest, treino via MLflow │
└──────────────────────────────────────────────────────────────────┘
```

**Regra de dependencia**: setas de import apontam sempre para dentro
(`interface -> application -> domain`; `infrastructure` implementa
interfaces consumidas pela `application`, mas o `domain` nunca importa
SQLAlchemy, FastAPI ou Streamlit). Isso permite testar 100% da logica
clinica (`domain/`) sem banco de dados nem HTTP — ver `tests/unit/`.

## 3. Fluxo de dados (input de prescricao -> relatorio)

```
[1] Prescricao eletronica / cadastro         [2] ETL (scripts/etl_pipeline.py)
    (CSV sintetico ou sistema de origem)  ─────────────▶  PostgreSQL normalizado
                                                            (patients, medications,
                                                             prescriptions, comorbidities)
                                                                    │
                                                                    ▼
[3] PatientRepository carrega Patient (dominio)      BeersCriteriaRepository
    com prescricoes/comorbidades ativas          carrega BeersCriterion[] (dominio)
                                                                    │
                                                                    ▼
[4] RiskScoringService.assess(patient)
      ├─ BeersRulesEngine        -> alertas de PIM
      ├─ InteractionRulesEngine  -> alertas de DDI / ajuste renal
      ├─ PolypharmacyRulesEngine -> alertas de poli/hiperpolifarmacia
      └─ (opcional) AdverseEventRiskModel.predict_proba -> sinal de ML complementar
                                                                    │
                                                                    ▼
[5] RiskAssessmentDTO (nivel de risco + lista de alertas explicaveis)
                                                                    │
                            ┌───────────────────────────────────────┤
                            ▼                                       ▼
[6a] API FastAPI                                      [6b] Relatorio R/Quarto
     GET /patients/{id}/risk-assessment                    (analise epidemiologica
     (JSON, consumido por sistemas externos)                agregada da coorte)
                            │
                            ▼
[7] Dashboard Streamlit — visualizacao interativa por paciente/farmaceutico clinico
```

## 4. Componentes de MLOps

- **MLflow**: tracking de experimentos e registry de modelos (`configs/mlops.md`).
- **DVC** (opcional): versionamento de `data/raw`/`data/processed` fora do git.
- **Evidently AI**: deteccao de drift semanal via GitHub Actions
  (`.github/workflows/model-monitoring.yml`).
- **Docker Compose**: `db` (Postgres) + `api` (FastAPI) + `dashboard` (Streamlit).

## 5. Seguranca (resumo — ver `SECURITY.md`)

- Sem PII no schema (pseudonimos, nao nomes/CPF).
- Segredos via `.env` / GitHub Secrets, nunca hardcoded.
- API Key stub -> substituir por OAuth2/OIDC em producao.
- HTTPS terminado no proxy reverso, nunca a API exposta em HTTP puro.

## 6. Decisões arquiteturais notáveis

| Decisão | Alternativa considerada | Motivo |
|---|---|---|
| Regras clinicas em Python puro (domain/), sem SQL embutido na logica | Regras 100% em SQL (views/stored procedures) | Testabilidade unitaria rapida, sem dependencia de banco; SQL usado apenas para persistencia/consulta |
| Dashboard consome a API (nao acessa o banco direto) | Streamlit lendo o banco diretamente | Unica fonte de verdade das regras de negocio; evita duplicar logica de risco no dashboard |
| RandomForest simples em vez de XGBoost/deep learning | Modelos mais complexos | Interpretabilidade priorizada sobre performance marginal em contexto clinico educacional |
| Rotulo de treino sintetico explicitamente marcado como proxy | Reivindicar rotulo "real" | Honestidade cientifica — ver `docs/clinical_validation.md` |
