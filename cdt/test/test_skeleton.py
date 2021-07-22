import pytest

from cdt.test import setup as setup_test

class TestSomething:
    @pytest.fixture(scope="function")
    async def setup(self):
        network, alice, bob = await setup_test()
        yield network, alice, bob

    @pytest.mark.asyncio
    async def test_something(self, setup):
        network, alice, bob = setup
        try:
            pass
        finally:
            await network.close()
