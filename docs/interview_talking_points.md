# Como Explicar Este Projeto em Entrevista

## Pitch de 30 segundos

"Construi uma plataforma que aplica os criterios oficiais da American
Geriatrics Society (Beers 2023) para identificar medicamentos de risco em
pacientes idosos — cobrindo desde o schema do banco de dados ate um motor de
regras clinico, uma API, um modelo de ML complementar e um pipeline completo
de MLOps. O foco foi arquitetura limpa e testabilidade: a logica clinica e
100% desacoplada de banco de dados e framework web, o que permite testar
regras complexas de interacao medicamentosa sem subir infraestrutura."

## Perguntas provaveis e como responder

**"Por que separar domain/application/infrastructure/interface?"**
> Porque a regra de negocio (o que conta como PIM, o que e polifarmacia) e o
> ativo mais valioso e mais sensivel a mudanca do projeto — precisa ser
> testada isoladamente e nunca deve depender de detalhes de implementacao
> como SQLAlchemy ou FastAPI. Isso tambem facilita trocar Postgres por outro
> banco, ou a API por gRPC, sem tocar em uma linha de regra clinica.

**"Como voce validou que as regras estao corretas?"**
> Com testes unitarios que cobrem casos conhecidos da literatura (ex.:
> glibenclamida sempre PIM, benzodiazepinico + historico de queda ativa um
> alerta de condicao especifica). Mas fui explicito na documentacao
> (`docs/clinical_validation.md`) de que isso valida *fidelidade de
> implementacao*, nao validacao clinica prospectiva — que exigiria dataset
> golden revisado por farmaceutico e, idealmente, dados reais.

**"Por que um RandomForest e nao um modelo mais sofisticado?"**
> Priorizei interpretabilidade sobre performance marginal, porque em contexto
> clinico um modelo caixa-preta é dificil de auditar e de confiar. Alem
> disso, fui transparente que o rotulo de treino no dataset sintetico e uma
> proxy estatistica, nao um desfecho real — isso evita a armadilha comum de
> "vender" um modelo como clinicamente validado quando na verdade so prova o
> pipeline de ponta a ponta.

**"Como isso lida com dados sensiveis de saude?"**
> O schema nunca armazena PII — pacientes sao identificados por pseudonimo
> nao reversivel. Todos os dados de demonstracao sao sinteticos, gerados com
> seed fixa para reprodutibilidade. Documentei a estrategia de LGPD/GDPR e
> deixei explicito o que mudaria se fosse adaptado para dados reais
> (anonimizacao previa, controle de acesso RBAC, board de etica).

**"O que voce faria diferente com mais tempo/recursos?"**
> Validaria o motor de regras contra um dataset golden com farmaceutico
> clinico, integraria HL7 FHIR para ingestao de prontuarios reais, e
> substituiria o rotulo sintetico do modelo de ML por um desfecho real
> (reinternacao por RAM em 30 dias) — tudo ja mapeado no `docs/roadmap.md`.

## Foco de impacto (nao superestimar)

Evite alegar "reduz reacoes adversas em X%" sem dado real. Posicione o
projeto pelo que ele efetivamente demonstra: capacidade de traduzir um
guideline clinico denso em um sistema de software auditavel, testado e
operacionalizavel — uma habilidade central em HealthTech/Clinical
Informatics, independente do dominio clinico especifico.
