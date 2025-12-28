"""Tests for Distributed Node Counting Stage 2 - Health Checking"""
import pytest
import time
from solution import NodeCounter


class TestNodeCounterStage2:
    def test_heartbeat(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        assert nc.heartbeat("node1") is True

    def test_heartbeat_nonexistent(self):
        nc = NodeCounter()
        assert nc.heartbeat("missing") is False

    def test_check_health_timeout(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        time.sleep(0.15)

        unhealthy = nc.check_health()
        assert "node1" in unhealthy
        assert nc.is_healthy("node1") is False

    def test_check_health_with_heartbeat(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        time.sleep(0.05)
        nc.heartbeat("node1")
        time.sleep(0.05)

        unhealthy = nc.check_health()
        assert "node1" not in unhealthy

    def test_count_healthy(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")
        time.sleep(0.15)
        nc.heartbeat("node1")

        assert nc.count() == 2
        assert nc.count_healthy() == 1

    def test_remove_unhealthy(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")
        time.sleep(0.15)
        nc.heartbeat("node1")

        removed = nc.remove_unhealthy()
        assert removed == 1
        assert nc.count() == 1
        assert nc.is_registered("node1") is True
        assert nc.is_registered("node2") is False

    def test_list_healthy(self):
        nc = NodeCounter(heartbeat_timeout=0.1)
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")
        time.sleep(0.15)
        nc.heartbeat("node1")

        healthy = nc.list_healthy()
        assert healthy == ["node1"]

    def test_is_registered(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        assert nc.is_registered("node1") is True
        assert nc.is_registered("missing") is False
