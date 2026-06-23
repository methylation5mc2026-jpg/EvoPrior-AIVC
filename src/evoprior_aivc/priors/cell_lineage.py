"""Cell lineage tree representation and cell-type mapping utilities."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import yaml


@dataclass(frozen=True)
class LineageValidationReport:
    """Summary returned by lineage tree validation."""

    root: str
    n_nodes: int
    max_depth: int


class LineageTree:
    """A deterministic rooted tree for cell-lineage priors."""

    def __init__(self, edges: Sequence[tuple[str | None, str]]) -> None:
        self._edges = [(parent, child) for parent, child in edges]
        self._parents: dict[str, str | None] = {}
        self._children: dict[str, list[str]] = defaultdict(list)
        self._nodes: set[str] = set()
        self._build()
        self._validation_report = self.validate()

    @classmethod
    def from_edges(cls, edges: Sequence[tuple[str | None, str]]) -> LineageTree:
        return cls(edges)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        *,
        parent_col: str = "parent",
        child_col: str = "child",
    ) -> LineageTree:
        if parent_col not in df.columns or child_col not in df.columns:
            raise KeyError(f"dataframe must contain {parent_col!r} and {child_col!r}")
        edges = []
        for _, row in df.iterrows():
            parent = row[parent_col]
            parent_value = None if pd.isna(parent) else str(parent)
            edges.append((parent_value, str(row[child_col])))
        return cls(edges)

    @classmethod
    def from_yaml(cls, path: str | Path) -> LineageTree:
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        edges = payload.get("edges", payload)
        normalized_edges: list[tuple[str | None, str]] = []
        for edge in edges:
            parent = edge.get("parent") if isinstance(edge, Mapping) else edge[0]
            child = edge.get("child") if isinstance(edge, Mapping) else edge[1]
            normalized_edges.append((None if parent in {None, ""} else str(parent), str(child)))
        return cls(normalized_edges)

    @property
    def nodes(self) -> tuple[str, ...]:
        return tuple(sorted(self._nodes))

    @property
    def root(self) -> str:
        roots = [node for node, parent in self._parents.items() if parent is None]
        if len(roots) != 1:
            raise ValueError(f"expected exactly one root, found {len(roots)}")
        return roots[0]

    def parent(self, node: str) -> str | None:
        self._require_node(node)
        return self._parents[node]

    def children(self, node: str) -> tuple[str, ...]:
        self._require_node(node)
        return tuple(sorted(self._children.get(node, [])))

    def ancestors(self, node: str, *, include_self: bool = False) -> tuple[str, ...]:
        self._require_node(node)
        lineage: list[str] = [node] if include_self else []
        current = self._parents[node]
        while current is not None:
            lineage.append(current)
            current = self._parents[current]
        return tuple(lineage)

    def descendants(self, node: str, *, include_self: bool = False) -> tuple[str, ...]:
        self._require_node(node)
        result: list[str] = [node] if include_self else []
        queue = deque(sorted(self._children.get(node, [])))
        while queue:
            current = queue.popleft()
            result.append(current)
            queue.extend(sorted(self._children.get(current, [])))
        return tuple(result)

    def depth(self, node: str) -> int:
        self._require_node(node)
        return len(self.ancestors(node))

    def lowest_common_ancestor(self, a: str, b: str) -> str:
        self._require_node(a)
        self._require_node(b)
        a_path = set(self.ancestors(a, include_self=True))
        current = b
        while current not in a_path:
            parent = self._parents[current]
            if parent is None:
                raise ValueError(f"no common ancestor found for {a!r}, {b!r}")
            current = parent
        return current

    def tree_distance(self, a: str, b: str) -> int:
        lca = self.lowest_common_ancestor(a, b)
        return self.depth(a) + self.depth(b) - 2 * self.depth(lca)

    def validate(self) -> LineageValidationReport:
        roots = [node for node, parent in self._parents.items() if parent is None]
        if len(roots) != 1:
            raise ValueError(f"lineage tree must have exactly one root, found {len(roots)}")
        root = roots[0]

        visited: set[str] = set()
        visiting: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ValueError(f"cycle detected at node {node!r}")
            if node in visited:
                return
            visiting.add(node)
            for child in self._children.get(node, []):
                visit(child)
            visiting.remove(node)
            visited.add(node)

        visit(root)
        unreachable = self._nodes.difference(visited)
        if unreachable:
            missing = ", ".join(sorted(unreachable))
            raise ValueError(f"unreachable lineage nodes from root {root!r}: {missing}")
        return LineageValidationReport(
            root=root,
            n_nodes=len(self._nodes),
            max_depth=max(self.depth(node) for node in self._nodes),
        )

    def _build(self) -> None:
        seen_children: set[str] = set()
        for parent, child in self._edges:
            child = str(child)
            if child in seen_children:
                raise ValueError(f"duplicate lineage node or child assignment: {child!r}")
            seen_children.add(child)
            self._nodes.add(child)
            if parent is not None:
                parent = str(parent)
                self._nodes.add(parent)
                self._children[parent].append(child)
            self._parents[child] = parent

        for parent in list(self._nodes):
            if parent not in self._parents:
                raise ValueError(f"parent node {parent!r} is referenced but never defined")

    def _require_node(self, node: str) -> None:
        if node not in self._nodes:
            raise KeyError(f"unknown lineage node: {node}")


class CellTypeLineageMapper:
    """Map canonical cell-type labels to lineage tree node identifiers."""

    def __init__(
        self,
        mapping: Mapping[str, str],
        *,
        synonyms: Mapping[str, str] | None = None,
        unknown_node: str | None = None,
        on_unknown: Literal["raise", "unknown"] = "raise",
    ) -> None:
        if on_unknown not in {"raise", "unknown"}:
            raise ValueError("on_unknown must be 'raise' or 'unknown'")
        self.mapping = {_normalize_label(key): value for key, value in mapping.items()}
        self.synonyms = {
            _normalize_label(key): _normalize_label(value)
            for key, value in (synonyms or {}).items()
        }
        self.unknown_node = unknown_node
        self.on_unknown = on_unknown
        if on_unknown == "unknown" and unknown_node is None:
            raise ValueError("unknown_node is required when on_unknown='unknown'")

    def map_one(self, cell_type: str) -> str:
        normalized = _normalize_label(cell_type)
        normalized = self.synonyms.get(normalized, normalized)
        if normalized in self.mapping:
            return self.mapping[normalized]
        if self.on_unknown == "unknown":
            return str(self.unknown_node)
        raise KeyError(f"unmapped cell type: {cell_type}")

    def map_many(self, cell_types: Iterable[str]) -> list[str]:
        return [self.map_one(cell_type) for cell_type in cell_types]

    def unmapped(self, cell_types: Iterable[str]) -> list[str]:
        missing = []
        for cell_type in cell_types:
            normalized = _normalize_label(cell_type)
            normalized = self.synonyms.get(normalized, normalized)
            if normalized not in self.mapping:
                missing.append(cell_type)
        return sorted(set(missing))


def _normalize_label(value: Any) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")
