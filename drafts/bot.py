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




# class Autoroomer(commands.Cog):
#     __slots__ = ('bot', 'room_states', '_channel_cache', 'localization', 'config', 'logger')
    
#     def __init__(self, bot: commands.Bot, localization, config, logger):
#         self.bot = bot
#         self.room_states: Dict[int, RoomState] = {}
#         self.localization = localization
#         self.config = config
#         self.logger = logger

#     @commands.Cog.listener()
#     async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
#         channel_limits = {
#             self.config.voice_1: 2,
#             self.config.voice_2: 3,
#             self.config.voice_3: 4
#         }

#         try:
#             # BEFORE CHANNEL
#             if before.channel and before.channel.category_id in [self.config.category_filled, self.config.category_find]:
#                 message = self.bot.get_channel(self.config.text_channel_id)
#                 state = self.room_states[before.channel.id]
#                 if before.channel.category_id == self.config.category_filled and len(before.channel.members) < before.channel.user_limit:
#                     category = discord.utils.get(before.channel.guild.categories, id=self.config.category_find)
#                     await before.channel.edit(category=category)
#                     if before.channel.members:
#                         #state = self.room_states[before.channel.id]
#                         await Message.create_message(self.logger, self.localization, before.channel, state, message)
                
#                 # msg = await message.fetch_message(state.message_id)
#                 if not before.channel.members:
#                     msg = await message.fetch_message(state.message_id)
#                     await msg.delete()
#                     del self.room_states[before.channel.id]
#                     await before.channel.delete()
                
#                 elif before.channel.id in self.room_states:
#                     #state = self.room_states[before.channel.id]
#                     msg = await message.fetch_message(state.message_id)
#                     await Message.update_participants_message(self.logger, self.localization, before.channel, state, msg)
            
#             # AFTER CHANNEL
#             if after.channel and after.channel.category_id == self.config.category_create_room and after.channel.id in channel_limits:
#                 await CreateRoom.create_room(self.logger, self.config.category_find, self.room_states, channel_limits[after.channel.id], member)
            
#             elif after.channel and after.channel.category_id in [self.config.category_filled, self.config.category_find]:
#                 if after.channel.id in self.room_states:
#                     message = self.bot.get_channel(self.config.text_channel_id)
#                     state = self.room_states[after.channel.id]
#                     if after.channel.category_id != self.config.category_filled and len(after.channel.members) == after.channel.user_limit:
#                         if after.channel.id in self.room_states:
#                             msg_dlt = await message.fetch_message(self.room_states[after.channel.id].message_id)
#                             await msg_dlt.delete()
#                         category = discord.utils.get(after.channel.guild.categories, id=self.config.category_filled)
#                         await after.channel.edit(category=category)
#                     elif state.value == 0:
#                         print("0")
#                         await Message.create_message(self.logger, self.localization, after.channel, state, message)
#                     elif state.value == 1:
#                         print("1")
#                         msg_updt = await message.fetch_message(state.message_id)
#                         await Message.update_participants_message(self.logger, self.localization, after.channel, state, msg_updt)
                
#                 # if after.channel.category_id != self.config.category_filled and len(after.channel.members) == after.channel.user_limit:
#                 #     message = self.bot.get_channel(self.config.text_channel_id)
#                 #     if after.channel.id in self.room_states:
#                 #         msg_dlt = await message.fetch_message(self.room_states[after.channel.id].message_id)
#                 #         await msg_dlt.delete()
#                 #     category = discord.utils.get(after.channel.guild.categories, id=self.config.category_filled)
#                 #     await after.channel.edit(category=category)
        
#         except Exception as e:
#             await self.logger.error(f"❌ Error in voice state update: {e}")