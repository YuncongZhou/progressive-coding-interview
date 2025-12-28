"""
Distributed Node Counting - Stage 3

Sharding and partitions.

Design Rationale:
- Assign nodes to shards
- Track partition membership
- Balance across partitions
"""

from typing import Optional, List, Dict, Set
from dataclasses import dataclass, field
import time
import hashlib


@dataclass
class NodeInfo:
    node_id: str
    address: str
    registered_at: float
    last_heartbeat: float
    healthy: bool = True
    shard: Optional[int] = None


class NodeCounter:
    """Node counter with sharding support."""

    def __init__(self, num_shards: int = 4, heartbeat_timeout: float = 30.0):
        self._nodes: dict[str, NodeInfo] = {}
        self._num_shards = num_shards
        self._heartbeat_timeout = heartbeat_timeout
        self._shard_nodes: dict[int, Set[str]] = {i: set() for i in range(num_shards)}

    def _compute_shard(self, node_id: str) -> int:
        """Compute shard using consistent hashing."""
        h = int(hashlib.md5(node_id.encode()).hexdigest(), 16)
        return h % self._num_shards

    def register(self, node_id: str, address: str,
                 shard: Optional[int] = None) -> bool:
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
            shard=shard
        )
        self._shard_nodes[shard].add(node_id)
        return True

    def unregister(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        info = self._nodes.pop(node_id)
        if info.shard is not None:
            self._shard_nodes[info.shard].discard(node_id)
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
        return unhealthy

    def count(self) -> int:
        return len(self._nodes)

    def count_by_shard(self) -> Dict[int, int]:
        """Count nodes per shard."""
        return {shard: len(nodes) for shard, nodes in self._shard_nodes.items()}

    def get_shard(self, node_id: str) -> Optional[int]:
        """Get node's shard."""
        info = self._nodes.get(node_id)
        return info.shard if info else None

    def list_shard(self, shard: int) -> List[str]:
        """List nodes in shard."""
        return sorted(self._shard_nodes.get(shard, set()))

    def rebalance(self) -> int:
        """Rebalance nodes across shards. Returns moves made."""
        counts = self.count_by_shard()
        avg = len(self._nodes) / self._num_shards
        moves = 0

        # Move from over-populated to under-populated
        for shard in range(self._num_shards):
            while len(self._shard_nodes[shard]) > avg + 1:
                # Find under-populated shard
                target = min(range(self._num_shards),
                            key=lambda s: len(self._shard_nodes[s]))
                if len(self._shard_nodes[target]) >= avg:
                    break

                # Move one node
                node_id = next(iter(self._shard_nodes[shard]))
                self._shard_nodes[shard].remove(node_id)
                self._shard_nodes[target].add(node_id)
                self._nodes[node_id].shard = target
                moves += 1

        return moves

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        return self._nodes.get(node_id)

    def list_nodes(self) -> list[str]:
        return sorted(self._nodes.keys())
