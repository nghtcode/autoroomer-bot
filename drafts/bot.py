# import discord
# from discord.ext import commands
# from pathlib import Path
# from .utils.logger import setup_async_logger


# class Bot(commands.Bot):
#     __slots__ = ('config', 'localization', 'logger', 'cog_loggers')

#     def __init__(self, config, localization, logger):
#         intents = discord.Intents(guilds=True, messages=True, message_content=True)
#         super().__init__(command_prefix='!', intents=intents)
#         self.config = config
#         self.localization = localization
#         self.logger = logger
#         self.cog_loggers = []

#     async def setup(self):
#         await self.load_cogs()

#     async def load_cogs(self):
#         """Loading of all cogs from the src/cogs folder"""
#         for file_path in Path("/cogs").iterdir():
#             if file_path.suffix == '.py' and not file_path.name.startswith('__'):
#                 try:
#                     module = __import__(f'src.cogs.{file_path.stem}', fromlist=[''])
#                     cog_class = getattr(module, file_path.stem.capitalize(), None)
#                     if cog_class and issubclass(cog_class, commands.Cog) and cog_class is not commands.Cog:
#                         cog_logger = await setup_async_logger(f'Cog:{file_path.stem}')
#                         self.cog_loggers.append(cog_logger)
#                         await self.add_cog(cog_class(self, self.localization, self.config, cog_logger))
#                         await self.logger.info(f'Loaded cog: {file_path.stem}')
#                 except Exception as e:
#                     await self.logger.error(f'Failed to load cog {file_path.stem}: {e}')

#     async def on_ready(self):
#         await self.logger.info(f'Bot {self.user} is ready!')

#     async def close(self):
#         for cog_logger in self.cog_loggers:
#             cog_logger.stop()
#         await super().close()