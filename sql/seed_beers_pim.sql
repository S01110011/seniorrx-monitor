-- =============================================================================
-- Seed: subconjunto ILUSTRATIVO dos criterios AGS Beers 2023 e catalogo de
-- medicamentos associado. NAO EXAUSTIVO — ver docs/beers_criteria.md para
-- disclaimer completo e referencia oficial (AGS 2023 Beers Criteria(R), JAGS).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Catalogo de medicamentos (subconjunto usado nos exemplos e dados sinteticos)
-- -----------------------------------------------------------------------------
INSERT INTO medications (drug_name, atc_code, drug_class, route, is_high_alert) VALUES
    ('Amitriptilina',      'N06AA09', 'Antidepressivo triciclico',                 'oral', FALSE),
    ('Clomipramina',       'N06AA04', 'Antidepressivo triciclico',                 'oral', FALSE),
    ('Diazepam',           'N05BA01', 'Benzodiazepinico (longa acao)',             'oral', TRUE),
    ('Clonazepam',         'N03AE01', 'Benzodiazepinico (longa acao)',             'oral', TRUE),
    ('Lorazepam',          'N05BA06', 'Benzodiazepinico (curta/media acao)',       'oral', TRUE),
    ('Zolpidem',           'N05CF02', 'Hipnotico Z-drug',                          'oral', TRUE),
    ('Difenidramina',      'R06AA02', 'Anti-histaminico 1a geracao',               'oral', FALSE),
    ('Hidroxizina',        'N05BB01', 'Anti-histaminico 1a geracao',               'oral', FALSE),
    ('Ciclobenzaprina',    'M03BX08', 'Relaxante muscular esqueletico',            'oral', FALSE),
    ('Carisoprodol',       'M03BA02', 'Relaxante muscular esqueletico',            'oral', FALSE),
    ('Glibenclamida',      'A10BB01', 'Sulfonilureia de longa acao',               'oral', TRUE),
    ('Gliclazida',         'A10BB09', 'Sulfonilureia',                             'oral', TRUE),
    ('Metformina',         'A10BA02', 'Biguanida',                                 'oral', FALSE),
    ('Nifedipino (acao curta)', 'C08CA05', 'Bloqueador de canal de calcio',        'oral', FALSE),
    ('Digoxina',           'C01AA05', 'Glicosideo digitalico',                     'oral', TRUE),
    ('Doxazosina',         'C02CA04', 'Alfa-bloqueador',                          'oral', FALSE),
    ('Metoclopramida',     'A03FA01', 'Procinetico / antiemetico',                 'oral', FALSE),
    ('Ibuprofeno',         'M01AE01', 'AINE nao seletivo',                         'oral', FALSE),
    ('Naproxeno',          'M01AE02', 'AINE nao seletivo',                         'oral', FALSE),
    ('Diclofenaco',        'M01AB05', 'AINE nao seletivo',                         'oral', FALSE),
    ('Omeprazol',          'A02BC01', 'Inibidor de bomba de protons',              'oral', FALSE),
    ('Varfarina',          'B01AA03', 'Anticoagulante antagonista de vitamina K',  'oral', TRUE),
    ('Meperidina (Petidina)', 'N02AB02', 'Opioide',                                'oral', TRUE),
    ('Tramadol',           'N02AX02', 'Opioide',                                   'oral', TRUE),
    ('Sertralina',         'N06AB06', 'Inibidor seletivo de recaptacao de serotonina', 'oral', FALSE),
    ('Losartana',          'C09CA01', 'Bloqueador do receptor de angiotensina II', 'oral', FALSE),
    ('Enalapril',          'C09AA02', 'Inibidor da ECA',                          'oral', FALSE),
    ('Espironolactona',    'C03DA01', 'Diuretico poupador de potassio',            'oral', FALSE),
    ('Haloperidol',        'N05AD01', 'Antipsicotico tipico',                      'oral', FALSE),
    ('Risperidona',        'N05AX08', 'Antipsicotico atipico',                     'oral', FALSE),
    ('Insulina regular (escala movel isolada)', 'A10AB01', 'Insulina',             'subcutanea', TRUE)
ON CONFLICT (drug_name, route) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Criterios Beers 2023 — PIM independentes de diagnostico
-- -----------------------------------------------------------------------------
INSERT INTO beers_pim_criteria
    (criteria_type, drug_or_class, atc_pattern, organ_system, rationale, recommendation,
     quality_of_evidence, strength_of_recommendation, severity_default)
VALUES
('PIM_INDEPENDENTE_DIAGNOSTICO', 'Antidepressivos triciclicos (amitriptilina, clomipramina)', 'N06AA',
 'Sistema Nervoso Central / Anticolinergico',
 'Alta potencia anticolinergica: sedacao, hipotensao ortostatica, risco de quedas e confusao. Eficacia reduzida vs. alternativas mais seguras.',
 'Evitar. Preferir ISRS ou outras classes com menor carga anticolinergica quando clinicamente apropriado.',
 'Alta', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Benzodiazepinicos (todos, independente da duracao de acao)', 'N05BA',
 'Sistema Nervoso Central',
 'Aumento do risco de comprometimento cognitivo, delirium, quedas, fraturas e acidentes automobilisticos em idosos; metabolismo reduzido.',
 'Evitar para insonia, agitacao ou delirium. Considerar apenas em transtorno de ansiedade generalizada refratario, convulsoes ou abstinencia alcoolica, com reavaliacao periodica.',
 'Alta', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Benzodiazepinicos de longa acao (diazepam, clonazepam)', 'N05BA01',
 'Sistema Nervoso Central',
 'Meia-vida prolongada aumenta acumulo e sedacao diurna em idosos.',
 'Evitar; se necessario, preferir agentes de meia-vida curta e menor dose eficaz.',
 'Alta', 'Forte', 'CRITICA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Hipnoticos Z-drugs (zolpidem, zopiclona, zaleplon)', 'N05CF',
 'Sistema Nervoso Central',
 'Eventos adversos similares aos benzodiazepinicos (quedas, fraturas, acidentes), com beneficio minimo sobre latencia/duracao do sono em idosos.',
 'Evitar uso cronico (>90 dias). Priorizar higiene do sono e terapia cognitivo-comportamental para insonia.',
 'Moderada', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Anti-histaminicos de 1a geracao (difenidramina, hidroxizina)', 'R06AA',
 'Anticolinergico',
 'Clearance reduzido com o envelhecimento; risco de confusao, boca seca, constipacao, retencao urinaria.',
 'Evitar, especialmente como hipnotico ou para reacoes alergicas de rotina.',
 'Moderada', 'Forte', 'MODERADA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Relaxantes musculares esqueleticos (ciclobenzaprina, carisoprodol)', 'M03B',
 'Sistema Nervoso Central / Anticolinergico',
 'Mal tolerados por idosos devido a efeitos anticolinergicos, sedacao e fraqueza; eficacia questionavel nas doses toleradas.',
 'Evitar.',
 'Moderada', 'Forte', 'MODERADA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Glibenclamida (sulfonilureia de longa acao)', 'A10BB01',
 'Endocrino / Metabolico',
 'Hipoglicemia prolongada e grave em comparacao a sulfonilureias de acao mais curta.',
 'Evitar. Preferir sulfonilureias de acao curta ou outras classes com menor risco de hipoglicemia.',
 'Alta', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Nifedipino de acao curta', 'C08CA05',
 'Cardiovascular',
 'Risco de hipotensao e isquemia miocardica por vasodilatacao rapida e reflexo simpatico.',
 'Evitar; preferir formulacoes de liberacao prolongada quando bloqueador de canal de calcio for necessario.',
 'Moderada', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Digoxina em dose > 0.125 mg/dia (uso cronico)', 'C01AA05',
 'Cardiovascular',
 'Clearance renal reduzido em idosos aumenta risco de toxicidade (nauseas, arritmias, confusao) mesmo com niveis "terapeuticos".',
 'Evitar como primeira linha para fibrilacao atrial ou insuficiencia cardiaca; se usado, limitar a <=0.125 mg/dia e monitorar funcao renal.',
 'Moderada', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Alfa-1 bloqueadores como monoterapia para hipertensao (doxazosina)', 'C02CA04',
 'Cardiovascular',
 'Alto risco de hipotensao ortostatica e quedas quando usado como agente anti-hipertensivo isolado.',
 'Evitar como monoterapia de hipertensao; considerar apenas em contexto de hiperplasia prostatica benigna, com cautela.',
 'Moderada', 'Forte', 'MODERADA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Metoclopramida (uso > 12 semanas)', 'A03FA01',
 'Neurologico',
 'Risco de sintomas extrapiramidais e discinesia tardia aumenta com duracao de uso e fragilidade.',
 'Evitar uso continuo por mais de 12 semanas, exceto em gastroparesia refrataria.',
 'Moderada', 'Forte', 'MODERADA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Inibidores de bomba de protons (uso continuo > 8 semanas sem indicacao)', 'A02BC',
 'Gastrointestinal',
 'Uso prolongado sem indicacao associado a risco aumentado de fratura, deficiencia de B12/magnesio e infeccao por C. difficile.',
 'Evitar uso continuo acima de 8 semanas, salvo indicacoes de alto risco (ex: Barrett, sangramento GI, uso cronico de AINE/corticoide).',
 'Moderada', 'Forte', 'BAIXA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'AINEs nao seletivos, uso cronico oral (ibuprofeno, naproxeno, diclofenaco)', 'M01A',
 'Gastrointestinal / Renal / Cardiovascular',
 'Risco aumentado de sangramento gastrointestinal, lesao renal aguda e eventos cardiovasculares com uso continuo em idosos.',
 'Evitar uso cronico; se necessario uso agudo, associar gastroprotecao e monitorar funcao renal.',
 'Moderada', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Meperidina (petidina)', 'N02AB02',
 'Sistema Nervoso Central',
 'Metabolito neurotoxico (normeperidina) acumula-se em insuficiencia renal, aumentando risco de convulsoes e delirium; analgesia inferior a alternativas.',
 'Evitar.',
 'Alta', 'Forte', 'ALTA'),

('PIM_INDEPENDENTE_DIAGNOSTICO', 'Insulina em escala movel isolada (sem esquema basal)', 'A10AB01',
 'Endocrino / Metabolico',
 'Maior risco de hipoglicemia e hiperglicemia sem melhora de controle glicemico comparado a esquema basal-bolus.',
 'Evitar como estrategia isolada de manejo glicemico em idosos.',
 'Moderada', 'Forte', 'MODERADA')
ON CONFLICT (criteria_type, drug_or_class) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Criterios Beers 2023 — condicao especifica (interacao doenca-medicamento)
-- -----------------------------------------------------------------------------
INSERT INTO beers_pim_criteria
    (criteria_type, drug_or_class, atc_pattern, organ_system, rationale, recommendation,
     related_condition_icd10, quality_of_evidence, strength_of_recommendation, severity_default)
VALUES
('PIM_CONDICAO_ESPECIFICA', 'AINEs em pacientes com Insuficiencia Cardiaca', 'M01A',
 'Cardiovascular',
 'Retencao hidrossalina e efeito pro-natremico podem precipitar descompensacao de IC.',
 'Evitar em pacientes com diagnostico ativo de insuficiencia cardiaca (ICD-10 I50%).',
 'I50', 'Moderada', 'Forte', 'ALTA'),

('PIM_CONDICAO_ESPECIFICA', 'Antipsicoticos em pacientes com demencia (sintomas comportamentais)', 'N05A',
 'Neurologico',
 'Aumento do risco de AVC e mortalidade em pacientes idosos com demencia (alerta de tarja preta da FDA).',
 'Evitar, exceto quando medidas nao farmacologicas falharam e ha risco de dano ao paciente ou terceiros; usar menor dose/tempo possivel.',
 'F03', 'Alta', 'Forte', 'CRITICA'),

('PIM_CONDICAO_ESPECIFICA', 'Anticolinergicos em pacientes com demencia ou comprometimento cognitivo', 'N06AA',
 'Neurologico',
 'Piora do desempenho cognitivo e risco de delirium sobreposto.',
 'Evitar em pacientes com diagnostico de demencia ou comprometimento cognitivo leve (ICD-10 F00-F03, G30, G31).',
 'F00', 'Moderada', 'Forte', 'ALTA'),

('PIM_CONDICAO_ESPECIFICA', 'Benzodiazepinicos em pacientes com historico de quedas ou fraturas', 'N05BA',
 'Sistema Nervoso Central',
 'Efeito sedativo e prejuizo psicomotor aumentam substancialmente o risco de novas quedas.',
 'Evitar em pacientes com historico de queda ou fratura nos ultimos 12 meses (ICD-10 R29.6, W19, S72%).',
 'R29.6', 'Alta', 'Forte', 'CRITICA'),

('PIM_CONDICAO_ESPECIFICA', 'AINEs em Doenca Renal Cronica estagio >=3 (eGFR < 60)', 'M01A',
 'Renal',
 'Reducao adicional da perfusao renal em pacientes com reserva funcional ja diminuida.',
 'Evitar em pacientes com DRC estagio 3b-5 (ICD-10 N18.3-N18.5); considerar analgesia alternativa.',
 'N18', 'Moderada', 'Forte', 'ALTA')
ON CONFLICT (criteria_type, drug_or_class) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Criterios Beers 2023 — interacao medicamento-medicamento
-- -----------------------------------------------------------------------------
INSERT INTO beers_pim_criteria
    (criteria_type, drug_or_class, atc_pattern, organ_system, rationale, recommendation,
     interacting_atc_pattern, quality_of_evidence, strength_of_recommendation, severity_default)
VALUES
('INTERACAO_MEDICAMENTO_MEDICAMENTO', 'Opioides + Benzodiazepinicos', 'N02A',
 'Sistema Nervoso Central / Respiratorio',
 'Efeito sinergico de depressao do SNC e respiratoria; risco aumentado de overdose fatal.',
 'Evitar a combinacao; se inevitavel, usar menores doses eficazes com monitoramento estreito.',
 'N05BA', 'Alta', 'Forte', 'CRITICA'),

('INTERACAO_MEDICAMENTO_MEDICAMENTO', 'Varfarina + AINEs', 'B01AA03',
 'Hematologico / Gastrointestinal',
 'Efeito antiplaquetario e gastroirritante do AINE somado ao efeito anticoagulante aumenta risco de sangramento grave.',
 'Evitar a combinacao; se necessario, usar gastroprotecao e monitorar INR/sinais de sangramento.',
 'M01A', 'Alta', 'Forte', 'CRITICA'),

('INTERACAO_MEDICAMENTO_MEDICAMENTO', '"Triple whammy": IECA/BRA + Diuretico + AINE', 'C09',
 'Renal',
 'Combinacao associada a risco substancialmente aumentado de lesao renal aguda por reducao da perfusao glomerular.',
 'Evitar a associacao tripla; monitorar funcao renal se uso concomitante for inevitavel.',
 'M01A', 'Moderada', 'Forte', 'ALTA'),

('INTERACAO_MEDICAMENTO_MEDICAMENTO', 'IECA/BRA + Espironolactona (risco de hipercalemia)', 'C09',
 'Renal / Eletrolitico',
 'Ambas as classes reduzem excrecao de potassio; combinacao aumenta risco de hipercalemia grave, especialmente com DRC concomitante.',
 'Monitorar potassio serico periodicamente; ajustar dose ou suspender se K+ > 5.5 mEq/L.',
 'C03DA', 'Moderada', 'Forte', 'ALTA'),

('INTERACAO_MEDICAMENTO_MEDICAMENTO', 'Benzodiazepinicos + Alcool/Outros depressores do SNC', 'N05BA',
 'Sistema Nervoso Central',
 'Potencializacao do efeito sedativo com risco de depressao respiratoria e quedas.',
 'Evitar a combinacao.',
 'N05C', 'Alta', 'Forte', 'CRITICA')
ON CONFLICT (criteria_type, drug_or_class) DO NOTHING;
