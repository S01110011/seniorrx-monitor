# SeniorRx Monitor

🌐 [English](README.md) · **Português**

**Plataforma de detecção de Medicamentos Potencialmente Inapropriados (PIM) e
polifarmácia em idosos, baseada nos AGS Beers Criteria® 2023.**

[![CI](https://github.com/S01110011/seniorrx-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/S01110011/seniorrx-monitor/actions/workflows/ci.yml)
[![Model Monitoring](https://github.com/S01110011/seniorrx-monitor/actions/workflows/model-monitoring.yml/badge.svg)](https://github.com/S01110011/seniorrx-monitor/actions/workflows/model-monitoring.yml)
![coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-informational)
![security](https://img.shields.io/badge/security-bandit%20%7C%20pip--audit%20%7C%20gitleaks-orange)
![status](https://img.shields.io/badge/status-v0.1%20prot%C3%B3tipo-yellow)

> **Aviso:** projeto de pesquisa e educação. Usa exclusivamente dados
> sintéticos. Os alertas gerados **não substituem o julgamento clínico** nem
> constituem dispositivo médico regulado. Ver [`docs/clinical_validation.md`](docs/clinical_validation.md).

## O que este projeto faz

Idosos em polifarmácia (uso de múltiplos medicamentos) têm risco elevado de
reações adversas, muitas vezes evitáveis, porque já são conhecidas e
catalogadas pela literatura geriátrica. O **SeniorRx Monitor** implementa,
como software auditável e testado, um subconjunto ilustrativo dos
[AGS Beers Criteria® 2023](https://doi.org/10.1111/jgs.18372) para:

- detectar **polifarmácia** (≥ 5 medicamentos) e **hiperpolifarmácia** (≥ 10);
- sinalizar **PIM** (Medicamentos Potencialmente Inapropriados), independentes
  de diagnóstico ou condicionados a comorbidades específicas (por exemplo, AINE
  em insuficiência cardíaca);
- identificar **interações medicamento–medicamento** de alto risco (por exemplo,
  opioide + benzodiazepínico, varfarina + AINE, o *triple whammy*
  IECA/BRA + diurético + AINE);
- alertar sobre a necessidade de **ajuste pela função renal** (eGFR);
- consolidar tudo em um **nível de risco farmacoterapêutico** explicável,
  exposto via API REST e visualizado em um painel clínico.

Ver [`docs/beers_criteria.md`](docs/beers_criteria.md) para os conceitos-chave
(polifarmácia, PIM, metodologia Beers) e o aviso sobre a natureza ilustrativa
(não exaustiva) do conjunto de critérios implementado.

## Arquitetura

Arquitetura limpa (*clean architecture*) em quatro camadas — as regras clínicas
são 100% desacopladas do banco de dados e do framework web (ver
[`docs/architecture.md`](docs/architecture.md)):

```
interface/       FastAPI (API REST) + Streamlit (painel)
application/     serviços que orquestram os motores de regra
domain/          entidades + motores de regra (Beers, polifarmácia, interações) — núcleo puro
infrastructure/  SQLAlchemy (PostgreSQL) + modelo de ML (scikit-learn/MLflow)
```

## Pilha tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| API | FastAPI | Tipagem nativa (Pydantic), desempenho assíncrono, OpenAPI automático |
| Banco de dados | PostgreSQL | JSONB, UUID, *views*, maturidade em saúde |
| ORM | SQLAlchemy 2.x | Separação clara entre ORM e entidades de domínio |
| ML | scikit-learn + MLflow | Interpretabilidade priorizada; rastreamento de experimentos |
| Painel | Streamlit | Prototipagem rápida de interface clínica interativa |
| Análise reprodutível | R + Quarto | Relatórios epidemiológicos versionáveis e citáveis |
| Orquestração local | Docker Compose | `db` + `api` + `dashboard` com um comando |
| CI/CD | GitHub Actions | Lint, verificação de tipos, testes, build de imagem e checagem de *drift* |

## Início rápido

```bash
git clone https://github.com/S01110011/seniorrx-monitor.git
cd seniorrx-monitor

# Gera um .env com segredos FORTES e aleatórios (obrigatório: o compose falha sem eles)
make secrets          # ou: bash scripts/gen_secrets.sh

# Sobe PostgreSQL + API + painel
docker compose up --build

# Em outro terminal: inicializa o schema, gera dados sintéticos, roda o ETL e treina o modelo
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
bash scripts/run_pipeline.sh
```

Acesse:
- API: http://localhost:8000/docs (Swagger UI)
- Painel: http://localhost:8501

### Execução sem Docker

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
make typecheck     # mypy --strict
make test-unit     # pytest, sem exigir banco
make test          # pytest completo (inclui integração; requer TEST_DATABASE_URL)
make cov           # relatório HTML de cobertura
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
      "message": "PIM (Beers 2023): Glibenclamida — sulfonilureia de longa ação. ..."
    }
  ]
}
```

## Estrutura de pastas

```
seniorrx-monitor/
├── src/seniorrx/           # código-fonte (domain/application/infrastructure/interface)
├── sql/                    # schema.sql + seed dos critérios Beers 2023
├── scripts/                # geração de dados sintéticos, ETL, treino de ML, pipeline completo
├── tests/                  # unit/ (sem banco) + integration/ (requer PostgreSQL)
├── configs/                # settings.yaml, logging.yaml, notas de MLOps
├── data/                   # raw/ (CSV sintéticos) e processed/ (features, modelo) — não versionados
├── docs/                   # arquitetura, schema, critérios Beers, roadmap, validação, referências
├── references/             # resumo detalhado das fontes clínicas dos critérios implementados
├── reports/quarto/         # relatório epidemiológico reprodutível (R/Quarto)
├── notebooks/              # análise exploratória de dados (Jupyter)
└── .github/                # CI/CD, templates de issue/PR
```

A descrição completa de cada módulo está em [`docs/architecture.md`](docs/architecture.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Arquitetura em camadas, fluxo de dados, decisões técnicas |
| [`docs/DEEP_DIVE.md`](docs/DEEP_DIVE.md) | Análise técnica aprofundada de todo o sistema |
| [`docs/database_schema.md`](docs/database_schema.md) | Modelo relacional detalhado |
| [`docs/beers_criteria.md`](docs/beers_criteria.md) | Conceitos clínicos e aviso sobre o subconjunto implementado |
| [`docs/clinical_validation.md`](docs/clinical_validation.md) | Estratégia de validação científica (regras e ML) |
| [`docs/references.md`](docs/references.md) | Referências científicas completas |
| [`docs/roadmap.md`](docs/roadmap.md) | Milestones da v0.1 à v1.0 |
| [`docs/linkedin_pitch.md`](docs/linkedin_pitch.md) e [`docs/interview_talking_points.md`](docs/interview_talking_points.md) | Apresentação do projeto para portfólio |
| [`configs/mlops.md`](configs/mlops.md) | Estratégia de MLflow, DVC e Evidently AI |
| [`SECURITY.md`](SECURITY.md) e [`CONTRIBUTING.md`](CONTRIBUTING.md) | Segurança e como contribuir |

## Privacidade e conformidade

Nenhum dado real de paciente é usado ou armazenado. O schema não possui campos
de PII (nome, CPF, endereço); os pacientes são identificados por um pseudônimo
não reversível. Ver [`data/README.md`](data/README.md) e [`SECURITY.md`](SECURITY.md)
para a política completa (com referência à LGPD e ao GDPR).

## Licença

Código sob a [licença MIT](LICENSE). O conteúdo clínico dos AGS Beers Criteria®
é propriedade da American Geriatrics Society — este repositório implementa apenas
um subconjunto ilustrativo, com fins educacionais (ver
[`docs/beers_criteria.md`](docs/beers_criteria.md)).
