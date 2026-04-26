from repositories.postgres import PostgresRepository


class UnifiedBalanceService:
    def __init__(self, repository: PostgresRepository):
        self.repository = repository

    async def bootstrap_user(self, user_id: int, username: str | None, full_name: str | None):
        await self.repository.ensure_schema()
        await self.repository.ensure_user(user_id, username, full_name)

    async def get_balance(self, user_id: int) -> int:
        return await self.repository.get_balance(user_id)

    async def charge(self, user_id: int, amount: int, provider: str, reference: str = "") -> bool:
        return await self.repository.reserve_balance(user_id, amount, provider, reference)

    async def refund(self, user_id: int, amount: int, provider: str, reference: str = "") -> int:
        return await self.repository.refund_balance(user_id, amount, provider, reference)

    async def top_up(self, user_id: int, amount: int, provider: str = "manual", reference: str = "") -> int:
        return await self.repository.add_balance(user_id, amount, provider, reference)

    async def record_order(
        self,
        user_id: int,
        provider: str,
        external_id: str,
        title: str,
        target: str,
        amount: int,
        status: str = "pending",
    ) -> int:
        return await self.repository.create_order(
            user_id=user_id,
            provider=provider,
            external_id=external_id,
            title=title,
            target=target,
            amount=amount,
            status=status,
        )
