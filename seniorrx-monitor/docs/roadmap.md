# Roadmap

## v0.1 — Prototipo (atual)
- [x] Arquitetura limpa (domain/application/infrastructure/interface).
- [x] Schema PostgreSQL + subconjunto ilustrativo de criterios Beers 2023.
- [x] Motor de regras: PIM, polifarmacia/hiperpolifarmacia, DDI, ajuste renal.
- [x] API FastAPI + dashboard Streamlit.
- [x] Geracao de dados sinteticos + ETL.
- [x] Modelo de ML (RandomForest) com rotulo sintetico + tracking MLflow.
- [x] Suite de testes (unit + integration), CI no GitHub Actions.
- [x] Relatorio reprodutivel R/Quarto.
- [x] Documentacao tecnica completa.

## v0.2 — Robustez e cobertura clinica
- [ ] Expandir `beers_pim_criteria` para categoria "Usar com cautela" (ainda
      nao coberta pelo motor de regras).
- [ ] Suporte a STOPP/START v3 como segunda fonte de criterios (comparacao
      cruzada de alertas).
- [ ] Autenticacao OAuth2/OIDC real substituindo o stub de API Key.
- [ ] Fila assincrona (ex.: Celery/RQ) para reavaliacao em lote de coortes grandes.
- [ ] Explicabilidade por instancia (SHAP) no modelo de ML, alem de importancia global.
- [ ] Internacionalizacao dos textos de alerta (pt-BR / en-US).

## v0.3 — Escala e observabilidade
- [ ] Dashboard multi-paciente com filtros populacionais (unidade, faixa etaria, risco).
- [ ] Integracao HL7 FHIR (recurso `MedicationRequest`/`Condition`) para
      ingestao a partir de prontuarios eletronicos reais (com anonimizacao).
- [ ] Alertas automaticos de drift (Evidently) abrindo issue via API do GitHub.
- [ ] Auditoria completa de decisao (quem reconheceu/descartou cada alerta, com justificativa obrigatoria).
- [ ] Row-Level Security no PostgreSQL para multi-tenancy (multiplas instituicoes).

## v1.0 — Release estavel
- [ ] Validacao com dataset golden revisado por farmaceutico clinico
      (concordancia >=95% — ver `docs/clinical_validation.md`).
- [ ] Retreino do modelo de ML com rotulo clinico real (nao mais sintetico).
- [ ] Documentacao de conformidade LGPD/GDPR revisada por especialista juridico.
- [ ] Avaliacao formal de enquadramento regulatorio (SaMD) caso destinado a uso assistencial real.
- [ ] Publicacao de artigo/whitepaper descrevendo metodologia e resultados de validacao.
