from app.domain.artifacts.enums import ArtifactFamily
from app.domain.workers.enums import WORKER_OWNERSHIP_REGISTRY, WorkerName


def test_worker_registry_covers_every_required_worker():
    assert set(WORKER_OWNERSHIP_REGISTRY) == set(WorkerName)


def test_orchestrator_emits_no_proposal_content():
    assert WORKER_OWNERSHIP_REGISTRY[WorkerName.ORCHESTRATOR] == ()


def test_generator_and_critic_lanes_remain_structurally_independent():
    generator_artifacts = set(WORKER_OWNERSHIP_REGISTRY[WorkerName.GENERATOR])
    critic_artifacts = set(WORKER_OWNERSHIP_REGISTRY[WorkerName.CRITIC_FALSIFIER])
    verifier_artifacts = set(WORKER_OWNERSHIP_REGISTRY[WorkerName.VERIFIER])

    assert generator_artifacts == {ArtifactFamily.CANDIDATE_PATCH}
    assert critic_artifacts == {ArtifactFamily.FALSIFICATION_REPORT}
    assert verifier_artifacts == {ArtifactFamily.CANDIDATE_VERIFICATION}
    assert generator_artifacts.isdisjoint(critic_artifacts)
