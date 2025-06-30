import discord
from ..utils import views
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class RoomState:
    owner_id: int
    message_id: Optional[int]
    value: int
    comment: str


class CreateRoom:
    @staticmethod
    async def create_room(
        logger,
        category_id: int,
        room_states: Dict[int, RoomState],
        user_limit: int,
        member: discord.Member
    ) -> None:
        """Creates a voice channel and initializes its state.

        Args:
            logger: Logger for recording events and errors.
            category_id: ID of the category where the channel will be created.
            room_states: Dictionary of room states.
            user_limit: User limit for the channel.
            member: The user initiating the channel creation.

        Returns:
            Optional[discord.VoiceChannel]: The created voice channel, or None if an error occurs.
        """
        try:
            voice_channel = await member.guild.create_voice_channel(
                name=f"Room_{user_limit}",
                category=discord.utils.get(member.guild.categories, id=category_id),
                user_limit=user_limit
            )
            room_states[voice_channel.id] = RoomState(
                owner_id=member.id,
                message_id=None,
                value=0,
                comment=""
            )
            await voice_channel.set_permissions(member, connect=True, mute_members=True, move_members=True)
            await member.move_to(voice_channel)
        except discord.errors.Forbidden:
            await logger.error(f"❌ Missing permissions to create channel in guild {member.guild.id}.")
        except Exception as e:
            await logger.error(f"❌ Error while creating the room: {e}")


class Message:
    @staticmethod
    async def create_message(
        logger,
        localization,
        channel: discord.VoiceChannel,
        state: RoomState,
        active_channel: discord.TextChannel
    ) -> None:
        """Creates an informational message about the voice channel.

        Args:
            logger: Logger for recording events and errors.
            localization: Localization object for texts.
            channel: The voice channel the message is about.
            state: The state of the room.
            active_channel: The text channel where the message will be sent.

        Returns:
            Optional[discord.Message]: The created message, or None if an error occurs.
        """
        try:
            embed_data = localization.get_text("embeds.create_message")
            state.value = 1
            embed = await Message._build_embed(embed_data, channel, state, channel.members)
            invite = await channel.create_invite()
            message = await active_channel.send(embed=embed, view=views.CreateInviteURL(invite))
            state.message_id = message.id
        except discord.errors.Forbidden:
            await logger.error(f"❌ Missing permissions to send message in channel {active_channel.id}.")
        except Exception as e:
            await logger.error(f"❌ Error while creating the message: {e}")

    @staticmethod
    async def update_comment_message(
        logger,
        localization,
        state: RoomState,
        message: discord.Message
    ) -> None:
        """Updates the comment in the informational message of the voice channel.

        Args:
            logger: Logger for recording events and errors.
            localization: Localization object for texts.
            state: The state of the room.
            message: The message to update.
        """
        try:
            # embed = message.embeds[0] if message.embeds else None
            # if not embed:
            #     await logger.error("❌ No embed found in the message to update")
            #     return
            
            embed = message.embeds[0]
            embed_data = localization.get_text("embeds.create_message")
            embed.set_field_at(index=1, name="", value=embed_data["fields"][1]["value"].format(comment=state.comment), inline=False)
            await message.edit(embed=embed)
        except discord.errors.Forbidden:
            await logger.error(f"❌ Missing permissions to edit message {message.id}.")
        except Exception as e:
            await logger.error(f"❌ Error updating comment: {e}")


    @staticmethod
    async def update_participants_message(
        logger,
        localization,
        channel: discord.VoiceChannel,
        state: RoomState,
        message: discord.Message
    ) -> None:
        """Updates the list of participants in the informational message of the voice channel.

        Args:
            logger: Logger for recording events and errors.
            localization: Localization object for texts.
            channel: The voice channel.
            state: The state of the room.
            message: The message to update.
        """
        try:
            embed = message.embeds[0]
            embed_data = localization.get_text("embeds.create_message")
            participants = channel.members
            output = Message._build_participant_list(embed_data, channel, state, participants)
            embed.set_field_at(index=0, name="", value="\n".join(output), inline=False)
            await message.edit(embed=embed)
        except discord.errors.Forbidden:
            await logger.error(f"❌ Missing permissions to edit message {message.id}.")
        except Exception as e:
            await logger.error(f"❌ Error updating message: {e}")

    @staticmethod
    async def _build_embed(
        embed_data: dict,
        channel: discord.VoiceChannel,
        state: RoomState,
        participants: List[discord.Member]
    ) -> discord.Embed:
        """Creates an embed for the informational message.

        Args:
            embed_data: Localization data for the embed.
            channel: The voice channel.
            state: The state of the room.
            participants: List of channel participants.

        Returns:
            discord.Embed: The generated embed.
        """
        output = Message._build_participant_list(embed_data, channel, state, participants)
        embed = discord.Embed(title=embed_data["title"],description="",color=discord.Color(embed_data["color"]), timestamp=datetime.now(timezone.utc))
        embed.add_field(name="", value="\n".join(output), inline=False)
        embed.add_field(name="", value=embed_data["fields"][1]["value"].format(comment=state.comment), inline=False)
        embed.set_author(name=embed_data["bot"]["name"], icon_url=embed_data["bot"]["url"])
        embed.set_thumbnail(url=embed_data["thumbnail"]["url"])
        embed.set_footer(text=embed_data["footer"]["text"], icon_url=embed_data["footer"]["icon_url"])
        return embed

    @staticmethod
    def _build_participant_list(
        embed_data: dict,
        channel: discord.VoiceChannel,
        state: RoomState,
        participants: List[discord.Member]
    ) -> List[str]:
        """Creates a list of participants to embed in the message.

        Args:
            embed_data: Localization data for the embed.
            channel: Voice channel.
            state: Room state.
            participants: List of channel participants.

        Returns:
            List[str]: A list of strings representing participants and available slots.
        """
        output = []
        for i in range(channel.user_limit):
            if i < len(participants):
                suffix = "[OWNER]" if participants[i].id == state.owner_id else ""
                output.append(
                    embed_data["fields"][0]["value"]["participant"].format(
                        suffix=suffix,
                        user_id=participants[i].id
                    )
                )
            else:
                output.append(embed_data["fields"][0]["value"]["free_slot"])
        return output