from typing import Any

try:
    import asyncpg
except ImportError:  # pragma: no cover - optional dependency during scaffolding
    asyncpg = None


def _coerce_money(amount: Any) -> int:
    try:
        return int(round(float(amount)))
    except (TypeError, ValueError):
        return 0


class PostgresRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool = None

    async def connect(self):
        if asyncpg is None:
            raise RuntimeError("asyncpg is not installed. Add it to requirements and install dependencies.")
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)
        return self._pool

    async def close(self):
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def ensure_schema(self):
        pool = await self.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance BIGINT NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS balance_transactions (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    amount BIGINT NOT NULL,
                    direction TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    reference TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS provider_orders (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL,
                    target TEXT NOT NULL DEFAULT '',
                    amount BIGINT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )

    async def ensure_user(self, user_id: int, username: str | None = None, full_name: str | None = None):
        pool = await self.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET username = COALESCE(EXCLUDED.username, users.username),
                    full_name = COALESCE(EXCLUDED.full_name, users.full_name)
                """,
                user_id,
                username,
                full_name,
            )

    async def get_user(self, user_id: int):
        pool = await self.connect()
        async with pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

    async def get_balance(self, user_id: int) -> int:
        row = await self.get_user(user_id)
        return int(row["balance"]) if row else 0

    async def add_balance(self, user_id: int, amount: int, provider: str, reference: str = "") -> int:
        amount = _coerce_money(amount)
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """
                    UPDATE users
                    SET balance = balance + $1
                    WHERE user_id = $2
                    RETURNING balance
                    """,
                    amount,
                    user_id,
                )
                await conn.execute(
                    """
                    INSERT INTO balance_transactions (user_id, amount, direction, provider, reference)
                    VALUES ($1, $2, 'credit', $3, $4)
                    """,
                    user_id,
                    amount,
                    provider,
                    reference,
                )
        return int(row["balance"]) if row else 0

    async def reserve_balance(self, user_id: int, amount: int, provider: str, reference: str = "") -> bool:
        amount = _coerce_money(amount)
        pool = await self.connect()
        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """
                    UPDATE users
                    SET balance = balance - $1
                    WHERE user_id = $2 AND balance >= $1
                    RETURNING balance
                    """,
                    amount,
                    user_id,
                )
                if row is None:
                    return False
                await conn.execute(
                    """
                    INSERT INTO balance_transactions (user_id, amount, direction, provider, reference)
                    VALUES ($1, $2, 'debit', $3, $4)
                    """,
                    user_id,
                    amount,
                    provider,
                    reference,
                )
        return True

    async def refund_balance(self, user_id: int, amount: int, provider: str, reference: str = "") -> int:
        return await self.add_balance(user_id, amount, provider, reference)

    async def create_order(
        self,
        user_id: int,
        provider: str,
        external_id: str,
        title: str,
        target: str,
        amount: int,
        status: str = "pending",
    ) -> int:
        amount = _coerce_money(amount)
        pool = await self.connect()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO provider_orders (user_id, provider, external_id, title, target, amount, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                user_id,
                provider,
                external_id,
                title,
                target,
                amount,
                status,
            )
        return int(row["id"])
