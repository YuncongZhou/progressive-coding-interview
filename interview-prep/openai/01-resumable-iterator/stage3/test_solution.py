"""Tests for Resumable Iterator Stage 3 - Async"""
import pytest
from solution import AsyncResumableIterator


class TestAsyncResumableIterator:
    @pytest.mark.asyncio
    async def test_async_iteration(self):
        it = AsyncResumableIterator([1, 2, 3])
        result = []
        async for item in it:
            result.append(item)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_async_save_restore_state(self):
        it = AsyncResumableIterator([1, 2, 3, 4, 5])
        assert await it.__anext__() == 1
        assert await it.__anext__() == 2

        state = await it.get_state()

        new_it = AsyncResumableIterator([1, 2, 3, 4, 5])
        await new_it.set_state(state)

        result = []
        async for item in new_it:
            result.append(item)
        assert result == [3, 4, 5]

    @pytest.mark.asyncio
    async def test_async_empty_list(self):
        it = AsyncResumableIterator([])
        result = []
        async for item in it:
            result.append(item)
        assert result == []
