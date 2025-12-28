"""Tests for Distributed Node Counting Stage 4 - Leader Election"""
import pytest
import time
from solution import NodeCounter


class TestNodeCounterStage4:
    def test_auto_elect_first_node(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")

        assert nc.get_leader() == "node1"
        assert nc.is_leader("node1") is True

    def test_leader_persists(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")

        # Leader should still be node1
        assert nc.get_leader() == "node1"

    def test_priority_election(self):
        nc = NodeCounter()
        nc.register("low", "192.168.1.1", priority=1)
        nc.register("high", "192.168.1.2", priority=10)

        nc.force_election()
        assert nc.get_leader() == "high"

    def test_leader_failover(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")

        assert nc.get_leader() == "node1"

        # Let node1 become unhealthy
        time.sleep(0.15)
        nc.heartbeat("node2")
        nc.check_health()

        # node2 should be new leader
        assert nc.get_leader() == "node2"

    def test_leader_unregister(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")

        assert nc.get_leader() == "node1"

        nc.unregister("node1")
        assert nc.get_leader() == "node2"

    def test_leader_history(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")

        nc.force_election()

        history = nc.get_leader_history()
        assert len(history) >= 1

    def test_no_leader_when_empty(self):
        nc = NodeCounter()
        assert nc.get_leader() is None

    def test_force_election(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1", priority=1)
        nc.register("node2", "192.168.1.2", priority=2)

        # Initially node1 (first registered)
        nc.force_election()

        # After force election, highest priority wins
        assert nc.get_leader() == "node2"

    def test_is_leader(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")

        assert nc.is_leader("node1") is True
        assert nc.is_leader("node2") is False
