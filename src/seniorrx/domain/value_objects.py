"""Value objects e constantes clinicas usadas pelas regras de dominio."""

from __future__ import annotations

# Limiares de polifarmacia adotados na literatura geriatrica
# (Masnoon et al. 2017; Hanlon & Semla — consenso amplamente citado).
POLYPHARMACY_THRESHOLD = 5          # >=5 medicamentos cronicos concomitantes
HYPER_POLYPHARMACY_THRESHOLD = 10   # >=10 medicamentos cronicos concomitantes

# Estagios de Doenca Renal Cronica (KDIGO) usados nas regras de ajuste renal.
EGFR_STAGE_3B_5_THRESHOLD = 45.0    # mL/min/1.73m2 — abaixo disso, alerta de ajuste renal

# Duracao (dias) acima da qual PPIs/metoclopramida sao considerados uso cronico.
PPI_CHRONIC_USE_DAYS = 56            # 8 semanas
METOCLOPRAMIDE_CHRONIC_USE_DAYS = 84  # 12 semanas
