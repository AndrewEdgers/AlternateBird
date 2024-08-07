""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import platform

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View, Select

from helpers import methods

config = methods.load_config()


class HelpSelect(Select):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            placeholder="Select a category...",
            options=[
                discord.SelectOption(label=cog_name.capitalize(), description=cog.__doc__) for cog_name, cog in
                bot.cogs.items() if
                cog.__cog_commands__ and cog_name not in ["Jishaku"]
            ])

        self.bot = bot

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_cog = self.values[0]
        await self.send_command_help(interaction, selected_cog)

    async def send_command_help(self, interaction: discord.Interaction, cog_name: str) -> None:
        cog = self.bot.get_cog(cog_name.lower())
        prefix = "/"
        embed = discord.Embed(
            title=f"<:Lightteal:1082786810662498304> Help for {cog_name.capitalize()} <:Lightteal:1082786810662498304>",
            description="**List of available commands:**",
            color=discord.Color.from_str(config["main_color"]),
        )

        for command in cog.get_commands():
            description = command.description.partition("\n")[0]
            cmd_id = self.bot.cached_command_ids.get(command.name, "Unknown")

            def format_command_name(name, id):
                return f"<{prefix}{name}:{id}>" if id != "Unknown" else f"!{name}"

            if hasattr(command, 'commands'):
                for subcommand in command.commands:
                    sub_desc = subcommand.description.partition("\n")[0]
                    formatted_name = format_command_name(f"{command.name} {subcommand.name}", cmd_id)
                    embed.add_field(
                        name=formatted_name,
                        value=f"`{sub_desc}`",
                        inline=False
                    )
            else:
                formatted_name = format_command_name(command.name, cmd_id)
                embed.add_field(
                    name=formatted_name,
                    value=f"`{description}`",
                    inline=False
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class General(commands.Cog, name="general"):
    """
    General commands that provide information about the bot or the server.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.context_menu_user = app_commands.ContextMenu(
            name="Grab ID", callback=self.grab_id
        )
        self.bot.tree.add_command(self.context_menu_user)
        self.context_menu_message = app_commands.ContextMenu(
            name="Remove spoilers", callback=self.remove_spoilers
        )
        self.bot.tree.add_command(self.context_menu_message)

    # Message context menu command
    async def remove_spoilers(
            self, interaction: discord.Interaction, message: discord.Message
    ) -> None:
        """
        Removes the spoilers from the message. This command requires the MESSAGE_CONTENT intent to work properly.

        :param interaction: The application command interaction.
        :param message: The message that is being interacted with.
        """
        spoiler_attachment = None
        for attachment in message.attachments:
            if attachment.is_spoiler():
                spoiler_attachment = attachment
                break
        embed = discord.Embed(
            title="Message without spoilers",
            description=message.content.replace("||", ""),
            color=discord.Color.from_str(config["main_color"]),
        )
        if spoiler_attachment is not None:
            embed.set_image(url=attachment.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # User context menu command
    async def grab_id(
            self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        """
        Grabs the ID of the user.

        :param interaction: The application command interaction.
        :param user: The user that is being interacted with.
        """
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=discord.Color.from_str(config["main_color"]),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="help", description="List all available commands."
    )
    async def help(self, context: Context) -> None:
        embed = discord.Embed(
            title="Help",
            description="**Select a category to get more information.**",
            color=discord.Color.from_str(config["main_color"]),
        )

        for cog_name, cog in self.bot.cogs.items():
            description = cog.__doc__[:97] + "..." if len(cog.__doc__) > 100 else cog.__doc__
            # strip description off of newlines and whitespace at the end and beginning
            description = description.strip()

            if cog.__doc__:  # Only add cogs that have a docstring description
                embed.add_field(
                    name=cog_name.capitalize(),
                    value=f"`{description}`",
                    inline=False
                )

        view = View().add_item(HelpSelect(self.bot))
        await context.send(embed=embed, view=view, delete_after=120)

    # @commands.hybrid_command(
    #     name="help", description="List all commands the bot has loaded."
    # )
    # async def help(self, context: Context) -> None:
    #     prefix = "/"
    #     embed = discord.Embed(
    #         title="Help",
    #         description="**List of available commands:**",
    #         color=discord.Color.from_str(config["main_color"]),
    #     )
    #     # embed.set_thumbnail(url="https://alt-esports.x3.pm/i/8d0lk.gif")
    #
    #     for i in self.bot.cogs:
    #         if i == "owner" and not (await self.bot.is_owner(context.author)):
    #             continue
    #         cog = self.bot.get_cog(i.lower())
    #         data = []
    #         for command in cog.get_commands():
    #             description = command.description.partition("\n")[0]
    #             cmd_id = self.bot.cached_command_ids.get(command.name, "Unknown")
    #
    #             # Function to format command name with or without ID
    #             def format_command_name(name, id):
    #                 return f"<{prefix}{name}:{id}>" if id != "Unknown" else f"!{name}"
    #
    #             # Check if this is a parent command
    #             if hasattr(command, 'commands'):
    #                 for subcommand in command.commands:
    #                     sub_desc = subcommand.description.partition("\n")[0]
    #                     formatted_name = format_command_name(f"{command.name} {subcommand.name}", cmd_id)
    #                     data.append(f"{formatted_name} - `{sub_desc}`")
    #             else:
    #                 formatted_name = format_command_name(command.name, cmd_id)
    #                 data.append(f"{formatted_name} - `{description}`")
    #
    #         help_text = "\n".join(data)
    #         embed.add_field(
    #             name='\u200b',
    #             value="``` ```",
    #             inline=False
    #         )
    #         embed.add_field(
    #             name=f"<:Lightteal:1082786810662498304> {i.capitalize()} <:Lightteal:1082786810662498304>",
    #             value=f"{help_text}", inline=False
    #         )
    #     await context.send(embed=embed, delete_after=90)

    @commands.hybrid_command(
        name="botinfo",
        description="Get information about the bot.",
    )
    async def botinfo(self, context: Context) -> None:
        """
        Get information about the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description="Used [Krypton's](https://krypton.ninja) template",
            color=discord.Color.from_str(config["main_color"]),
        )
        embed.set_author(name="Bot Information")
        embed.add_field(name="Owner:", value="edgers", inline=True)
        embed.add_field(
            name="Python Version:", value=f"{platform.python_version()}", inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {self.bot.config['prefix']} for normal commands",
            inline=False,
        )
        embed.set_footer(text=f"Requested by {context.author}")
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get information about the server.",
    )
    async def serverinfo(self, context: Context) -> None:
        """
        Get information about the server.

        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f"\n>>>> Displaying [50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**", description=f"{context.guild} <:Alternate:1053103469172625499>",
            color=discord.Color.from_str(config["main_color"])
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(url=context.guild.icon.url)
        embed.add_field(name="Server ID", value=f'{context.guild.id} ')
        embed.add_field(name="Member Count", value=context.guild.member_count)
        embed.add_field(
            name="Text/Voice Channels", value=f"{len(context.guild.channels)}"
        )
        embed.add_field(name=f"Roles ({len(context.guild.roles)})", value=roles)
        embed.set_footer(text=f"Created at: {context.guild.created_at}")
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=discord.Color.from_str(config["main_color"]),
        )
        await context.send(embed=embed, ephemeral=True)

    # @commands.hybrid_command(
    #     name="invite",
    #     description="Get the invite link of the bot to be able to invite it.",
    # )
    # async def invite(self, context: Context) -> None:
    #     """
    #     Get the invite link of the bot to be able to invite it.


#
#     :param context: The hybrid command context.
#     """
#     embed = discord.Embed(
#         description=f"Invite me by clicking [here]({self.bot.config['invite_link']}).",
#         color=0xD75BF4,
#     )
#     try:
#         await context.author.send(embed=embed)
#         await context.send("I sent you a private message!")
#     except discord.Forbidden:
#         await context.send(embed=embed)

# @commands.hybrid_command(
#     name="server",
#     description="Get the invite link of the discord server of the bot for some support.",
# )
# async def server(self, context: Context) -> None:
#     """
#     Get the invite link of the discord server of the bot for some support.
#
#     :param context: The hybrid command context.
#     """
#     embed = discord.Embed(
#         description=f"Join the support server for the bot by clicking [here](https://discord.gg/mTBrXyWxAF).",
#         color=0xD75BF4,
#     )
#     try:
#         await context.author.send(embed=embed)
#         await context.send("I sent you a private message!")
#     except discord.Forbidden:
#         await context.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(General(bot))
