#!/usr/bin/env bash
# Gera um .env a partir de .env.example com segredos FORTES e aleatorios.
# Nao sobrescreve um .env existente (evita perder segredos ja em uso).
# Uso: bash scripts/gen_secrets.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f .env ]; then
  echo "ERRO: .env ja existe. Remova-o manualmente se quiser regerar." >&2
  exit 1
fi

gen() { python -c "import secrets; print(secrets.token_urlsafe($1))"; }

PG_PASS="$(gen 24)"
API_KEY="$(gen 32)"

cp .env.example .env
# Preenche os segredos (sed compativel com GNU e BSD)
python - "$PG_PASS" "$API_KEY" <<'PY'
import sys, pathlib
pg, api = sys.argv[1], sys.argv[2]
p = pathlib.Path(".env")
text = p.read_text(encoding="utf-8")
text = text.replace("POSTGRES_PASSWORD=", f"POSTGRES_PASSWORD={pg}", 1)
text = text.replace("SENIORRX_API_KEY=", f"SENIORRX_API_KEY={api}", 1)
text = text.replace("seniorrx:CHANGE_ME@", f"seniorrx:{pg}@")
p.write_text(text, encoding="utf-8")
PY

chmod 600 .env 2>/dev/null || true
echo "OK: .env gerado com segredos fortes (permissao 600). NUNCA commite este arquivo."
