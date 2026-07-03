# Issues Iniciais Sugeridas (GitHub)

Copie os itens abaixo como issues reais no repositorio (cada um ja mapeado
para o template apropriado em `.github/ISSUE_TEMPLATE/`).

1. **[FEATURE] Implementar tabela e seed de PIM (Beers 2023)** — done no v0.1,
   manter como referencia historica / issue de expansao continua.
2. **[FEATURE] Criar pipeline de ingestao de dados (ETL)** — done no v0.1;
   proximo passo: suportar ingestao incremental (upsert) em vez de full load.
3. **[FEATURE] Adicionar categoria "Usar com cautela" ao motor de regras**
   — atualmente `CriteriaType.USE_WITH_CAUTION` existe no dominio mas nao
   tem engine dedicado nem seeds.
4. **[FEATURE] Suporte a criterios STOPP/START v3 como fonte alternativa**
   — permitir comparar alertas Beers vs. STOPP/START no mesmo paciente.
5. **[BUG] Validar timezone em `generated_at`/`calculated_at` para pacientes
   em fusos diferentes do servidor** — auditar uso de `datetime.utcnow()`.
6. **[FEATURE] Autenticacao OAuth2/OIDC substituindo o stub de API Key**
   — ver nota em `src/seniorrx/interface/api/main.py`.
7. **[FEATURE] Explicabilidade por instancia (SHAP) no modelo de risco**
   — hoje `AdverseEventRiskModel.explain()` retorna apenas importancia global.
8. **[FEATURE] Job de retrain automatico gatilhado por drift do Evidently**
   — hoje o workflow so gera o relatorio, sem acao automatica.
9. **[CRITERIO] Revisar limiares de dose no criterio de digoxina contra a
   tabela oficial AGS 2023 mais recente** — confirmar 0.125mg/dia.
10. **[FEATURE] Adicionar testes de carga/performance na API (>=1000 pacientes)**
    — validar tempo de resposta de `/patients` com paginacao.
11. **[FEATURE] Internacionalizacao (pt-BR/en-US) das mensagens de alerta**.
12. **[FEATURE] Row-Level Security multi-tenant no PostgreSQL**.

## Sugestoes de mensagens de commit para as primeiras funcionalidades

```
feat: inicializa estrutura do projeto com FastAPI e base de dados PostgreSQL
feat: adiciona schema SQL de pacientes, medicamentos e criterios Beers 2023
feat: implementa motor de regras BeersRulesEngine para deteccao de PIM
feat: adiciona PolypharmacyRulesEngine com limiares de poli/hiperpolifarmacia
feat: implementa InteractionRulesEngine para DDI e ajuste por funcao renal
feat: adiciona RiskScoringService consolidando alertas em nivel de risco
feat: expõe API REST FastAPI para consulta de risco por paciente
feat: adiciona dashboard Streamlit para visualizacao clinica interativa
feat: implementa geracao de dados sinteticos e pipeline de ETL
feat: adiciona modelo de ML de risco de evento adverso com tracking MLflow
test: adiciona suite de testes unitarios para motores de regra de dominio
ci: configura GitHub Actions para lint, typecheck, testes e build Docker
docs: adiciona documentacao tecnica completa (arquitetura, schema, roadmap)
```
