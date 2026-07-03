# SeniorRx Monitor

**Plataforma de deteccao de Medicamentos Potencialmente Inapropriados (PIM) e
polifarmacia em idosos, baseada nos AGS Beers Criteria(R) 2023.**

![build](https://img.shields.io/badge/build-passing-brightgreen)
![coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-informational)
![status](https://img.shields.io/badge/status-v0.1%20prototipo-yellow)

> **Aviso:** projeto de pesquisa/educacao. Usa exclusivamente dados
> sinteticos. Os alertas gerados **nao substituem julgamento clinico** nem
> constituem dispositivo medico regulado. Ver [`docs/clinical_validation.md`](docs/clinical_validation.md).

## O que este projeto faz

Idosos com polifarmacia (uso de multiplos medicamentos) tem risco elevado de
reacoes adversas, muitas vezes evitaveis porque ja sao conhecidas e
catalogadas pela literatura geriatrica. O **SeniorRx Monitor** implementa,
como software auditavel e testado, um subconjunto ilustrativo dos
[AGS Beers Criteria(R) 2023](https://doi.org/10.1111/jgs.18372) para:

- Detectar **polifarmacia** (>=5 medicamentos) e **hiperpolifarmacia** (>=10);
- Sinalizar **PIM** (Medicamentos Potencialmente Inapropriados), independentes
  de diagnostico ou condicionados a comorbidades especificas (ex.: AINE em
  insuficiencia cardiaca);
- Identificar **interacoes medicamento-medicamento** de alto risco (ex.:
  opioide + benzodiazepinico, varfarina + AINE, "triple whammy" IECA+diuretico+AINE);
- Alertar sobre necessidade de **ajuste por funcao renal** (eGFR);
- Consolidar tudo em um **nivel de risco farmacoterapeutico** explicavel,
  exposto via API REST e visualizado em dashboard clinico.

Ver [`docs/beers_criteria.md`](docs/beers_criteria.md) para conceitos-chave
(polifarmacia, PIM, metodologia Beers) e o disclaimer sobre a natureza
ilustrativa (nao exaustiva) do conjunto de criterios implementado.

## Arquitetura

Clean Architecture em 4 camadas — regras clinicas 100% desacopladas de
banco de dados e framework web (ver [`docs/architecture.md`](docs/architecture.md)):

```
interface/       FastAPI (API REST) + Streamlit (dashboard)
application/     Servicos que orquestram os motores de regra
domain/          Entidades + motores de regra (Beers, polifarmacia, interacoes) — nucleo puro
infrastructure/  SQLAlchemy (PostgreSQL) + modelo de ML (scikit-learn/MLflow)
```

## Stack tecnologico

| Camada | Tecnologia | Por que |
|---|---|---|
| API | FastAPI | Tipagem nativa (Pydantic), performance assincrona, OpenAPI automatico |
| Banco | PostgreSQL | JSONB, UUID, colunas geradas, maturidade em saude |
| ORM | SQLAlchemy 2.x | Separacao clara ORM <-> entidades de dominio |
| ML | scikit-learn + MLflow | Interpretabilidade priorizada; tracking de experimentos |
| Dashboard | Streamlit | Prototipagem rapida de UI clinica interativa |
| Analise reprodutivel | R + Quarto | Relatorios epidemiologicos versionaveis e citaveis |
| Orquestracao local | Docker Compose | `db` + `api` + `dashboard` com um comando |
| CI/CD | GitHub Actions | Lint, typecheck, testes, build de imagem, drift semanal |

## Quickstart

```bash
git clone <repo-url> seniorrx-monitor
cd seniorrx-monitor
cp .env.example .env

# Sobe Postgres + API + Dashboard
docker compose up --build

# Em outro terminal: inicializa schema, gera dados sinteticos, roda ETL e treina o modelo
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
bash scripts/run_pipeline.sh
```

Acesse:
- API: http://localhost:8000/docs (Swagger UI)
- Dashboard: http://localhost:8501

### Rodando sem Docker

```bash
pip install -e ".[dev]"
python scripts/init_db.py --database-url "$DATABASE_URL"
python scripts/generate_synthetic_data.py --n-patients 500
python scripts/etl_pipeline.py
uvicorn seniorrx.interface.api.main:app --reload &
streamlit run src/seniorrx/interface/dashboard/streamlit_app.py
```

### Testes

```bash
make lint          # ruff
make typecheck      # mypy --strict
make test-unit       # pytest, sem exigir banco
make test            # pytest completo (inclui integration, requer TEST_DATABASE_URL)
make cov              # relatorio HTML de cobertura
```

## Exemplo de uso da API

```bash
curl -H "X-API-Key: $SENIORRX_API_KEY" \
  http://localhost:8000/patients/<patient_id>/risk-assessment
```

```json
{
  "patient_id": "3f5a...",
  "active_medication_count": 7,
  "pim_count": 2,
  "ddi_count": 1,
  "comorbidity_count": 3,
  "rule_based_risk_level": "ALTO",
  "alerts": [
    {
      "alert_type": "PIM_BEERS",
      "severity": "ALTA",
      "message": "PIM (Beers 2023): Glibenclamida — Sulfonilureia de longa acao. ..."
    }
  ]
}
```

## Estrutura de pastas

```
seniorrx-monitor/
├── src/seniorrx/           # codigo-fonte (domain/application/infrastructure/interface)
├── sql/                    # schema.sql + seed dos criterios Beers 2023
├── scripts/                # geracao de dados sinteticos, ETL, treino de ML, pipeline completo
├── tests/                  # unit/ (sem banco) + integration/ (requer Postgres)
├── configs/                # settings.yaml, logging.yaml, notas de MLOps
├── data/                   # raw/ (CSV sinteticos) e processed/ (features, modelo) — nao versionados
├── docs/                   # arquitetura, schema, criterios Beers, roadmap, validacao, referencias
├── references/             # resumo detalhado das fontes clinicas dos criterios implementados
├── reports/quarto/          # relatorio epidemiologico reprodutivel (R/Quarto)
├── notebooks/                # EDA exploratoria (Jupyter)
└── .github/                  # CI/CD, templates de issue/PR
```

Descricao completa de cada modulo em [`docs/architecture.md`](docs/architecture.md).

## Documentacao

| Documento | Conteudo |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Arquitetura em camadas, fluxo de dados, decisoes tecnicas |
| [`docs/database_schema.md`](docs/database_schema.md) | Modelo relacional detalhado |
| [`docs/beers_criteria.md`](docs/beers_criteria.md) | Conceitos clinicos + disclaimer sobre o subconjunto implementado |
| [`docs/clinical_validation.md`](docs/clinical_validation.md) | Estrategia de validacao cientifica (regras + ML) |
| [`docs/references.md`](docs/references.md) | Referencias cientificas completas |
| [`docs/roadmap.md`](docs/roadmap.md) | Milestones v0.1 -> v1.0 |
| [`docs/initial_issues.md`](docs/initial_issues.md) | Issues iniciais sugeridas + mensagens de commit |
| [`docs/linkedin_pitch.md`](docs/linkedin_pitch.md) / [`docs/interview_talking_points.md`](docs/interview_talking_points.md) | Apresentacao do projeto para portfolio |
| [`configs/mlops.md`](configs/mlops.md) | Estrategia de MLflow, DVC, Evidently AI |
| [`SECURITY.md`](SECURITY.md) / [`CONTRIBUTING.md`](CONTRIBUTING.md) | Seguranca e como contribuir |

## Privacidade e conformidade

Nenhum dado real de paciente e usado ou armazenado. O schema nao possui
campos de PII (nome, CPF, endereco); pacientes sao identificados por
pseudonimo nao reversivel. Ver [`data/README.md`](data/README.md) e
[`SECURITY.md`](SECURITY.md) para a politica completa (referenciando LGPD/GDPR).

## Licenca

Codigo sob [MIT License](LICENSE). O conteudo clinico dos AGS Beers
Criteria(R) e propriedade da American Geriatrics Society — este repositorio
implementa apenas um subconjunto ilustrativo com fins educacionais (ver
[`docs/beers_criteria.md`](docs/beers_criteria.md)).
