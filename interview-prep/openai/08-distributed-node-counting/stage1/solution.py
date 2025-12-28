"""
Distributed Node Counting - Stage 1

Count nodes in a distributed system.

Design Rationale:
- Track nodes by ID
- Simple register/unregister
- Count active nodes
"""

from typing import Optional, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NodeInfo:
    node_id: str
    address: str
    registered_at: float


class NodeCounter:
    """Count nodes in distributed system."""

    def __init__(self):
        self._nodes: dict[str, NodeInfo] = {}

    def register(self, node_id: str, address: str) -> bool:
        """Register a node. Returns True if new."""
        if node_id in self._nodes:
            return False
        self._nodes[node_id] = NodeInfo(
            node_id=node_id,
            address=address,
            registered_at=datetime.now().timestamp()
        )
        return True

    def unregister(self, node_id: str) -> bool:
        """Unregister a node. Returns True if existed."""
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        return True

    def count(self) -> int:
        """Count active nodes."""
        return len(self._nodes)

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        """Get node info."""
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        """List all node IDs."""
        return sorted(self._nodes.keys())

    def is_registered(self, node_id: str) -> bool:
        """Check if node is registered."""
        return node_id in self._nodes

    def clear(self) -> None:
        """Unregister all nodes."""
        self._nodes.clear()
