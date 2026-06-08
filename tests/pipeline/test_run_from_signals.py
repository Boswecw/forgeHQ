"""Tests for orchestrator P3 — drive the real SIGNAL_INTAKE stage from signals.

The SIGNAL_INTAKE stage emits a real (non-placeholder) SignalSnapshot from
admitted forge-eval / ForgeMath / cloud refs; the remaining stages stay on the
placeholder path (P4), so the run still completes to a ForgeHQProposal.
"""
import pytest

from app.domain.artifacts.enums import ArtifactFamily
from app.domain.pipeline.enums import PIPELINE_STAGE_ORDER, PipelineStage
from app.domain.reviewability.enums import ProposalLifecycleState
from app.orchestration.forgehq_orchestrator import ForgeHQOrchestrator
from app.services.cloud_source_feeder import CloudSourceFeeder
from app.services.eval_source_feeder import EvalSourceFeeder
from app.services.signal_intake_service import NoAdmittedSourcesError


def _mixed_refs() -> tuple[str, ...]:
    ev = EvalSourceFeeder()
    cloud = CloudSourceFeeder()
    return (
        ev.forgeeval_output("forge_eval_evidence_bundle", "eb-1").to_source_ref(),
        ev.forgemath_output("forgemath_evaluation", "ev-1").to_source_ref(),
        cloud.proposal("p-1", "neuroforge").to_source_ref(),
    )


def test_advance_signal_intake_produces_real_snapshot():
    orch = ForgeHQOrchestrator()
    run = orch.advance_signal_intake(orch.start_run("r1"), _mixed_refs())
    snap = run.get_artifact(ArtifactFamily.SIGNAL_SNAPSHOT)
    assert snap.placeholder is False
    assert set(snap.admitted_source_refs) == set(_mixed_refs())
    assert run.current_stage == PipelineStage.SIGNAL_INTAKE


def test_run_from_signals_completes_pipeline_with_real_intake():
    orch = ForgeHQOrchestrator()
    run = orch.run_from_signals("r2", _mixed_refs())

    # full pipeline completes to a packaged proposal
    assert run.completed_stages == PIPELINE_STAGE_ORDER
    assert run.current_stage == PipelineStage.PROPOSAL_PACKAGING
    assert run.proposal_lifecycle_state == ProposalLifecycleState.PACKAGED
    assert run.has_artifact(ArtifactFamily.FORGEHQ_PROPOSAL)

    # intake is REAL (not placeholder), carrying our admitted refs
    snap = run.get_artifact(ArtifactFamily.SIGNAL_SNAPSHOT)
    assert snap.placeholder is False
    assert set(snap.admitted_source_refs) == set(_mixed_refs())


def test_run_from_signals_fails_closed_on_empty():
    with pytest.raises(NoAdmittedSourcesError):
        ForgeHQOrchestrator().run_from_signals("r3", ())


def test_run_from_signals_fails_closed_on_all_unknown():
    with pytest.raises(NoAdmittedSourcesError):
        ForgeHQOrchestrator().run_from_signals("r4", ("bogus://x", "nope://y"))
