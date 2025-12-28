"""Tests for Distributed Node Counting Stage 3 - Sharding"""
import pytest
from solution import NodeCounter


class TestNodeCounterStage3:
    def test_auto_shard_assignment(self):
        nc = NodeCounter(num_shards=4)
        nc.register("node1", "192.168.1.1")

        shard = nc.get_shard("node1")
        assert shard is not None
        assert 0 <= shard < 4

    def test_manual_shard_assignment(self):
        nc = NodeCounter(num_shards=4)
        nc.register("node1", "192.168.1.1", shard=2)

        assert nc.get_shard("node1") == 2

    def test_count_by_shard(self):
        nc = NodeCounter(num_shards=2)
        nc.register("node1", "192.168.1.1", shard=0)
        nc.register("node2", "192.168.1.2", shard=0)
        nc.register("node3", "192.168.1.3", shard=1)

        counts = nc.count_by_shard()
        assert counts[0] == 2
        assert counts[1] == 1

    def test_list_shard(self):
        nc = NodeCounter(num_shards=2)
        nc.register("node1", "192.168.1.1", shard=0)
        nc.register("node2", "192.168.1.2", shard=0)
        nc.register("node3", "192.168.1.3", shard=1)

        nodes = nc.list_shard(0)
        assert "node1" in nodes
        assert "node2" in nodes
        assert "node3" not in nodes

    def test_unregister_updates_shard(self):
        nc = NodeCounter(num_shards=2)
        nc.register("node1", "192.168.1.1", shard=0)
        nc.unregister("node1")

        assert nc.list_shard(0) == []

    def test_rebalance(self):
        nc = NodeCounter(num_shards=2)
        # Put all in shard 0
        nc.register("node1", "192.168.1.1", shard=0)
        nc.register("node2", "192.168.1.2", shard=0)
        nc.register("node3", "192.168.1.3", shard=0)
        nc.register("node4", "192.168.1.4", shard=0)

        moves = nc.rebalance()
        counts = nc.count_by_shard()

        assert moves > 0
        assert counts[0] == 2
        assert counts[1] == 2

    def test_consistent_shard_assignment(self):
        nc1 = NodeCounter(num_shards=4)
        nc2 = NodeCounter(num_shards=4)

        nc1.register("node1", "192.168.1.1")
        nc2.register("node1", "192.168.1.1")

        # Same node ID should get same shard
        assert nc1.get_shard("node1") == nc2.get_shard("node1")
