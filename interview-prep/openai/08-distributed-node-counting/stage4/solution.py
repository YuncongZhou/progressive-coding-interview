"""
Distributed Node Counting - Stage 4

Leader election and consensus.

Design Rationale:
- Elect leader among nodes
- Handle leader failover
- Track leader history
"""

from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field
import time
import hashlib
import random


@dataclass
class NodeInfo:
    node_id: str
    address: str
    registered_at: float
    last_heartbeat: float
    healthy: bool = True
    shard: Optional[int] = None
    priority: int = 0  # Higher = more likely to be leader


@dataclass
class LeaderHistory:
    node_id: str
    elected_at: float
    ended_at: Optional[float] = None


class NodeCounter:
    """Node counter with leader election."""

    def __init__(self, num_shards: int = 4, heartbeat_timeout: float = 30.0):
        self._nodes: dict[str, NodeInfo] = {}
        self._num_shards = num_shards
        self._heartbeat_timeout = heartbeat_timeout
        self._shard_nodes: dict[int, Set[str]] = {i: set() for i in range(num_shards)}
        self._leader: Optional[str] = None
        self._leader_history: List[LeaderHistory] = []

    def _compute_shard(self, node_id: str) -> int:
        h = int(hashlib.md5(node_id.encode()).hexdigest(), 16)
        return h % self._num_shards

    def register(self, node_id: str, address: str,
                 priority: int = 0, shard: Optional[int] = None) -> bool:
        if node_id in self._nodes:
            return False

        now = time.time()
        if shard is None:
            shard = self._compute_shard(node_id)

        self._nodes[node_id] = NodeInfo(
            node_id=node_id,
            address=address,
            registered_at=now,
            last_heartbeat=now,
            healthy=True,
            shard=shard,
            priority=priority
        )
        self._shard_nodes[shard].add(node_id)

        # Auto-elect if no leader
        if self._leader is None:
            self._elect_leader()

        return True

    def unregister(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        info = self._nodes.pop(node_id)
        if info.shard is not None:
            self._shard_nodes[info.shard].discard(node_id)

        # Re-elect if leader left
        if self._leader == node_id:
            self._end_leader_term()
            self._elect_leader()

        return True

    def heartbeat(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        self._nodes[node_id].last_heartbeat = time.time()
        self._nodes[node_id].healthy = True
        return True

    def check_health(self) -> List[str]:
        now = time.time()
        unhealthy = []
        for node_id, info in self._nodes.items():
            if now - info.last_heartbeat > self._heartbeat_timeout:
                info.healthy = False
                unhealthy.append(node_id)
            else:
                info.healthy = True

        # Check if leader is unhealthy
        if self._leader and not self._nodes.get(self._leader, NodeInfo("", "", 0, 0)).healthy:
            self._end_leader_term()
            self._elect_leader()

        return unhealthy

    def _elect_leader(self) -> Optional[str]:
        """Elect a leader from healthy nodes."""
        healthy_nodes = [(nid, info) for nid, info in self._nodes.items()
                        if info.healthy]
        if not healthy_nodes:
            self._leader = None
            return None

        # Sort by priority (desc), then by ID for determinism
        healthy_nodes.sort(key=lambda x: (-x[1].priority, x[0]))
        new_leader = healthy_nodes[0][0]

        self._leader = new_leader
        self._leader_history.append(LeaderHistory(
            node_id=new_leader,
            elected_at=time.time()
        ))
        return new_leader

    def _end_leader_term(self) -> None:
        """End current leader's term."""
        if self._leader_history and self._leader_history[-1].ended_at is None:
            self._leader_history[-1].ended_at = time.time()
        self._leader = None

    def get_leader(self) -> Optional[str]:
        """Get current leader."""
        return self._leader

    def is_leader(self, node_id: str) -> bool:
        """Check if node is the leader."""
        return self._leader == node_id

    def force_election(self) -> Optional[str]:
        """Force a new leader election."""
        self._end_leader_term()
        return self._elect_leader()

    def get_leader_history(self) -> List[LeaderHistory]:
        """Get leader election history."""
        return self._leader_history.copy()

    def count(self) -> int:
        return len(self._nodes)

    def count_by_shard(self) -> Dict[int, int]:
        return {shard: len(nodes) for shard, nodes in self._shard_nodes.items()}

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        return sorted(self._nodes.keys())

    def list_healthy(self) -> list[str]:
        self.check_health()
        return sorted(nid for nid, info in self._nodes.items() if info.healthy)
