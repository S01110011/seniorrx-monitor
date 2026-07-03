# Modelagem de Banco de Dados

Fonte de verdade: [`sql/schema.sql`](../sql/schema.sql). Este documento descreve
o modelo conceitual; para DDL completo (constraints, indices), ver o arquivo SQL.

## Diagrama entidade-relacionamento (textual)

```
patients (1) ───< comorbidities
patients (1) ───< prescriptions >─── (1) medications
patients (1) ───< alerts >─── (0..1) prescriptions
alerts   (0..1) >─── beers_pim_criteria
patients (1) ───< risk_scores
```

## Tabelas

### `patients`
Cadastro minimo, **sem PII**. `pseudonym` e um identificador nao reversivel
(ex.: hash) usado para correlacionar com sistemas externos sem expor identidade.
`egfr_ml_min_1_73m2` e a taxa de filtracao glomerular estimada (CKD-EPI),
usada pelas regras de ajuste renal.

### `comorbidities`
Diagnosticos ativos (ICD-10) usados pelas regras de interacao doenca-medicamento
(ex.: `I50` insuficiencia cardiaca habilita o criterio de AINE contraindicado).

### `medications`
Catalogo mestre codificado por **ATC** (Anatomical Therapeutic Chemical, OMS).
O casamento com `beers_pim_criteria` e feito por prefixo de ATC (`atc_pattern`),
permitindo que um criterio cubra uma classe inteira (ex.: `N05BA` = todos os
benzodiazepinicos) ou uma molecula especifica (ex.: `A10BB01` = glibenclamida).

### `beers_pim_criteria`
Tabela central do motor de regras. Cada linha e um criterio com:
- `criteria_type`: como o criterio deve ser avaliado (independente de diagnostico,
  condicao especifica, interacao medicamento-medicamento, ajuste renal);
- `atc_pattern` / `interacting_atc_pattern`: chaves de casamento;
- `related_condition_icd10`: usado quando o criterio depende de comorbidade;
- `egfr_threshold_ml_min`: usado quando o criterio depende de funcao renal;
- `rationale`, `recommendation`, `source_reference`: texto explicativo exibido no alerta.

Ver [`docs/beers_criteria.md`](beers_criteria.md) para o disclaimer sobre a
natureza ilustrativa deste subconjunto.

### `prescriptions`
Uma linha por medicamento prescrito. O estado "ativa" (`end_date IS NULL OR
end_date >= CURRENT_DATE`) e calculado em tempo de consulta pela view
`v_active_prescriptions` e, na camada de dominio, pela propriedade
`Prescription.is_active` — deliberadamente NAO materializado como coluna
gerada, pois o PostgreSQL exige expressao imutavel em `GENERATED` colunas e
`CURRENT_DATE` nao e imutavel. `duration_days` (calculado em
`domain.entities.Prescription`) e usado pelas regras de uso cronico
(IBP > 8 semanas, metoclopramida > 12 semanas).

### `alerts`
Saida persistida do motor de regras — permite auditoria (quem revisou, quando,
status: aberto/reconhecido/substituido/descartado com justificativa).

### `risk_scores`
Snapshot agregado por execucao de avaliacao: contagens (PIM, DDI, comorbidades),
nivel de risco baseado em regras e, opcionalmente, a probabilidade do modelo de ML
com `model_version` para rastreabilidade (qual modelo gerou qual score).

## Por que PostgreSQL

- **JSONB** (`risk_scores.explanation`) para armazenar explicabilidade
  semi-estruturada sem tabela adicional;
- **Extensao `uuid-ossp`** para chaves primarias UUID (evita vazamento de
  volume/sequencia que IDs seriais exporiam);
- **Views** (`v_active_prescriptions`) centralizam a logica de "prescricao
  ativa" avaliada em tempo de consulta, mantendo-a consistente sem trigger;
- Maturidade em ambientes de saude (HIPAA/LGPD compliance tooling, RLS
  para multi-tenancy futura).
