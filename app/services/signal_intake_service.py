"""
Signal intake service for forgeHQ — Stage 1.

Validates source admissibility, classifies authority posture, and produces
a SignalSnapshot + IntakeDiagnostics pair for the shaping pipeline.

Hard rules:
- Unknown source ref schemes are always rejected.
- If no refs are admitted, intake fails closed with NoAdmittedSourcesError.
- Admitted source refs are preserved verbatim in the snapshot.
"""
from app.domain.signals.enums import (
    AdmissibilityDecision,
    SourceAuthorityClass,
    classify_source_authority,
)
from app.schemas.intake_diagnostics import IntakeDiagnostics, SourceAdmissibilityRecord
from app.schemas.signal_snapshot import SignalSnapshot


class SignalIntakeError(ValueError):
    """Base error for signal intake failures."""


class UnknownSourceRefError(SignalIntakeError):
    """Raised when a single source ref is semantically unknown."""


class NoAdmittedSourcesError(SignalIntakeError):
    """Raised when no source refs pass admissibility — intake fails closed."""


class SignalIntakeService:
    """
    Validates and classifies source refs, producing admitted signal artifacts.

    Fails closed if all inputs are unknown or the input set is empty.
    """

    def admit_signals(
        self,
        run_id: str,
        source_refs: tuple[str, ...],
    ) -> tuple[SignalSnapshot, IntakeDiagnostics]:
        """
        Validate and classify a batch of source refs.

        Returns (SignalSnapshot, IntakeDiagnostics) with placeholder=False
        and real admitted/rejected ref lists.

        Raises NoAdmittedSourcesError if the input is empty or every ref
        carries an unknown scheme.
        """
        if not source_refs:
            raise NoAdmittedSourcesError(
                "no source refs provided — signal intake requires at least one ref"
            )

        records: list[SourceAdmissibilityRecord] = []
        admitted: list[str] = []
        rejected: list[str] = []

        for ref in source_refs:
            authority_class = classify_source_authority(ref)
            if authority_class == SourceAuthorityClass.UNKNOWN:
                records.append(
                    SourceAdmissibilityRecord(
                        source_ref=ref,
                        authority_class=SourceAuthorityClass.UNKNOWN,
                        decision=AdmissibilityDecision.REJECTED,
                        rejection_reason="semantically unknown source ref scheme",
                    )
                )
                rejected.append(ref)
            else:
                records.append(
                    SourceAdmissibilityRecord(
                        source_ref=ref,
                        authority_class=authority_class,
                        decision=AdmissibilityDecision.ADMITTED,
                    )
                )
                admitted.append(ref)

        if not admitted:
            raise NoAdmittedSourcesError(
                f"no admissible source refs — all {len(rejected)} ref(s) were rejected "
                f"due to unknown URI schemes"
            )

        snapshot = SignalSnapshot(
            run_id=run_id,
            placeholder=False,
            source_refs=tuple(admitted),
            admitted_source_refs=tuple(admitted),
            rejected_source_refs=tuple(rejected),
            non_authoritative_notice=(
                "Non-authoritative signal snapshot. "
                "Does not claim deterministic upstream truth."
            ),
            summary=(
                f"Admitted {len(admitted)} source ref(s) "
                f"({len(rejected)} rejected at intake)."
            ),
        )

        diagnostics = IntakeDiagnostics(
            run_id=run_id,
            placeholder=False,
            records=tuple(records),
            admitted_count=len(admitted),
            rejected_count=len(rejected),
            parent_artifact_ids=(snapshot.artifact_id,),
            summary=(
                f"Intake diagnostics: {len(admitted)} admitted, {len(rejected)} rejected."
            ),
        )

        return snapshot, diagnostics
