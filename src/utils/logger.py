import logging
import sys
import asyncio

class AsyncLogger:
    __slots__ = ('logger', 'queue', 'handler', '_running', '_task')
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.queue = asyncio.Queue()
        self._task = None
        
        if not self.logger.handlers:
            self.handler = logging.StreamHandler(sys.stdout)
            self.handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(self.handler)
        
        self._running = False

    async def log(self, level: int, message: str):
        """Asynchronously adds a message to the log queue"""
        await self.queue.put((level, message))

    async def info(self, message: str):
        """Asynchronous method for INFO level logs"""
        await self.log(logging.INFO, message)

    async def error(self, message: str):
        """Asynchronous method for ERROR level logs"""
        await self.log(logging.ERROR, message)
    
    async def process_logs(self):
        """Processes messages from the log queue"""
        self._running = True
        while self._running:
            try:
                level, message = await self.queue.get()
                self.logger.log(level, message)
                self.queue.task_done()
            except asyncio.CancelledError:
                self._running = False
                break

    def stop(self):
        """Stops processing logs"""
        self._running = False
        if self._task:
            self._task.cancel()
        self.logger.handlers.clear()
        print(f"❌ {self.logger.name} has been stopped")

async def setup_async_logger(name: str) -> AsyncLogger:
    """Creates and returns an asynchronous logger"""
    logger = AsyncLogger(name)
    logger._task = asyncio.create_task(logger.process_logs())
    return logger