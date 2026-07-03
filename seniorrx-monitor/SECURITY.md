# Politica de Seguranca

## Escopo

Este e um projeto de pesquisa/educacional. Ainda assim, tratamos seguranca com
seriedade porque o padrao de dados (mesmo sintetico) modela informacao de saude.

## Reportando uma vulnerabilidade

Nao abra uma issue publica para vulnerabilidades. Envie um e-mail para o
mantenedor do projeto com:
- Descricao da vulnerabilidade e impacto potencial;
- Passos para reproduzir;
- Versao/commit afetado.

Prazo de resposta inicial: ate 5 dias uteis.

## Praticas adotadas neste repositorio

- **Sem PII no schema**: `patients` nao possui nome, CPF, endereco ou telefone —
  apenas `pseudonym` (identificador nao reversivel) e dados demograficos minimos.
- **Segredos fora do codigo**: toda credencial vem de variaveis de ambiente
  (`.env`, nunca commitado — ver `.env.example`). CI usa GitHub Secrets.
  `.dockerignore` impede que `.env`/`.git` entrem nas imagens.
- **Autenticacao de API endurecida** (`src/seniorrx/interface/api/security.py`):
  - comparacao da API Key em **tempo constante** (`hmac.compare_digest`),
    mitigando timing attacks;
  - **fail-closed em producao**: com `SENIORRX_ENV=production`, a ausencia de
    `SENIORRX_API_KEY` retorna 503 em vez de deixar a API aberta;
  - para producao real, evoluir para OAuth2/OIDC no provedor de identidade.
- **Cabecalhos de seguranca** em toda resposta (`SecurityHeadersMiddleware`):
  `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`
  e `Strict-Transport-Security` (HSTS) quando em producao.
- **Rate limiting** por IP (`slowapi`, configuravel via `SENIORRX_RATE_LIMIT`):
  limita forca-bruta contra a API Key e abuso de recursos.
- **HTTPS obrigatorio em producao**: terminar TLS no proxy reverso/load balancer
  (nginx, Traefik, ALB); nunca expor a API FastAPI diretamente em HTTP na internet.
- **Varredura automatizada no CI** (`.github/workflows/ci.yml`, job `security-scan`):
  - **bandit** (SAST) sobre `src/`;
  - **pip-audit** para CVEs em dependencias;
  - **gitleaks** para deteccao de segredos vazados no historico.
- **Dependências**: `pyproject.toml` fixa versoes minimas; recomenda-se
  Dependabot/Renovate para atualizacao continua.
- **Principio de menor privilegio no banco**: o usuario de aplicacao deve ter
  apenas `SELECT/INSERT/UPDATE` nas tabelas necessarias, sem `DROP`/`ALTER`
  em producao (migrations rodam com um usuario administrativo separado).
- **Container nao-root**: as imagens rodam como usuario `seniorrx` (uid 1000),
  sem privilegios de root.
- **Logs**: `configs/logging.yaml` documenta a proibicao de logar payloads
  clinicos em texto livre — apenas identificadores e contadores agregados.

## Fora de escopo

Este projeto nao implementa criptografia em repouso (delegada ao provedor de
banco gerenciado/disco criptografado) nem WAF — ambos devem ser configurados
na infraestrutura de deploy, fora deste repositorio.
