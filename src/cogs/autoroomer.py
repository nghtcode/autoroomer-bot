import asyncio
import discord
from discord.ext import commands
from typing import Dict
from ..utils.func import RoomState, CreateRoom, Message


class Autoroomer(commands.Cog):
    def __init__(self, bot: commands.Bot, localization, config, logger):
        """Initializes the Autoroomer with the bot, localization, config, and logger.

        Args:
            bot: An instance of the Discord bot.
            localization: A localization object for messages.
            config: The bot's configuration.
            logger: A logger for recording events and errors.

        Raises:
            ValueError: If the configuration contains invalid values for categories.
        """
        if not all([config.category_filled, config.category_find, config.category_create_room]):
            raise ValueError("🔴 Invalid configuration: missing required category IDs.")
        
        self.bot: commands.Bot = bot
        self.room_states: Dict[int, RoomState] = {}
        self.localization = localization
        self.config = config
        self.logger = logger
        self._lock: asyncio.Lock = asyncio.Lock()
        self._channel_locks: Dict[int, asyncio.Lock] = {}

    async def _get_channel_lock(self, channel_id: int) -> asyncio.Lock:
        """Get or create a lock for a specific channel.

        Args:
            channel_id: ID of the voice channel.

        Returns:
            asyncio.Lock: Lock for the specified channel.
        """
        if channel_id not in self._channel_locks:
            self._channel_locks[channel_id] = asyncio.Lock()
        return self._channel_locks[channel_id]

    async def _ensure_message_created(self, channel: discord.VoiceChannel, state: RoomState, message_channel: discord.TextChannel) -> None:
        """Ensures that the message for the room is created and state.message_id is updated.

        Args:
            channel: Voice channel.
            state: Room state.
            message_channel: Text channel for messages.
        """
        await Message.create_message(self.logger, self.localization, channel, state, message_channel)

    async def _handle_before_channel(self, channel: discord.VoiceChannel, message_channel: discord.TextChannel) -> None:
        """Handles user leave events from a voice channel.

        Args:
            channel: The voice channel the user left.
            message_channel: The text channel for messages.
        """
        async with await self._get_channel_lock(channel.id):
            if channel.id not in self.room_states:
                await self.logger.info(f"🔴 No state found for channel {channel.id}.")
                return
            state = self.room_states[channel.id]

            if channel.category_id == self.config.category_filled and len(channel.members) < channel.user_limit:
                category = discord.utils.get(channel.guild.categories, id=self.config.category_find)
                await channel.edit(category=category)
                if channel.members:
                    await self._ensure_message_created(channel, state, message_channel)

            if not channel.members:
                try:
                    if state.message_id is not None:
                        msg = await message_channel.fetch_message(state.message_id)
                        await msg.delete()
                    else:
                        await self.logger.info(f"🟠 No message_id for channel {channel.id}, skipping message deletion.")
                except discord.errors.NotFound:
                    await self.logger.info(f"🟠 Message {state.message_id} already deleted or not found.")
                except Exception as e:
                    await self.logger.error(f"🔴 Unexpected error while deleting message: {e}")
                finally:
                    if channel.id in self.room_states:
                        del self.room_states[channel.id]
                    if channel.id in self._channel_locks:
                        del self._channel_locks[channel.id]
                    try:
                        await channel.delete()
                    except discord.errors.NotFound:
                        await self.logger.info(f"🟠 Channel {channel.id} already deleted.")
                    except Exception as e:
                        await self.logger.error(f"🔴 Unexpected error while deleting channel: {e}")
            else:
                try:
                    if state.message_id is not None:
                        msg = await message_channel.fetch_message(state.message_id)
                        await Message.update_participants_message(self.logger, self.localization, channel, state, msg)
                    else:
                        await self._ensure_message_created(channel, state, message_channel)
                except discord.errors.NotFound:
                    await self._ensure_message_created(channel, state, message_channel)
                except Exception as e:
                    await self.logger.error(f"🔴 Unexpected error while updating message: {e}")

    async def _handle_after_channel(self, channel: discord.VoiceChannel, member: discord.Member, message_channel: discord.TextChannel) -> None:
        """Handles user join events in a voice channel.

        Args:
            channel: The voice channel the user joined.
            member: The user who joined the channel.
            message_channel: The text channel for messages.
        """
        channel_limits = {
            self.config.voice_1: 2,
            self.config.voice_2: 3,
            self.config.voice_3: 4
        }

        async with await self._get_channel_lock(channel.id):
            if channel.category_id == self.config.category_create_room and channel.id in channel_limits:
                await CreateRoom.create_room(self.logger, self.config.category_find, self.room_states, channel_limits[channel.id], member)
                if channel.id in self.room_states:
                    await self._ensure_message_created(channel, self.room_states[channel.id], message_channel)
            elif channel.category_id in [self.config.category_filled, self.config.category_find]:
                if channel.id in self.room_states:
                    state = self.room_states[channel.id]
                    if channel.category_id != self.config.category_filled and len(channel.members) == channel.user_limit:
                        try:
                            if state.message_id is not None:
                                msg = await message_channel.fetch_message(state.message_id)
                                await msg.delete()
                            else:
                                await self.logger.info(f"🟠 No message_id for channel {channel.id}, skipping message deletion.")
                        except discord.errors.NotFound:
                            await self.logger.info(f"🟠 Message {state.message_id} already deleted.")
                        except Exception as e:
                            await self.logger.error(f"🔴 Unexpected error while deleting message: {e}")
                        category = discord.utils.get(channel.guild.categories, id=self.config.category_filled)
                        if category:
                            await channel.edit(category=category)
                    elif state.value == 0:
                        await self._ensure_message_created(channel, state, message_channel)
                    elif state.value == 1:
                        try:
                            if state.message_id is not None:
                                msg = await message_channel.fetch_message(state.message_id)
                                await Message.update_participants_message(self.logger, self.localization, channel, state, msg)
                            else:
                                await self._ensure_message_created(channel, state, message_channel)
                        except discord.errors.NotFound:
                            await self._ensure_message_created(channel, state, message_channel)
                        except Exception as e:
                            await self.logger.error(f"🔴 Unexpected error while updating message: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Handler for voice state update events.

        Args:
            member: The user whose voice state changed.
            before: The voice state before the change.
            after: The voice state after the change.
        """
        message_channel = self.bot.get_channel(self.config.text_channel_id)
        if not message_channel:
            await self.logger.error(f"🔴 Text channel {self.config.text_channel_id} not found.")
            return

        async with self._lock:
            try:
                if before.channel and before.channel.category_id in [self.config.category_filled, self.config.category_find]:
                    await self._handle_before_channel(before.channel, message_channel)
                if after.channel:
                    await self._handle_after_channel(after.channel, member, message_channel)
            except Exception as e:
                await self.logger.error(f"🔴 Error in voice state update: {e}")

    @commands.Cog.listener()
    async def on_voice_channel_status_update(self, channel: discord.abc.GuildChannel, before: str, after: str) -> None:
        """Synchronizes the status of the voice channel with the comment in the message.

        Args:
            channel: The channel whose status changed.
            before: The previous status of the channel.
            after: The new status of the channel.
        """
        if not isinstance(channel, discord.VoiceChannel):
            return

        message_channel = self.bot.get_channel(self.config.text_channel_id)
        if not message_channel:
            await self.logger.error(f"🔴 Text channel {self.config.text_channel_id} not found.")
            return

        async with await self._get_channel_lock(channel.id):
            try:
                if channel.id in self.room_states and channel.category_id == self.config.category_find:
                    state = self.room_states[channel.id]
                    if state.message_id is None:
                        await self._ensure_message_created(channel, state, message_channel)
                    else:
                        try:
                            msg = await message_channel.fetch_message(state.message_id)
                            state.comment = after or ""
                            await Message.update_comment_message(self.logger, self.localization, state, msg)
                        except discord.errors.NotFound:
                            await self._ensure_message_created(channel, state, message_channel)
                        except Exception as e:
                            await self.logger.error(f"🔴 Unexpected error while updating comment message: {e}")
            except Exception as e:
                await self.logger.error(f"🔴 Error in voice channel status update: {e}")