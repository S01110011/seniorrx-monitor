-- =============================================================================
-- SeniorRx Monitor — Esquema relacional (PostgreSQL 14+)
-- Plataforma de deteccao de Medicamentos Potencialmente Inapropriados (PIM)
-- em idosos, com base nos AGS Beers Criteria (r) 2023.
--
-- IMPORTANTE (privacidade / LGPD-GDPR):
--   Este esquema NAO armazena PII (nome, CPF, endereco, telefone, prontuario).
--   Pacientes sao identificados apenas por UUID interno. Todo dado de
--   demonstracao neste repositorio e SINTETICO (ver scripts/generate_synthetic_data.py).
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. PACIENTES (dados demograficos minimos, sem PII)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pseudonym           VARCHAR(32) NOT NULL UNIQUE,      -- identificador externo nao reversivel (ex: hash)
    birth_year          SMALLINT NOT NULL CHECK (birth_year BETWEEN 1900 AND 2100),
    sex                 CHAR(1) NOT NULL CHECK (sex IN ('M', 'F', 'O')),
    weight_kg           NUMERIC(5,2) CHECK (weight_kg > 0),
    height_cm           NUMERIC(5,2) CHECK (height_cm > 0),
    serum_creatinine_mg_dl NUMERIC(4,2) CHECK (serum_creatinine_mg_dl > 0),
    egfr_ml_min_1_73m2  NUMERIC(5,1),                     -- eGFR (CKD-EPI), usado nas regras dose-renal
    care_setting        VARCHAR(32) NOT NULL DEFAULT 'ambulatorial'
                        CHECK (care_setting IN ('ambulatorial', 'hospitalar', 'ilpi', 'domiciliar')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE patients IS 'Cadastro minimo de pacientes idosos (>=65a), sem PII. Idade calculada a partir de birth_year.';

-- -----------------------------------------------------------------------------
-- 2. COMORBIDADES (para regras de interacao doenca-medicamento)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS comorbidities (
    comorbidity_id      BIGSERIAL PRIMARY KEY,
    patient_id          UUID NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    icd10_code          VARCHAR(10) NOT NULL,
    description         VARCHAR(255) NOT NULL,
    diagnosed_on        DATE,
    active               BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_comorbidities_patient ON comorbidities(patient_id);
CREATE INDEX IF NOT EXISTS idx_comorbidities_icd10 ON comorbidities(icd10_code);

-- -----------------------------------------------------------------------------
-- 3. MEDICAMENTOS (catalogo mestre, codificado por ATC)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medications (
    medication_id       BIGSERIAL PRIMARY KEY,
    drug_name           VARCHAR(150) NOT NULL,
    atc_code            VARCHAR(10) NOT NULL,           -- codigo ATC (OMS)
    drug_class          VARCHAR(120) NOT NULL,
    route               VARCHAR(30) NOT NULL DEFAULT 'oral',
    is_high_alert       BOOLEAN NOT NULL DEFAULT FALSE,  -- classe de alta vigilancia (ISMP)
    UNIQUE (drug_name, route)
);

CREATE INDEX IF NOT EXISTS idx_medications_atc ON medications(atc_code);
CREATE INDEX IF NOT EXISTS idx_medications_class ON medications(drug_class);

-- -----------------------------------------------------------------------------
-- 4. CRITERIOS BEERS 2023 (subconjunto ilustrativo — ver docs/beers_criteria.md)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS beers_pim_criteria (
    criterion_id        BIGSERIAL PRIMARY KEY,
    criteria_type        VARCHAR(40) NOT NULL CHECK (criteria_type IN (
                             'PIM_INDEPENDENTE_DIAGNOSTICO',
                             'PIM_CONDICAO_ESPECIFICA',
                             'USAR_COM_CAUTELA',
                             'INTERACAO_MEDICAMENTO_MEDICAMENTO',
                             'AJUSTE_FUNCAO_RENAL'
                         )),
    drug_or_class        VARCHAR(150) NOT NULL,
    atc_pattern           VARCHAR(10),                    -- prefixo ATC para casar via LIKE 'prefixo%'
    organ_system          VARCHAR(80),
    rationale             TEXT NOT NULL,
    recommendation         TEXT NOT NULL,
    related_condition_icd10 VARCHAR(10),                  -- usado quando criteria_type = PIM_CONDICAO_ESPECIFICA
    interacting_atc_pattern VARCHAR(10),                   -- usado quando criteria_type = INTERACAO_MEDICAMENTO_MEDICAMENTO
    egfr_threshold_ml_min   NUMERIC(5,1),                  -- usado quando criteria_type = AJUSTE_FUNCAO_RENAL
    quality_of_evidence     VARCHAR(10) CHECK (quality_of_evidence IN ('Alta', 'Moderada', 'Baixa')),
    strength_of_recommendation VARCHAR(10) CHECK (strength_of_recommendation IN ('Forte', 'Fraca')),
    severity_default        VARCHAR(10) NOT NULL DEFAULT 'MODERADA'
                            CHECK (severity_default IN ('BAIXA', 'MODERADA', 'ALTA', 'CRITICA')),
    source_reference        VARCHAR(255) NOT NULL DEFAULT
                            'American Geriatrics Society 2023 Updated AGS Beers Criteria(R). J Am Geriatr Soc. 2023;71(7):2052-2081.',
    -- Chave natural que torna o seed idempotente (ON CONFLICT): re-executar o
    -- bootstrap (ex.: cada `docker compose up`) nao duplica criterios.
    UNIQUE (criteria_type, drug_or_class)
);

CREATE INDEX IF NOT EXISTS idx_beers_atc_pattern ON beers_pim_criteria(atc_pattern);
CREATE INDEX IF NOT EXISTS idx_beers_type ON beers_pim_criteria(criteria_type);

COMMENT ON TABLE beers_pim_criteria IS
  'Subconjunto ILUSTRATIVO e EDUCACIONAL dos criterios AGS Beers 2023. '
  'Para uso clinico real, adquirir a tabela completa e licenciada junto a American Geriatrics Society / Wiley.';

-- -----------------------------------------------------------------------------
-- 5. PRESCRICOES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id            UUID NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    medication_id          BIGINT NOT NULL REFERENCES medications(medication_id),
    prescriber_pseudonym    VARCHAR(32) NOT NULL,          -- CRM/identificador nao reversivel
    dose_value              NUMERIC(8,2),
    dose_unit                VARCHAR(20),
    frequency_per_day         NUMERIC(4,1),
    route                     VARCHAR(30),
    indication_icd10           VARCHAR(10),
    start_date                 DATE NOT NULL,
    end_date                   DATE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
    -- Nota: "prescricao ativa" (end_date NULL ou futuro) NAO e materializada como
    -- coluna gerada porque a expressao depende de CURRENT_DATE, que o PostgreSQL
    -- rejeita em GENERATED colunas (exige expressao imutavel). O estado ativo e
    -- calculado em tempo de consulta pela view v_active_prescriptions e, na camada
    -- de dominio, pela propriedade Prescription.is_active.
);

CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_medication ON prescriptions(medication_id);
-- Predicado imutavel (end_date IS NULL): acelera a busca das prescricoes
-- cronicas em aberto, o caso mais comum de "ativa".
CREATE INDEX IF NOT EXISTS idx_prescriptions_open ON prescriptions(patient_id) WHERE end_date IS NULL;

-- -----------------------------------------------------------------------------
-- 6. ALERTAS (saida do motor de regras Beers / polifarmacia / interacoes)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    alert_id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id              UUID NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    prescription_id           UUID REFERENCES prescriptions(prescription_id) ON DELETE CASCADE,
    criterion_id               BIGINT REFERENCES beers_pim_criteria(criterion_id),
    alert_type                  VARCHAR(30) NOT NULL CHECK (alert_type IN (
                                    'PIM_BEERS', 'POLIFARMACIA', 'HIPERPOLIFARMACIA',
                                    'INTERACAO_MEDICAMENTOSA', 'INTERACAO_DOENCA_MEDICAMENTO',
                                    'AJUSTE_RENAL'
                                )),
    severity                     VARCHAR(10) NOT NULL CHECK (severity IN ('BAIXA', 'MODERADA', 'ALTA', 'CRITICA')),
    message                       TEXT NOT NULL,
    status                        VARCHAR(20) NOT NULL DEFAULT 'ABERTO'
                                  CHECK (status IN ('ABERTO', 'RECONHECIDO', 'SUBSTITUIDO', 'DESCARTADO_JUSTIFICADO')),
    reviewed_by_pseudonym           VARCHAR(32),
    reviewed_at                      TIMESTAMPTZ,
    generated_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alerts_patient ON alerts(patient_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_type_severity ON alerts(alert_type, severity);

-- -----------------------------------------------------------------------------
-- 7. RISCO FARMACOTERAPEUTICO (saida agregada por paciente / execucao)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_scores (
    score_id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id                UUID NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    calculated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    active_medication_count       SMALLINT NOT NULL,
    pim_count                       SMALLINT NOT NULL,
    ddi_count                        SMALLINT NOT NULL,
    comorbidity_count                 SMALLINT NOT NULL,
    rule_based_risk_level               VARCHAR(10) NOT NULL CHECK (rule_based_risk_level IN ('BAIXO', 'MODERADO', 'ALTO', 'CRITICO')),
    ml_adverse_event_probability          NUMERIC(5,4) CHECK (ml_adverse_event_probability BETWEEN 0 AND 1),
    model_version                           VARCHAR(40),
    explanation                              JSONB          -- fatores contribuintes (SHAP-like, para explicabilidade)
);

CREATE INDEX IF NOT EXISTS idx_risk_scores_patient ON risk_scores(patient_id, calculated_at DESC);

-- -----------------------------------------------------------------------------
-- View de conveniencia: prescricoes ativas com dados do medicamento
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_active_prescriptions AS
SELECT
    p.prescription_id,
    p.patient_id,
    m.medication_id,
    m.drug_name,
    m.atc_code,
    m.drug_class,
    p.dose_value,
    p.dose_unit,
    p.frequency_per_day,
    p.indication_icd10,
    p.start_date
FROM prescriptions p
JOIN medications m ON m.medication_id = p.medication_id
WHERE p.end_date IS NULL OR p.end_date >= CURRENT_DATE;
