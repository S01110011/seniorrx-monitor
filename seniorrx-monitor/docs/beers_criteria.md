# Criterios de Beers 2023 — Conceitos e Uso Neste Projeto

## O que sao os AGS Beers Criteria

Os **Beers Criteria** sao uma lista de referencia, publicada e atualizada
periodicamente pela **American Geriatrics Society (AGS)**, que identifica
medicamentos cuja relacao risco-beneficio e geralmente desfavoravel em
adultos com 65 anos ou mais — os chamados **Medicamentos Potencialmente
Inapropriados (PIM)**. Criados originalmente por Mark Beers em 1991, sao hoje
mantidos por um painel multidisciplinar de especialistas (geriatria, farmacia
clinica, farmacologia) usando metodologia de revisao sistematica e consenso
formal (Delphi modificado).

A atualizacao de 2023 organiza os criterios em **cinco categorias**:

1. PIM a evitar na maioria dos idosos, **independente de diagnostico** ou condicao;
2. PIM a evitar em idosos com **doencas/sindromes especificas** (interacao doenca-medicamento);
3. Medicamentos a **usar com cautela**;
4. **Interacoes medicamento-medicamento** clinicamente importantes a evitar;
5. Medicamentos que exigem **ajuste de dose por funcao renal**.

**Referencia oficial:**
American Geriatrics Society Beers Criteria(R) Update Expert Panel. *American
Geriatrics Society 2023 updated AGS Beers Criteria(R) for potentially
inappropriate medication use in older adults.* J Am Geriatr Soc.
2023;71(7):2052-2081. doi: [10.1111/jgs.18372](https://doi.org/10.1111/jgs.18372)

## Conceitos-chave

- **Polifarmacia**: uso concomitante de multiplos medicamentos, convencionalmente
  definido como **>=5 medicamentos cronicos** (limiar adotado neste projeto —
  ver `src/seniorrx/domain/value_objects.py`). **Hiperpolifarmacia**: **>=10**.
  Cada medicamento adicional aumenta o risco de interacao, erro de adesao e
  reacao adversa, mesmo quando cada prescricao individual e apropriada.
- **PIM (Medicamento Potencialmente Inapropriado)**: medicamento cujo risco
  supera o beneficio esperado em idosos, geralmente por alteracoes
  farmacocineticas/farmacodinamicas do envelhecimento (reducao de clearance
  renal/hepatico, maior sensibilidade do SNC, menor reserva homeostatica).
- **Interacao medicamento-medicamento (DDI)**: efeito farmacologico alterado
  quando dois farmacos sao usados juntos (ex.: opioide + benzodiazepinico
  potencializando depressao respiratoria).
- **Interacao doenca-medicamento**: um farmaco seguro em geral, mas
  contraindicado ou de alto risco numa condicao clinica especifica (ex.: AINE
  em insuficiencia cardiaca).
- **Deprescricao**: processo estruturado e supervisionado de reducao/suspensao
  de medicamentos cujo risco passou a superar o beneficio — a acao clinica
  tipicamente recomendada apos um alerta de PIM, nunca suspensao abrupta sem
  avaliacao médica.

## IMPORTANTE — Natureza do conteudo neste repositorio

A tabela `beers_pim_criteria` (`sql/seed_beers_pim.sql`) contem um
**subconjunto ilustrativo e educacional** de ~24 criterios amplamente citados
na literatura, escolhidos por relevancia didatica (ex.: benzodiazepinicos,
anti-histaminicos de 1a geracao, AINEs, glibenclamida, "triple whammy").

- **NAO e a tabela oficial completa** dos AGS Beers Criteria 2023, que contem
  dezenas de criterios adicionais, doses especificas e notas de excecao;
- A tabela oficial completa e **propriedade intelectual da American Geriatrics
  Society**, distribuida por Wiley — consulte a publicacao original ou o app
  oficial da AGS para uso clinico assistencial real;
- Este projeto foi desenhado para que adicionar/corrigir criterios seja
  trivial (uma linha em `sql/seed_beers_pim.sql` + citacao da fonte no PR —
  ver template de issue "Novo criterio clinico" e `CONTRIBUTING.md`).

## Aviso de uso

Este software e destinado a **pesquisa e educacao**. Os alertas gerados sao
um apoio a decisao, nao um diagnostico ou prescricao automatizada, e **nao
substituem o julgamento clinico** de um farmaceutico ou medico responsavel
pelo paciente.
