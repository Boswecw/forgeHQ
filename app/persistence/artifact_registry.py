"""
Artifact registry persistence stub for forgeHQ — Phase 5.

Maintains an in-memory registry of artifact stubs by artifact_id.
The DataForge persistence wiring is not yet implemented — this stub
provides the typed boundary and in-memory semantics for Phase 5 testing.

Hard rules:
- Artifacts are append-only; re-registering the same artifact_id is a no-op.
- Deterministic evidence lineage, non-authoritative proposal lineage, and
  operator decision lineage must remain in separate logical layers.
"""
from app.domain.artifacts.enums import ArtifactFamily, LineageLayer
from app.schemas._base import ArtifactStub


class ArtifactRegistryError(RuntimeError):
    """Raised when the artifact registry encounters an integrity violation."""


class ArtifactRegistry:
    """
    In-memory artifact registry.

    Accepts ArtifactStub instances and indexes them by artifact_id.
    DataForge wiring is pending Phase 5 DataForge integration.
    """

    def __init__(self) -> None:
        self._store: dict[str, ArtifactStub] = {}
        self._family_index: dict[ArtifactFamily, list[str]] = {}

    def register(self, artifact: ArtifactStub) -> None:
        """
        Register an artifact in the in-memory store.

        Re-registration of an existing artifact_id is a no-op (append-only semantics).
        """
        if artifact.artifact_id in self._store:
            return

        self._store[artifact.artifact_id] = artifact
        self._family_index.setdefault(artifact.artifact_family, []).append(
            artifact.artifact_id
        )

    def get(self, artifact_id: str) -> ArtifactStub | None:
        """Return the artifact for the given ID, or None if not found."""
        return self._store.get(artifact_id)

    def list_by_family(self, family: ArtifactFamily) -> list[ArtifactStub]:
        """Return all registered artifacts of the given family."""
        ids = self._family_index.get(family, [])
        return [self._store[aid] for aid in ids]

    def count(self) -> int:
        return len(self._store)
