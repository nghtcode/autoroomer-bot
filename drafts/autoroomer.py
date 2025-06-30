# import asyncio
# import discord
# from discord.ext import commands
# from typing import Dict
# from ..utils.func import RoomState, CreateRoom, Message


# class Autoroomer(commands.Cog):
#     __slots__ = ('bot', 'room_states', '_channel_cache', 'localization', 'config', 'logger')
    
#     def __init__(self, bot: commands.Bot, localization, config, logger):
#         self.bot = bot
#         self.room_states: Dict[int, RoomState] = {}
#         self.localization = localization
#         self.config = config
#         self.logger = logger
#         self._lock = asyncio.Lock()

#     @commands.Cog.listener()
#     async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
#         channel_limits = {
#             self.config.voice_1: 2,
#             self.config.voice_2: 3,
#             self.config.voice_3: 4
#         }

#         async with self._lock:
#             try:
#                 # BEFORE CHANNEL
#                 if before.channel and before.channel.category_id in [self.config.category_filled, self.config.category_find]:
#                     message = self.bot.get_channel(self.config.text_channel_id)
#                     if before.channel.id not in self.room_states:
#                         await self.logger.error(f"❌ Room state for channel {before.channel.id} not found.")
#                         return
#                     state = self.room_states[before.channel.id]

#                     if before.channel.category_id == self.config.category_filled and len(before.channel.members) < before.channel.user_limit:
#                         category = discord.utils.get(before.channel.guild.categories, id=self.config.category_find)
#                         await before.channel.edit(category=category)
#                         if before.channel.members:
#                             await Message.create_message(self.logger, self.localization, before.channel, state, message)
                    
#                     if not before.channel.members:
#                         msg = await message.fetch_message(state.message_id)
#                         await msg.delete()
#                         del self.room_states[before.channel.id]
#                         await before.channel.delete()
                    
#                     elif before.channel.id in self.room_states:
#                         msg = await message.fetch_message(state.message_id)
#                         await Message.update_participants_message(self.logger, self.localization, before.channel, state, msg)
                
#                 # AFTER CHANNEL
#                 if after.channel and after.channel.category_id == self.config.category_create_room and after.channel.id in channel_limits:
#                     await CreateRoom.create_room(self.logger, self.config.category_find, self.room_states, channel_limits[after.channel.id], member)
                
#                 elif after.channel and after.channel.category_id in [self.config.category_filled, self.config.category_find]:
#                     if after.channel.id in self.room_states:
#                         message = self.bot.get_channel(self.config.text_channel_id)
#                         state = self.room_states[after.channel.id]
#                         if after.channel.category_id != self.config.category_filled and len(after.channel.members) == after.channel.user_limit:
#                             msg_dlt = await message.fetch_message(state.message_id)
#                             await msg_dlt.delete()
#                             category = discord.utils.get(after.channel.guild.categories, id=self.config.category_filled)
#                             await after.channel.edit(category=category)
#                         elif state.value == 0:
#                             await Message.create_message(self.logger, self.localization, after.channel, state, message)
#                         elif state.value == 1:
#                             msg_updt = await message.fetch_message(state.message_id)
#                             await Message.update_participants_message(self.logger, self.localization, after.channel, state, msg_updt)
            
#             except Exception as e:
#                 await self.logger.error(f"❌ Error in voice state update: {e}")

#     @commands.Cog.listener()
#     async def on_voice_channel_status_update(self, channel: discord.abc.GuildChannel, after: str, before: str):
#         """Sync voice status with party comment"""        
#         try:
#             if not isinstance(channel, discord.VoiceChannel):
#                 return
            
#             if channel.set_status and channel.id in self.room_states and channel.category_id == self.config.category_find:
#                 state = self.room_states[channel.id]
#                 msg_updt = await self.bot.get_channel(self.config.text_channel_id).fetch_message(state.message_id)
#                 if msg_updt:
#                     state.comment = channel.status
#                     await Message.update_comment_message(self.logger, self.localization, state, msg_updt)
#         except Exception as e:
#             await self.logger.error(f"❌ Error in voice state update: {e}")