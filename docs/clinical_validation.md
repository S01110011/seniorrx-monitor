# Validacao Cientifica e Clinica

## Aviso central

**SeniorRx Monitor e um projeto de pesquisa/educacao.** Nenhum componente
deste sistema foi validado prospectivamente em populacao real, submetido a
orgao regulador (ANVISA/FDA/CE como SaMD) ou testado em ensaio clinico. Os
resultados abaixo descrevem *como* o sistema deveria ser validado, nao uma
validacao ja realizada.

## 1. Validacao do motor de regras (Beers/DDI/polifarmacia)

O motor de regras e **deterministico e auditavel por construcao** — cada
alerta e rastreavel a uma linha especifica em `beers_pim_criteria` com fonte
citada. A validacao aqui e essencialmente de **fidelidade de implementacao**:

- Testes unitarios (`tests/unit/`) cobrem: reconhecimento correto de PIM por
  ATC, respeito ao limiar etario (>=65a), casamento de condicao especifica por
  ICD-10, casamento par-a-par de interacoes, thresholds de polifarmacia/eGFR.
- Recomenda-se, antes de uso em qualquer ambiente real, um **conjunto de
  casos de teste clinico revisado por farmaceutico** (golden dataset com
  casos conhecidos de PIM/nao-PIM), comparando saida do sistema contra
  revisao manual — metrica alvo: concordancia >=95% (Cohen's kappa).

## 2. Validacao do modelo de ML (probabilidade de evento adverso)

O rotulo usado em `scripts/build_training_set.py` (`adverse_event`) e **uma
variavel latente sintetica**, gerada por uma funcao logistica calibrada para
correlacionar com PIM/polifarmacia/eGFR baixo — **nao um desfecho clinico
observado**. Isso existe para permitir demonstrar o pipeline de MLOps de
ponta a ponta (features -> treino -> tracking -> serving -> monitoramento).

**Antes de qualquer uso assistencial**, o modelo deve ser retreinado com um
rotulo clinico real, por exemplo:
- Reinternacao hospitalar em 30 dias atribuivel a reacao adversa a medicamento;
- Visita a emergencia com CID compativel com RAM (ICD-10 Y40-Y59 / T36-T50);
- Evento de farmacovigilancia reportado (ex.: VigiBase/Notivisa).

Metricas recomendadas para validacao com dados reais:
- **Discriminacao**: AUROC, AUPRC (priorizar AUPRC dado desbalanceamento
  esperado do desfecho);
- **Calibracao**: Brier score, calibration plot (probabilidade predita vs.
  observada por decil);
- **Validacao externa**: coorte de outra instituicao/periodo antes de
  generalizar;
- **Fairness**: desempenho estratificado por sexo, faixa etaria e
  care_setting, para evitar viés sistemático contra subgrupos.

## 3. Epidemiologia descritiva (relatorio R/Quarto)

`reports/quarto/clinical_report.qmd` produz estatisticas descritivas
(prevalencia de PIM, distribuicao de polifarmacia) — util para caracterizar
uma coorte, mas **nao estabelece causalidade**. Para inferencia causal
(ex.: "PIM causa mais quedas"), seria necessario desenho de coorte
prospectivo ou emulacao de trial-alvo com ajuste para confusão por indicacao.

## 4. Referencias que embasam as escolhas metodologicas

Ver [`docs/references.md`](references.md) para a lista completa.
