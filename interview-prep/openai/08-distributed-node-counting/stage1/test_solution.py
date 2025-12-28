"""Tests for Distributed Node Counting Stage 1"""
import pytest
from solution import NodeCounter


class TestNodeCounterStage1:
    def test_register(self):
        nc = NodeCounter()
        assert nc.register("node1", "192.168.1.1") is True
        assert nc.count() == 1

    def test_register_duplicate(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        assert nc.register("node1", "192.168.1.2") is False

    def test_unregister(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        assert nc.unregister("node1") is True
        assert nc.count() == 0

    def test_unregister_nonexistent(self):
        nc = NodeCounter()
        assert nc.unregister("missing") is False

    def test_get_node(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        info = nc.get_node("node1")
        assert info is not None
        assert info.address == "192.168.1.1"

    def test_list_nodes(self):
        nc = NodeCounter()
        nc.register("node2", "192.168.1.2")
        nc.register("node1", "192.168.1.1")
        assert nc.list_nodes() == ["node1", "node2"]

    def test_is_registered(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        assert nc.is_registered("node1") is True
        assert nc.is_registered("missing") is False

    def test_clear(self):
        nc = NodeCounter()
        nc.register("node1", "192.168.1.1")
        nc.register("node2", "192.168.1.2")
        nc.clear()
        assert nc.count() == 0
