"""Tests for Resumable Iterator Stage 2"""
import pytest
import json
import tempfile
import os
from solution import JsonFileIterator, MultipleJsonFileIterator


class TestJsonFileIterator:
    def test_iterate_json_file(self, tmp_path):
        filepath = tmp_path / "data.json"
        filepath.write_text(json.dumps([1, 2, 3]))

        it = JsonFileIterator(str(filepath))
        result = list(it)
        assert result == [1, 2, 3]

    def test_save_restore_state(self, tmp_path):
        filepath = tmp_path / "data.json"
        filepath.write_text(json.dumps([1, 2, 3, 4, 5]))

        it = JsonFileIterator(str(filepath))
        next(it)
        next(it)
        state = it.get_state()

        new_it = JsonFileIterator(str(filepath))
        new_it.set_state(state)
        assert list(new_it) == [3, 4, 5]


class TestMultipleJsonFileIterator:
    def test_iterate_multiple_files(self, tmp_path):
        f1 = tmp_path / "a.json"
        f2 = tmp_path / "b.json"
        f1.write_text(json.dumps([1, 2]))
        f2.write_text(json.dumps([3, 4]))

        it = MultipleJsonFileIterator([str(f1), str(f2)])
        result = list(it)
        assert result == [1, 2, 3, 4]

    def test_skip_empty_files(self, tmp_path):
        f1 = tmp_path / "a.json"
        f2 = tmp_path / "b.json"
        f3 = tmp_path / "c.json"
        f1.write_text(json.dumps([1, 2]))
        f2.write_text(json.dumps([]))
        f3.write_text(json.dumps([3, 4]))

        it = MultipleJsonFileIterator([str(f1), str(f2), str(f3)])
        result = list(it)
        assert result == [1, 2, 3, 4]

    def test_save_restore_state(self, tmp_path):
        f1 = tmp_path / "a.json"
        f2 = tmp_path / "b.json"
        f1.write_text(json.dumps([1, 2]))
        f2.write_text(json.dumps([3, 4, 5]))

        it = MultipleJsonFileIterator([str(f1), str(f2)])
        next(it)  # 1
        next(it)  # 2
        next(it)  # 3
        state = it.get_state()

        new_it = MultipleJsonFileIterator([str(f1), str(f2)])
        new_it.set_state(state)
        assert list(new_it) == [4, 5]
