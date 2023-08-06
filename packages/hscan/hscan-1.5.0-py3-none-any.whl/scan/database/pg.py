import asyncpg
from scan.common import logger


class Postgresql:
    def __init__(self, host, port, user, database, password, min_size=10, max_size=10, **kwargs):
        self._pool = None
        self.host = host
        self.port = port
        self.user = user
        self.database = database
        self.password = password
        self.min_size = min_size
        self.max_size = max_size

    async def _create_pool(self):
        try:
            dsn = f'postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'
            self._pool = await asyncpg.create_pool(dsn=dsn, min_size=self.min_size, max_size=self.max_size,
                                                   command_timeout=60)
        except Exception as e:
            await logger.error(f'create pool error: {e}')

    async def get_pool(self):
        if not self._pool:
            await self._create_pool()
        return self._pool


__all__ = Postgresql


