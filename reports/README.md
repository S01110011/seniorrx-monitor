# reports/

Saidas geradas (nao versionadas em git, exceto os fontes `.qmd`):

- `quarto/clinical_report.qmd` — fonte do relatorio epidemiologico reprodutivel (R/Quarto).
  Renderizar com: `quarto render reports/quarto/clinical_report.qmd --to html`
- `drift_report.html` — gerado automaticamente pelo workflow `model-monitoring.yml` (Evidently AI).

Os `.html`/`.pdf` renderizados sao artefatos de execucao e ficam fora do controle de versao
(ver `.gitignore`); publique-os como GitHub Actions artifacts ou em `gh-pages` se necessario.
