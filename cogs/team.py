""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import json
import os
import sys
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
        config = json.load(file)


# Here we name the cog and create a new class for the cog.
class Team(commands.Cog, name="team"):
    """
    Team commands handle various functionalities related to teams.
    """
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger("discord_bot")
        self.invites = {}
        self.clean_expired_invites.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug("On ready started.")
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()
            self.logger.debug(f"Cached invites for {guild.name}: {self.invites[guild.id]}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print("Member joined:", member.name)  # Debug line
        guild = member.guild

        # Read the tryout data from the JSON file
        json_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/tryout_invites.json"
        with open(json_path, "r") as f:
            tryout_data = json.load(f)

        # Fetch the new list of invites
        new_invites = await guild.invites()

        # Find the used invite by comparing old and new invite data
        used_invite = None
        for new_invite in new_invites:
            for cached_invite in self.invites[guild.id]:
                if new_invite.code == cached_invite.code and new_invite.uses > cached_invite.uses:
                    used_invite = new_invite

        # Update the cached invites
        self.invites[guild.id] = new_invites

        if used_invite:  # Check if used_invite is not None
            role_name = tryout_data.get(str(used_invite.code), None)
            if role_name:
                del tryout_data[str(used_invite.code)]

                # Update the JSON file
                with open(json_path, "w") as f:
                    json.dump(tryout_data, f)

                # Delete the used invite
                await used_invite.delete(reason="Invite used, deleting.")

                # Get the role object from the guild based on the role_name
                role_to_assign = discord.utils.get(guild.roles, name=role_name)
                if role_to_assign:
                    await member.add_roles(role_to_assign)
                else:
                    self.logger.warning(f"Role {role_name} not found in guild {guild.name}")

    @tasks.loop(hours=168)
    async def clean_expired_invites(self):
        self.logger.info("Cleaning expired invites")
        channel = await self.bot.fetch_channel(1000763776095752302)
        json_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/tryout_invites.json"

        with open(json_path, "r") as f:
            tryout_data = json.load(f)

        for code in list(tryout_data.keys()):
            try:
                invite = await self.bot.fetch_invite(code)
            except discord.NotFound:  # Invite not found
                del tryout_data[code]

        with open(json_path, "w") as f:
            json.dump(tryout_data, f)

    def standardize_team_name(self, team_name: str) -> str:
        words = team_name.split()
        capitalized_words = [word.capitalize() for word in words]
        capitalized_team_name = ' '.join(capitalized_words)

        if not capitalized_team_name.startswith("Alternate "):
            return f"Alternate {capitalized_team_name}"

        return capitalized_team_name

    # populate string with captain roles from database in format "OW | {stripped_team_name} Captain",
    # def get_captain_roles(self) -> str:
    #     for team in self.bot.database.get_teams():
    #         stripped_team_name = team.replace("Alternate ", "").strip()
    #         yield f"OW | {stripped_team_name} Captain"

    @commands.hybrid_command(
        name="tryout",
        description="Creates a tryout invite for the specified team.",
    )
    @commands.check_any(commands.has_any_role("Operation Manager", "AP", "Managers", "OW | Coach"))
    async def tryout(self, context: Context, team: str, amount: int = 1, member: discord.Member = None) -> None:
        """
        Creates a tryout invite for the specified team.

        :param context: The context of the command.
        :param team: The name of the team.
        :param amount: The amount of invites to create.
        :param member: The member to give tryout to.
        """
        await context.defer()
        team = self.standardize_team_name(team)
        stripped_team_name = team.replace("Alternate ", "").strip()

        team = await self.bot.database.get_team(team)
        if not team:
            embed = discord.Embed(
                title="Team not found",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        if member:
            role_name = f"OW | {stripped_team_name} Tryout"
            role = discord.utils.get(context.guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="Tryout role not found",
                    color=0xE02B2B,
                )
                await context.send(embed=embed, ephemeral=True)
                return

            await member.add_roles(role)
            embed = discord.Embed(
                title=f"{team[0]} tryout given to {member.display_name}",
                color=discord.Color.from_str(config["color"]),
            )
        else:

            embed = discord.Embed(
                title="Tryout invite created",
                description=f"**Team:** {team[0]}",
                color=discord.Color.from_str(config["color"]),
            )

            channel = self.bot.get_channel(1000763776095752302)
            # for each amount of invites, create a new invite
            for i in range(amount):
                invite = await channel.create_invite(max_age=604800, max_uses=2, unique=True,
                                                     reason="Tryout invite")
                self.invites[context.guild.id] = await context.guild.invites()
                json_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/tryout_invites.json"

                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        file_content = f.read()
                        if file_content:
                            tryout_data = json.loads(file_content)
                        else:
                            tryout_data = {}  # Initialize as empty dictionary if the file is empty

                role_name = f"OW | {stripped_team_name} Tryout"
                tryout_data[str(invite.code)] = role_name

                with open(json_path, "w") as f:
                    json.dump(tryout_data, f)

                embed.add_field(name="Invite link", value=f"```{invite.url}```", inline=False)

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ringer",
        description="Creates a tryout invite for the specified team.",
    )
    @commands.check_any(commands.has_any_role("Operation Manager", "AP", "Managers", "OW | Coach"))
    async def ringer(self, context: Context, team: str, amount: int = 1, member: discord.Member = None) -> None:
        """
        Creates a ringer invite for the specified team.

        :param context: The context of the command.
        :param team: The name of the team.
        :param amount: The amount of invites to create.
        :param member: The member to give tryout to.
        """
        await context.defer()
        team = self.standardize_team_name(team)
        stripped_team_name = team.replace("Alternate ", "").strip()

        team = await self.bot.database.get_team(team)
        if not team:
            embed = discord.Embed(
                title="Team not found",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        if member:
            role_name = f"OW | {stripped_team_name} Ringer"
            role = discord.utils.get(context.guild.roles, name=role_name)
            if not role:
                embed = discord.Embed(
                    title="Ringer role not found",
                    color=0xE02B2B,
                )
                await context.send(embed=embed, ephemeral=True)
                return

            await member.add_roles(role)
            embed = discord.Embed(
                title=f"{team[0]} ringer given to {member.display_name}",
                color=discord.Color.from_str(config["color"]),
            )
        else:

            embed = discord.Embed(
                title="Ringer invite created",
                description=f"**Team:** {team[0]}",
                color=discord.Color.from_str(config["color"]),
            )

            channel = self.bot.get_channel(1000763776095752302)
            # for each amount of invites, create a new invite
            for i in range(amount):
                invite = await channel.create_invite(max_age=604800, max_uses=2, unique=True,
                                                     reason="Ringer invite")
                self.invites[context.guild.id] = await context.guild.invites()
                json_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/tryout_invites.json"

                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        file_content = f.read()
                        if file_content:
                            tryout_data = json.loads(file_content)
                        else:
                            tryout_data = {}  # Initialize as empty dictionary if the file is empty

                role_name = f"OW | {stripped_team_name} Ringer"
                tryout_data[str(invite.code)] = role_name

                with open(json_path, "w") as f:
                    json.dump(tryout_data, f)

                embed.add_field(name="Invite link", value=f"```{invite.url}```", inline=False)

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="cut",
        description="Cuts a tryout from the specified team."
    )
    @commands.check_any(commands.has_any_role("Operation Manager", "AP", "Managers", "OW | Coach"))
    async def cut(self, context: Context, team: str, member: discord.Member) -> None:
        """
        Cuts a tryout from the specified team.

        :param context: The context of the command.
        :param team: The name of the team.
        :param member: The member to cut.
        """
        await context.defer(ephemeral=True)
        team = self.standardize_team_name(team)
        team = await self.bot.database.get_team(team)
        if not team:
            embed = discord.Embed(
                title="Team not found",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        role_name = f"OW | {team[0].replace('Alternate ', '').strip()} Tryout"
        role = discord.utils.get(context.guild.roles, name=role_name)
        if not role:
            embed = discord.Embed(
                title="Tryout role not found",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        await member.remove_roles(role)
        embed = discord.Embed(
            title="Tryout cut",
            color=discord.Color.from_str(config["color"]),
        )
        await context.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Team(bot))
