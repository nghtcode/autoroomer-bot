import discord
from discord.ext import commands

class Test(commands.Cog):
    __slots__ = ('bot', 'localization', 'config', 'logger')
    
    def __init__(self, bot: commands.Bot, localization, config, logger):
        self.bot = bot
        self.localization = localization
        self.config = config
        self.logger = logger

    @commands.command()
    async def greet(self, ctx: commands.Context):
        embed = discord.Embed(
            title=self.localization.get_text('welcome_message', user=ctx.author.name),
            description=self.localization.get_text('help_command', commands="greet"),
            color=discord.Color.blue()
        )
        # Отправка в канал приветствий из .env
        welcome_channel = self.bot.get_channel(self.config.welcome_channel_id)
        if welcome_channel:
            await welcome_channel.send(embed=embed)
        else:
            await ctx.send(embed=embed)