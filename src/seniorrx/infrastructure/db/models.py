"""Modelos SQLAlchemy ORM — espelham `sql/schema.sql`.

Mantidos na camada de infraestrutura (nao de dominio) para que as regras
de negocio em `domain/` permanecam livres de dependencia de ORM.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PatientModel(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pseudonym: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    birth_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    height_cm: Mapped[float | None] = mapped_column(Numeric(5, 2))
    serum_creatinine_mg_dl: Mapped[float | None] = mapped_column(Numeric(4, 2))
    egfr_ml_min_1_73m2: Mapped[float | None] = mapped_column(Numeric(5, 1))
    care_setting: Mapped[str] = mapped_column(String(32), nullable=False, default="ambulatorial")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    comorbidities: Mapped[list[ComorbidityModel]] = relationship(back_populates="patient")
    prescriptions: Mapped[list[PrescriptionModel]] = relationship(back_populates="patient")


class ComorbidityModel(Base):
    __tablename__ = "comorbidities"

    comorbidity_id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    icd10_code: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnosed_on: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    patient: Mapped[PatientModel] = relationship(back_populates="comorbidities")


class MedicationModel(Base):
    __tablename__ = "medications"

    medication_id: Mapped[int] = mapped_column(primary_key=True)
    drug_name: Mapped[str] = mapped_column(String(150), nullable=False)
    atc_code: Mapped[str] = mapped_column(String(10), nullable=False)
    drug_class: Mapped[str] = mapped_column(String(120), nullable=False)
    route: Mapped[str] = mapped_column(String(30), default="oral")
    is_high_alert: Mapped[bool] = mapped_column(Boolean, default=False)


class BeersPimCriterionModel(Base):
    __tablename__ = "beers_pim_criteria"
    # Paridade com sql/schema.sql: chave natural que torna o seed idempotente.
    __table_args__ = (UniqueConstraint("criteria_type", "drug_or_class"),)

    criterion_id: Mapped[int] = mapped_column(primary_key=True)
    criteria_type: Mapped[str] = mapped_column(String(40), nullable=False)
    drug_or_class: Mapped[str] = mapped_column(String(150), nullable=False)
    atc_pattern: Mapped[str | None] = mapped_column(String(10))
    organ_system: Mapped[str | None] = mapped_column(String(80))
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    related_condition_icd10: Mapped[str | None] = mapped_column(String(10))
    interacting_atc_pattern: Mapped[str | None] = mapped_column(String(10))
    egfr_threshold_ml_min: Mapped[float | None] = mapped_column(Numeric(5, 1))
    quality_of_evidence: Mapped[str | None] = mapped_column(String(10))
    strength_of_recommendation: Mapped[str | None] = mapped_column(String(10))
    severity_default: Mapped[str] = mapped_column(String(10), default="MODERADA")
    source_reference: Mapped[str] = mapped_column(String(255))


class PrescriptionModel(Base):
    __tablename__ = "prescriptions"

    prescription_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    medication_id: Mapped[int] = mapped_column(ForeignKey("medications.medication_id"))
    prescriber_pseudonym: Mapped[str] = mapped_column(String(32), nullable=False)
    dose_value: Mapped[float | None] = mapped_column(Numeric(8, 2))
    dose_unit: Mapped[str | None] = mapped_column(String(20))
    frequency_per_day: Mapped[float | None] = mapped_column(Numeric(4, 1))
    route: Mapped[str | None] = mapped_column(String(30))
    indication_icd10: Mapped[str | None] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    patient: Mapped[PatientModel] = relationship(back_populates="prescriptions")
    medication: Mapped[MedicationModel] = relationship()


class AlertModel(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    prescription_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("prescriptions.prescription_id")
    )
    criterion_id: Mapped[int | None] = mapped_column(ForeignKey("beers_pim_criteria.criterion_id"))
    alert_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ABERTO")
    reviewed_by_pseudonym: Mapped[str | None] = mapped_column(String(32))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RiskScoreModel(Base):
    __tablename__ = "risk_scores"

    score_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    active_medication_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    pim_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ddi_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comorbidity_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    rule_based_risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    ml_adverse_event_probability: Mapped[float | None] = mapped_column(Numeric(5, 4))
    model_version: Mapped[str | None] = mapped_column(String(40))
    explanation: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
