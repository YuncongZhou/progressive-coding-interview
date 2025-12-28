"""Tests for Resumable Iterator Stage 1"""
import pytest
from solution import ResumableIterator


class TestResumableIteratorStage1:
    def test_iterate_through_list(self):
        it = ResumableIterator([1, 2, 3])
        assert next(it) == 1
        assert next(it) == 2
        assert next(it) == 3
        with pytest.raises(StopIteration):
            next(it)

    def test_save_and_restore_state(self):
        it = ResumableIterator([1, 2, 3, 4, 5])
        assert next(it) == 1
        assert next(it) == 2

        state = it.get_state()

        # Create new iterator and restore state
        new_it = ResumableIterator([1, 2, 3, 4, 5])
        new_it.set_state(state)

        assert next(new_it) == 3
        assert next(new_it) == 4
        assert next(new_it) == 5

    def test_state_at_beginning(self):
        it = ResumableIterator([1, 2, 3])
        state = it.get_state()

        new_it = ResumableIterator([1, 2, 3])
        new_it.set_state(state)
        assert next(new_it) == 1

    def test_state_at_end(self):
        it = ResumableIterator([1, 2])
        next(it)
        next(it)
        state = it.get_state()

        new_it = ResumableIterator([1, 2])
        new_it.set_state(state)
        with pytest.raises(StopIteration):
            next(new_it)

    def test_empty_list(self):
        it = ResumableIterator([])
        with pytest.raises(StopIteration):
            next(it)

    def test_for_loop(self):
        it = ResumableIterator([1, 2, 3])
        result = list(it)
        assert result == [1, 2, 3]
