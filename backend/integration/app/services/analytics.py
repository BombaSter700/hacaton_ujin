import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
import clickhouse_connect
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnalyticsWriter:
    def __init__(self):
        self.queue = asyncio.Queue(maxsize=10000)
        self.is_running = False
        self.client = None

    def connect(self):
        """Синхронное подключение при старте"""
        try:
            self.client = clickhouse_connect.get_client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                username=settings.clickhouse_user,
                password=settings.clickhouse_password,
                database=settings.clickhouse_db,
                connect_timeout=5
            )
            logger.info("Connected to ClickHouse")
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")

    async def start(self):
        """Запуск фонового цикла"""
        self.is_running = True
        self.task = asyncio.create_task(self._flush_loop())

    async def stop(self):
        """Остановка и финальный сброс"""
        self.is_running = False
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
        await self._flush_batch()
        if self.client:
            self.client.close()

    def log_event(self, table: str, data: Dict[str, Any]):
        """Добавляем событие в очередь (не блокирует запрос)"""
        try:
            self.queue.put_nowait((table, data))
        except asyncio.QueueFull:
            logger.error("ClickHouse queue is full! Dropping event.")

    async def _flush_loop(self):
        """Бесконечный цикл записи батчами"""
        while self.is_running:
            await asyncio.sleep(1.0) # Собираем данные раз в секунду
            await self._flush_batch()

    async def _flush_batch(self):
        """Забирает всё из очереди и пишет в ClickHouse"""
        if self.queue.empty() or not self.client:
            return

        batches: Dict[str, List[Dict]] = {}

        # Забираем максимум 1000 элементов за раз
        for _ in range(min(1000, self.queue.qsize())):
            try:
                table, data = self.queue.get_nowait()
                if table not in batches:
                    batches[table] = []
                batches[table].append(data)
            except asyncio.QueueEmpty:
                break

        for table, rows in batches.items():
            try:
                # ClickHouse-connect синхронный, запускаем в отдельном потоке
                await asyncio.to_thread(
                    self.client.insert,
                    table,
                    [[row.get(key) for key in rows[0]] for row in rows],
                    column_names=list(rows[0].keys())
                )
                logger.debug(f"Inserted {len(rows)} rows into {table}")
            except Exception as e:
                logger.error(f"Failed to insert into {table}: {e}")

# Глобальный экземпляр
analytics = AnalyticsWriter()
