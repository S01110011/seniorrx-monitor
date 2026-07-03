# Resumo de Referencia — Subconjunto de Criterios Implementados

Este arquivo documenta, criterio a criterio, a origem conceitual do
subconjunto ilustrativo carregado em `sql/seed_beers_pim.sql`. Todos os
criterios abaixo correspondem a categorias amplamente descritas na
literatura de farmacoterapia geriatrica e nos proprios AGS Beers Criteria(R);
doses/limiares exatos podem divergir levemente da tabela oficial mais
recente — sempre validar contra a fonte primaria antes de uso assistencial.

| Categoria | Exemplos incluidos | Racional resumido |
|---|---|---|
| PIM independente de diagnostico | Antidepressivos triciclicos, benzodiazepinicos, Z-drugs, anti-histaminicos 1a geracao, relaxantes musculares, glibenclamida, nifedipino curta acao, digoxina >0.125mg/dia, alfa-bloqueadores como monoterapia, metoclopramida cronica, IBP cronico, AINE cronico, meperidina, insulina em escala movel isolada | Perfil farmacocinetico/farmacodinamico desfavoravel em idosos (ver `docs/beers_criteria.md`) |
| PIM por condicao especifica | AINE em IC; antipsicotico em demencia; anticolinergico em demencia; benzodiazepinico em historico de queda; AINE em DRC avancada | Interacao doenca-medicamento com risco documentado de descompensacao |
| Interacao medicamento-medicamento | Opioide+benzodiazepinico; varfarina+AINE; IECA/BRA+diuretico+AINE ("triple whammy"); IECA/BRA+espironolactona; benzodiazepinico+alcool | Sinergismo de toxicidade bem descrito em farmacovigilancia |

## Fontes primarias recomendadas para expansao

1. American Geriatrics Society Beers Criteria(R) Update Expert Panel.
   *American Geriatrics Society 2023 updated AGS Beers Criteria(R) for
   potentially inappropriate medication use in older adults.* J Am Geriatr
   Soc. 2023;71(7):2052-2081. doi:10.1111/jgs.18372
2. O'Mahony D, et al. *STOPP/START criteria for potentially inappropriate
   prescribing in older people: version 3.* Age Ageing. 2023;52(3).
   (Criterio europeu complementar, util para expandir cobertura de
   interacao doenca-medicamento e omissao de prescricao.)
3. Masnoon N, Shakib S, Kalisch-Ellett L, Caughey GE. *What is
   polypharmacy? A systematic review of definitions.* BMC Geriatr.
   2017;17:230. (Base para os limiares de polifarmacia/hiperpolifarmacia.)

> Ao adicionar um novo criterio, cite a fonte especifica (artigo, secao da
> tabela AGS) no PR — ver `CONTRIBUTING.md` e o template de issue
> "Novo criterio clinico".
