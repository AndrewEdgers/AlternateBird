""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers.methods import load_config

config = load_config()


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    """
    This is a template cog.
    """
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    async def testcommand(self, context: Context) -> None:
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        # Do your stuff here

        # Don't forget to remove "pass", I added this just because there's no content in the method.
        pass


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Template(bot))
