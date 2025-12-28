"""
Distributed Node Counting - Stage 2

Heartbeats and health checking.

Design Rationale:
- Track last heartbeat time
- Mark nodes as unhealthy
- Auto-remove dead nodes
"""

from typing import Optional, List
from dataclasses import dataclass
import time


@dataclass
class NodeInfo:
    node_id: str
    address: str
    registered_at: float
    last_heartbeat: float
    healthy: bool = True


class NodeCounter:
    """Node counter with health tracking."""

    def __init__(self, heartbeat_timeout: float = 30.0):
        self._nodes: dict[str, NodeInfo] = {}
        self._heartbeat_timeout = heartbeat_timeout

    def register(self, node_id: str, address: str) -> bool:
        if node_id in self._nodes:
            return False
        now = time.time()
        self._nodes[node_id] = NodeInfo(
            node_id=node_id,
            address=address,
            registered_at=now,
            last_heartbeat=now,
            healthy=True
        )
        return True

    def unregister(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        return True

    def heartbeat(self, node_id: str) -> bool:
        """Record heartbeat from node."""
        if node_id not in self._nodes:
            return False
        self._nodes[node_id].last_heartbeat = time.time()
        self._nodes[node_id].healthy = True
        return True

    def check_health(self) -> List[str]:
        """Check all nodes and mark unhealthy ones. Returns unhealthy IDs."""
        now = time.time()
        unhealthy = []

        for node_id, info in self._nodes.items():
            if now - info.last_heartbeat > self._heartbeat_timeout:
                info.healthy = False
                unhealthy.append(node_id)
            else:
                info.healthy = True

        return unhealthy

    def remove_unhealthy(self) -> int:
        """Remove all unhealthy nodes. Returns count removed."""
        self.check_health()
        unhealthy = [nid for nid, info in self._nodes.items() if not info.healthy]
        for node_id in unhealthy:
            del self._nodes[node_id]
        return len(unhealthy)

    def count(self) -> int:
        return len(self._nodes)

    def count_healthy(self) -> int:
        """Count only healthy nodes."""
        self.check_health()
        return sum(1 for info in self._nodes.values() if info.healthy)

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        return self._nodes.get(node_id)

    def is_healthy(self, node_id: str) -> bool:
        """Check if specific node is healthy."""
        self.check_health()
        node = self._nodes.get(node_id)
        return node.healthy if node else False

    def list_nodes(self) -> list[str]:
        return sorted(self._nodes.keys())

    def list_healthy(self) -> list[str]:
        """List only healthy nodes."""
        self.check_health()
        return sorted(nid for nid, info in self._nodes.items() if info.healthy)
