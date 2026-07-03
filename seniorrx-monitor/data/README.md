# data/

## `raw/`
CSVs sinteticos gerados por `scripts/generate_synthetic_data.py` (patients, comorbidities,
prescriptions). Nao versionados em git (ver `.gitignore`) — cada desenvolvedor gera sua
propria copia local com seed fixa para reprodutibilidade.

## `processed/`
Datasets derivados (feature store local): `training_set.parquet`, `risk_model.joblib`.
Gerados por `scripts/build_training_set.py` e `seniorrx.infrastructure.ml.train`.

## Politica de dados (LGPD/GDPR)

- **Nenhum dado real de paciente deve ser colocado nesta pasta.**
- Se este projeto for adaptado para dados reais, eles devem estar previamente anonimizados
  (sem nome, CPF/SSN, endereco, telefone, numero de prontuario) e o acesso deve ser restrito
  por controle de acesso baseado em papel (RBAC) fora do escopo deste repositorio.
- Para versionamento de datasets maiores/reais, usar DVC apontando para um storage
  criptografado e com controle de acesso (ver `configs/mlops.md`), nunca git puro.
