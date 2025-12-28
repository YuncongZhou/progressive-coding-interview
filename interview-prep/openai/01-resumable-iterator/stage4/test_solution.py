"""Tests for Resumable Iterator Stage 4 - 2D and 3D"""
import pytest
from solution import Resumable2DIterator, Resumable3DIterator


class TestResumable2DIterator:
    def test_iterate_2d(self):
        it = Resumable2DIterator([[1, 2], [3, 4, 5], [6]])
        result = list(it)
        assert result == [1, 2, 3, 4, 5, 6]

    def test_2d_with_empty_rows(self):
        it = Resumable2DIterator([[1, 2], [], [3, 4]])
        result = list(it)
        assert result == [1, 2, 3, 4]

    def test_2d_save_restore(self):
        it = Resumable2DIterator([[1, 2], [3, 4, 5], [6]])
        next(it)  # 1
        next(it)  # 2
        next(it)  # 3

        state = it.get_state()

        new_it = Resumable2DIterator([[1, 2], [3, 4, 5], [6]])
        new_it.set_state(state)
        result = list(new_it)
        assert result == [4, 5, 6]

    def test_2d_empty(self):
        it = Resumable2DIterator([])
        result = list(it)
        assert result == []


class TestResumable3DIterator:
    def test_iterate_3d(self):
        data = [[[1, 2], [3]], [[4, 5, 6]]]
        it = Resumable3DIterator(data)
        result = list(it)
        assert result == [1, 2, 3, 4, 5, 6]

    def test_3d_with_empty_inner(self):
        data = [[[1], []], [[2, 3]]]
        it = Resumable3DIterator(data)
        result = list(it)
        assert result == [1, 2, 3]

    def test_3d_save_restore(self):
        data = [[[1, 2], [3, 4]], [[5, 6]]]
        it = Resumable3DIterator(data)
        next(it)  # 1
        next(it)  # 2
        next(it)  # 3

        state = it.get_state()

        new_it = Resumable3DIterator(data)
        new_it.set_state(state)
        result = list(new_it)
        assert result == [4, 5, 6]
