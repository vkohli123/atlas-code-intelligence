import asyncio

class ProviderRouter:
    def __init__(self, provider_order: list[str]):
        self.provider_order = provider_order

    async def complete(self, payload: dict):
        last_error = None
        for provider in self.provider_order:
            try:
                return await self._call_provider(provider, payload)
            except TimeoutError as exc:
                last_error = exc
                continue
        raise RuntimeError(f"all providers failed: {last_error}")

    async def _call_provider(self, provider: str, payload: dict):
        await asyncio.sleep(0.01)
        return {"provider": provider, "message": "mock completion"}
