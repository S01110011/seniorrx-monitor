"""Motor de regras: polifarmacia e hiperpolifarmacia.

Definicoes adotadas (consenso da literatura geriatrica — ver docs/references.md):
  - Polifarmacia: uso concomitante de >=5 medicamentos cronicos.
  - Hiperpolifarmacia: uso concomitante de >=10 medicamentos cronicos.
"""

from __future__ import annotations

from seniorrx.domain.entities import Alert, AlertType, Patient, Severity
from seniorrx.domain.value_objects import (
    HYPER_POLYPHARMACY_THRESHOLD,
    POLYPHARMACY_THRESHOLD,
)


class PolypharmacyRulesEngine:
    def evaluate_patient(self, patient: Patient) -> list[Alert]:
        active_count = len(patient.active_prescriptions)

        if active_count >= HYPER_POLYPHARMACY_THRESHOLD:
            return [
                Alert(
                    patient_id=patient.patient_id,
                    alert_type=AlertType.HYPER_POLYPHARMACY,
                    severity=Severity.CRITICAL,
                    message=(
                        f"Hiperpolifarmacia: {active_count} medicamentos ativos concomitantes "
                        f"(limiar: {HYPER_POLYPHARMACY_THRESHOLD}). Recomenda-se revisao "
                        f"farmacoterapeutica estruturada (ex.: metodo STOPP/START ou deprescricao)."
                    ),
                )
            ]

        if active_count >= POLYPHARMACY_THRESHOLD:
            return [
                Alert(
                    patient_id=patient.patient_id,
                    alert_type=AlertType.POLYPHARMACY,
                    severity=Severity.MODERATE,
                    message=(
                        f"Polifarmacia: {active_count} medicamentos ativos concomitantes "
                        f"(limiar: {POLYPHARMACY_THRESHOLD}). Considerar revisao de indicacoes "
                        f"e possibilidade de deprescricao."
                    ),
                )
            ]

        return []
