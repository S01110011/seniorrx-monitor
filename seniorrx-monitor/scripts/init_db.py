"""Inicializa o banco: aplica schema.sql + seed_beers_pim.sql via psycopg.

Uso:
    python scripts/init_db.py --database-url postgresql://seniorrx:seniorrx@localhost:5432/seniorrx
"""

from __future__ import annotations

import argparse
from pathlib import Path

import psycopg

REPO_ROOT = Path(__file__).resolve().parents[1]


def apply_sql_file(conn: psycopg.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Aplicado: {path.relative_to(REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa o banco do SeniorRx Monitor")
    parser.add_argument(
        "--database-url",
        default="postgresql://seniorrx:seniorrx@localhost:5432/seniorrx",
        help="String de conexao (nao usar credenciais reais aqui — apenas dev/local)",
    )
    args = parser.parse_args()

    with psycopg.connect(args.database_url) as conn:
        apply_sql_file(conn, REPO_ROOT / "sql" / "schema.sql")
        apply_sql_file(conn, REPO_ROOT / "sql" / "seed_beers_pim.sql")

    print("Banco inicializado com sucesso.")


if __name__ == "__main__":
    main()
