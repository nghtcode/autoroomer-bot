import discord


class CreateInviteURL(discord.ui.View):
    def __init__(self, invite):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="Join voice channel",
                url=invite.url
            )
        )