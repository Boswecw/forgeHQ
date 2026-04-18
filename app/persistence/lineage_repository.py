"""
Lineage edge persistence stub for forgeHQ — Phase 5.

Records directed parent→child artifact lineage edges with layer classification.
Preserves deterministic evidence lineage separately from non-authoritative
proposal lineage and operator decision lineage.

DataForge wiring is pending Phase 5 DataForge integration.
"""
from dataclasses import dataclass

from app.domain.artifacts.enums import LineageLayer


@dataclass(frozen=True, slots=True)
class LineageEdge:
    parent_artifact_id: str
    child_artifact_id: str
    layer: LineageLayer


class LineageRepository:
    """
    In-memory lineage edge store.

    DataForge wiring is pending Phase 5 DataForge integration.
    """

    def __init__(self) -> None:
        self._edges: list[LineageEdge] = []

    def record_edge(
        self,
        parent_artifact_id: str,
        child_artifact_id: str,
        layer: LineageLayer,
    ) -> None:
        """Record a directed parent→child lineage edge."""
        edge = LineageEdge(
            parent_artifact_id=parent_artifact_id,
            child_artifact_id=child_artifact_id,
            layer=layer,
        )
        self._edges.append(edge)

    def edges_for(self, artifact_id: str) -> list[LineageEdge]:
        """Return all edges where artifact_id is the child."""
        return [e for e in self._edges if e.child_artifact_id == artifact_id]

    def children_of(self, artifact_id: str) -> list[LineageEdge]:
        """Return all edges where artifact_id is the parent."""
        return [e for e in self._edges if e.parent_artifact_id == artifact_id]

    def all_edges(self) -> list[LineageEdge]:
        return list(self._edges)

    def count(self) -> int:
        return len(self._edges)
