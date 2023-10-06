""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import asyncio
import json
import os
import sys

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Context

import traceback
from typing import List, Dict

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
        config = json.load(file)


class ConfirmModal(discord.ui.Modal, title="Confirm Delete"):
    def __init__(self, actual_team_name):
        super().__init__()
        self.should_delete = False
        self.actual_team_name = actual_team_name
        self.submitted = asyncio.Event()

    name = discord.ui.TextInput(
        label='Confirm Team Name',
        placeholder='Enter the team name to confirm deletion',
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.name.value == self.actual_team_name:
            print("Names match. Setting should_delete to True")  # Debugging line
            await interaction.response.send_message(f'Deleting {self.name.value}!', ephemeral=True, delete_after=5)
            self.should_delete = True
            self.submitted.set()
            self.stop()

        else:
            await interaction.response.send_message('Team name does not match. Deletion cancelled.', ephemeral=True,
                                                    delete_after=5)
            self.should_delete = False
            self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class ConfirmView(discord.ui.View):
    def __init__(self, actual_team_name, *, timeout=180):
        super().__init__(timeout=timeout)
        self.value = None
        self.actual_team_name = actual_team_name
        self.modal = ConfirmModal(self.actual_team_name)

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message(content='Confirming', ephemeral=True)
        await interaction.response.send_modal(self.modal)

    @discord.ui.button(label="Cancel Delete", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


class Roster(commands.Cog, name="rosters"):
    def __init__(self, bot) -> None:
        self.bot = bot

    def get_coaches_embed(self, context: Context):
        head_coaches = []
        assistant_head_coaches = []
        coaches = []

        for member in context.guild.members:
            if discord.utils.get(member.roles, name="OW | Head Coach"):
                head_coaches.append(member)
            elif discord.utils.get(member.roles, name="Assistant Head Coach"):
                assistant_head_coaches.append(member)
            elif discord.utils.get(member.roles, name="OW | Coach"):
                coaches.append(member)

        # Sort the lists alphabetically
        head_coaches = sorted(head_coaches, key=lambda x: x.name.lower())
        assistant_head_coaches = sorted(assistant_head_coaches, key=lambda x: x.name.lower())
        coaches = sorted(coaches, key=lambda x: x.name.lower())

        # Initialize description string
        description_str = ""

        # Create strings for the embed description based on the number of coaches
        if head_coaches:
            title = "**<:HeadCoach:1159488503437078598> Head Coach**" if len(
                head_coaches) == 1 else "**<:HeadCoach:1159488503437078598> Head Coaches**"
            head_coaches_str = "\n".join([f"{member.mention} - {member.name}" for member in head_coaches])
            description_str += f"**{title}**\n{head_coaches_str}\n\n"

        if assistant_head_coaches:
            title = "**<:AHC:1159488404950622218> Assistant Head Coach**" if len(
                assistant_head_coaches) == 1 else "**<:AHC:1159488404950622218> Assistant Head Coaches**"
            assistant_head_coaches_str = "\n".join(
                [f"{member.mention} - {member.name}" for member in assistant_head_coaches])
            description_str += f"**{title}**\n{assistant_head_coaches_str}\n\n"

        description_str += "**<:Coach:1159488573502931004> Coaches**"

        embed = discord.Embed(
            title="Alternate eSports Coaches Roster",
            description=description_str,
            color=discord.Color.from_str(config["color"])
        )

        # Add the rest of the coaches as fields
        for member in coaches:
            embed.add_field(name=member.name, value=member.mention, inline=True)

        return embed

    def get_staff_embed(self, context: Context):
        roles_dict = {
            "Operation Manager": [],
            "Operations Coordinator": [],
            "Community Events Coordinator": [],
            "Staff Coordinator": [],
            "Head Moderator": [],
            "Server Moderator": [],
            "Technician Team": [],
            "Social Media Team": [],
            "Graphics Team": [],
            "Content Analyst": []
        }

        role_emojis = {
            "Operation Manager": "<:OM:1159587754250874941>",
            "Operations Coordinator": "<:OC:1159587816318185632>",
            "Community Events Coordinator": "<:EC:1159587876393209896>",
            "Staff Coordinator": "<:SC:1159587910174130227>",
            "Head Moderator": "<:HM:1159587983939342408>",
            "Server Moderator": "<:SM:1159588016919158898>",
            "Technician Team": "<:TT:1159588058841223248>",
            "Social Media Team": "<:SMT:1159588106169765898>",
            "Graphics Team": "<:GT:1159588167226245211>",
            "Content Analyst": "<:CA:1159588200088608940>"
        }

        no_plural_roles = ["Technician Team", "Social Media Team", "Graphics Team"]

        for member in context.guild.members:
            for role in member.roles:
                if role.name in roles_dict:
                    roles_dict[role.name].append(member)

        # Sort the lists alphabetically
        for role, members in roles_dict.items():
            roles_dict[role] = sorted(members, key=lambda x: x.name.lower())

        # Initialize description string
        description_str = ""

        for role, members in roles_dict.items():
            if members:
                emoji = role_emojis.get(role, "")  # Get the emoji for the role, if available
                if role in no_plural_roles:
                    title = f"{emoji} **{role}**"
                else:
                    title = f"{emoji} **{role}**" if len(members) == 1 else f"{emoji} **{role}s**"
                members_str = "\n".join([f"{member.mention} - {member.name}" for member in members])
                description_str += f"{title}\n{members_str}\n\n"

        embed = discord.Embed(
            title="Alternate eSports Staff and Teams",
            description=description_str,
            color=discord.Color.from_str(config["color"])
        )

        return embed

    def get_players_embed(self, context: Context, team_name: str, color: str, players: List[Dict]):
        roles_order = [
            ("Staff", ["Head Coach", "Assistant Coach", "Manager"]),
            ("Players", ["Main Tank", "Off Tank", "Hitscan DPS", "Flex DPS", "Main Support", "Flex Support"]),
            ("Substitute", ["Substitute"])
        ]

        emojis = {
            "Head Coach": "<:HeadCoach:1159488503437078598>",
            "Assistant Coach": "<:AHC:1159488404950622218>",
            "Manager": "<:manager:1159872594502242375>",
            "Main Tank": "<:tank:1159871555128537241>",
            "Off Tank": "<:offtank:1159872063322988657>",
            "Hitscan DPS": "<:hitscan:1159872249843699734>",
            "Flex DPS": "<:flexdps:1159871979315282000>",
            "Main Support": "<:mainsupport:1159871872842866828>",
            "Flex Support": "<:flexsupport:1159871932099989595>",
            "Substitute": "<:sub:1159872018150338661>"
        }

        roster_dict = {}
        for _, role_group in roles_order:
            for role in role_group:
                roster_dict[role] = []

        for player in players:
            player_id, role = player[0], player[2]
            member = context.guild.get_member(player_id)
            if member:
                username = member.name
                mention = member.mention
                roster_dict[role].append(f"{mention} - {username}")

        embeds = []
        for category, role_group in roles_order:
            description_str = ""
            for role in role_group:
                emoji = emojis.get(role, "")
                title = f"{emoji} {role}"
                if roster_dict[role]:
                    for username in roster_dict[role]:
                        description_str += f"{title}: {username}\n"
                else:
                    description_str += f"{title}: *Trialing*\n"

            embed = discord.Embed(
                description=description_str,
                color=discord.Color.from_str(color)
            )
            embeds.append(embed)

        return embeds

    @commands.hybrid_command(
        name="coaches",
        description="Lists all Alternate eSports coaches roster.",
    )
    async def coaches(self, context: Context) -> None:
        """
        Lists all Alternate eSports coaches roster.

        :param context: The hybrid command context.
        """
        if await self.bot.is_owner(context.author):
            embed = discord.Embed(
                title="Alternate eSports Coaches Roster",
                color=discord.Color.from_str(config["color"])
            )
            await context.send(embed=embed, ephemeral=True)
            await context.channel.send(file=discord.File('graphics/Coaches.png'), embed=self.get_coaches_embed(context))
        else:
            await context.send(file=discord.File('graphics/Coaches.png'), embed=self.get_coaches_embed(context),
                               ephemeral=True)

    @commands.hybrid_command(
        name="updatecoach",
        description="Updates the coaches roster message.",
    )
    @app_commands.describe(message="The message to update.")
    @commands.is_owner()
    async def update_coach(self, context: Context, message: str = None) -> None:
        """
        Updates the coaches roster message.

        :param context: The hybrid command context.
        :param message: The message to update.
        """
        if message is not None:
            # convert message to int
            message = int(message)

        embed = discord.Embed(
            title="Updating Coach roster...",
            color=discord.Color.from_str(config["color"])
        )
        reply = await context.send(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="Coaches roster updated.",
            color=discord.Color.from_str(config["color"])
        )
        # get the message
        message = await context.channel.fetch_message(message)
        await message.edit(embed=self.get_coaches_embed(context))
        await reply.edit(embed=embed, delete_after=5)

    @commands.hybrid_command(
        name="staff",
        description="Lists all Alternate eSports staff roster.",
    )
    @commands.is_owner()
    async def staff(self, context: Context) -> None:
        """
        Lists all Alternate eSports staff roster.

        :param context: The hybrid command context.
        """
        reply = discord.Embed(
            title="Alternate eSports Staff and Teams Roster",
            color=discord.Color.from_str(config["color"])
        )
        await context.send(embed=reply, ephemeral=True)

        await context.channel.send(file=discord.File('graphics/Staff.png'), embed=self.get_staff_embed(context))

    @commands.hybrid_command(
        name="updatestaff",
        description="Updates the staff roster message.",
    )
    @app_commands.describe(message="The message to update.")
    @commands.is_owner()
    async def update_staff(self, context: Context, message: str = None) -> None:
        """
        Updates the staff roster message.

        :param context: The hybrid command context.
        :param message: The message to update.
        """
        if message is not None:
            # convert message to int
            message = int(message)

        embed = discord.Embed(
            title="Updating Staff roster...",
            color=discord.Color.from_str(config["color"])
        )
        reply = await context.send(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="Staff roster updated.",
            color=discord.Color.from_str(config["color"])
        )
        # get the message
        message = await context.channel.fetch_message(message)
        await message.edit(embed=self.get_staff_embed(context))
        await reply.edit(embed=embed, delete_after=5)

    @commands.hybrid_group(
        name="team",
        description="Lists, create, edit and delete Alternate eSports teams.",
    )
    @commands.is_owner()
    async def team(self, context: Context) -> None:
        """
        Lists, create, edit and delete all Alternate eSports team rosters.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n"
                            "`list` - List all team.\n`create` - Create a new team.\n"
                            "`edit` - Edit an existing team.\n`delete` - Delete an existing team.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)

    @team.command(
        base="team",
        name="list",
        description="List all Alternate eSports team rosters.",
    )
    @commands.is_owner()
    async def list_team(self, context: Context) -> None:
        """
        List all Alternate eSports team rosters.

        :param context: The hybrid command context.
        """
        teams = await self.bot.database.get_teams()
        embed = discord.Embed(
            title="Alternate eSports Teams",
            color=discord.Color.from_str(config["color"])
        )

        for team in teams:
            embed.add_field(name=team[0], value=f'`{team[1]}`', inline=True)

        await context.send(embed=embed, ephemeral=True)

    @team.command(
        base="team",
        name="create",
        description="Create a new team.",
    )
    @app_commands.describe(name="The name of the team to create.", color="The color of the team to create.",
                           rank="The rank of the team to create. (Optional)")
    @commands.is_owner()
    async def create_team(self, context: Context, name: str, color: str, rank: str = None) -> None:
        """
        Create a new team.

        :param context: The hybrid command context.
        :param name: The name of the team to create.
        :param color: The color of the team to create.
        :param rank: The rank of the team to create.
        """
        name = name.capitalize()
        if name.startswith("Alternate "):
            name = name
        else:
            name = "Alternate " + name

        if await self.bot.database.get_team(name):
            embed = discord.Embed(
                title=f"Team {name} already exists.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        global banner_path, message
        embed = discord.Embed(
            title=f'Creating {name}...',
            color=discord.Color.from_str(color)
        )
        reply = await context.send(embed=embed, ephemeral=True)

        request = await context.send("Please upload the team banner.", ephemeral=True)

        def check(message):
            return message.author == context.author and len(message.attachments) > 0

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await request.edit(content="Time's up. Please try the command again.", delete_after=10)
        else:
            attachment = message.attachments[0]
            banner_path = f'graphics/{attachment.filename}'
            await attachment.save(banner_path)
            await context.send(f"Saved banner to {banner_path}", ephemeral=True, delete_after=4)
            await request.delete()

        await self.bot.database.create_team(name, color, banner_path, rank)

        embed = discord.Embed(
            title=f'Team {name} created.',
            color=discord.Color.from_str(color)
        )
        await reply.edit(embed=embed, delete_after=5)
        await message.delete()

    @team.command(
        base="team",
        name="edit",
        description="Edit an existing team.",
    )
    @app_commands.describe(
        name="The name of the team to edit.",
        new_name="The new name for the team.",
        new_color="The new color for the team.",
        new_banner="Change the banner?",
        new_rank="The new rank for the team."
    )
    @app_commands.choices(new_banner=[Choice(name="True", value="True")])
    @commands.is_owner()
    async def edit_team(self, context: Context, name: str, new_name: str = None, new_color: str = None,
                        new_banner: str = None, new_rank: str = None) -> None:
        """
        Edit an existing team.

        :param context: The hybrid command context.
        :param name: The name of the team to edit.
        :param new_name: The new name for the team.
        :param new_color: The new color for the team.
        :param new_banner: The new banner for the team.
        :param new_rank: The new rank for the team.
        """
        name = name.capitalize()
        if name.startswith("Alternate "):
            name = name
        else:
            name = "Alternate " + name

        existing_team = await self.bot.database.get_team(name)
        if not existing_team:
            embed = discord.Embed(
                title=f"Team {name} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        # Update what's necessary
        if new_name:
            await self.bot.database.edit_team(name, new_name)
        if new_color:
            await self.bot.database.update_team_color(name, new_color)
        if new_banner:
            # Step 1: Delete the old banner file
            old_banner_path = existing_team[2]
            if os.path.exists(old_banner_path):
                os.remove(old_banner_path)

            # Step 2: Prompt the user to upload a new banner
            request = await context.send("Please upload the new team banner.", ephemeral=True)

            def check(message):
                return message.author == context.author and len(message.attachments) > 0

            try:
                message = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                await request.edit(content="Time's up. Please try the command again.", delete_after=10)
            else:
                # Step 3: Save the new banner
                attachment = message.attachments[0]
                new_banner_path = f'graphics/{attachment.filename}'
                await attachment.save(new_banner_path)
                await self.bot.database.update_team_banner(name,
                                                           new_banner_path)
                await context.send(f"New banner saved to {new_banner_path}", ephemeral=True, delete_after=4)
                await request.delete()
                await message.delete()
        if new_rank:
            await self.bot.database.update_team_rank(name, new_rank)

        embed = discord.Embed(
            title=f'Team {name} updated.',
            color=discord.Color.green()
        )
        await context.send(embed=embed, delete_after=5)

    @team.command(
        base="team",
        name="delete",
        description="Delete an existing team.",
    )
    @app_commands.describe(name="The name of the team to delete.")
    @commands.is_owner()
    async def delete_team(self, context: Context, name: str) -> None:
        """
        Delete an existing team.

        :param context: The hybrid command context.
        :param name: The name of the team to delete.
        """
        # Check if the team exists
        name = name.capitalize()
        if name.startswith("Alternate "):
            name = name
        else:
            name = "Alternate " + name

        confirm_view = ConfirmView(name)
        existing_team = await self.bot.database.get_team(name)
        if not existing_team:
            embed = discord.Embed(
                title=f"Team {name} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        # Initial confirmation message
        await context.send("Are you sure you want to delete the team?", view=confirm_view, ephemeral=True,
                           delete_after=20)

        await confirm_view.modal.submitted.wait()  # Wait for the ConfirmModal to be submitted

        if confirm_view.modal.should_delete:
            banner_path = existing_team[2]
            if os.path.exists(banner_path):
                os.remove(banner_path)

            # Delete the team
            await self.bot.database.delete_team(name)

            embed = discord.Embed(
                title=f'Team {name} deleted.',
                color=discord.Color.from_str(config["color"])
            )
            await context.send(embed=embed, ephemeral=True, delete_after=5)
        else:
            embed = discord.Embed(
                title=f'Deletion cancelled.',
                color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True, delete_after=5)

    @commands.hybrid_group(
        name="player",
        description="Lists, sign, release and edit Alternate eSports players.",
    )
    @commands.is_owner()
    async def player(self, context: Context) -> None:
        """
        Lists, sign, release and edit Alternate eSports players.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n"
                            "`roster` - List all players.\n`sign` - Sign a new player.\n"
                            "`release` - Release an existing player.\n"
                            "`edit` - Edit an existing player.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)

    @player.command(
        base="player",
        name="roster",
        description="Shows team roster.",
    )
    @commands.is_owner()
    async def player_roster(self, context: Context, team: str) -> None:
        """
        List all Alternate eSports players.


        :param context: The hybrid command context.
        :param team: The team to list the players for.
        """
        team = team.capitalize()
        if team.startswith("Alternate "):
            team = team
        else:
            team = "Alternate " + team
        # Check if the team exists
        if not await self.bot.database.get_team(team):
            embed = discord.Embed(
                title=f"Team {team} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        team_data = await self.bot.database.get_team(team)
        color = team_data[1]
        banner_path = team_data[2]

        players = await self.bot.database.get_players(team)
        embeds = self.get_players_embed(context, team, color, players)

        embed = discord.Embed(
            title=f'Alternate eSports {team} Roster',
            color=discord.Color.from_str(config["color"])
        )
        await context.send(embed=embed, ephemeral=True)

        await context.channel.send(file=discord.File(banner_path), embeds=embeds)

    @player.command(
        base="player",
        name="update",
        description="Updates the roster message.",
    )
    @app_commands.describe(message="The message to update.")
    @commands.is_owner()
    async def update_player(self, context: Context, message: str, team: str) -> None:
        """
        Updates the roster message.

        :param context: The hybrid command context.
        :param message: The message to update.
        :param team: The team to update the roster for.
        """
        message = int(message)
        team = team.capitalize()
        if team.startswith("Alternate "):
            team = team
        else:
            team = "Alternate " + team

        # Check if the team exists
        if not await self.bot.database.get_team(team):
            embed = discord.Embed(
                title=f"Team {team} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="Updating roster...",
            color=discord.Color.from_str(config["color"])
        )
        reply = await context.send(embed=embed, ephemeral=True)

        team_data = await self.bot.database.get_team(team)
        color = team_data[1]

        players = await self.bot.database.get_players(team)

        message = await context.channel.fetch_message(message)
        embeds = self.get_players_embed(context, team, color, players)
        await message.edit(embeds=embeds)

        embed = discord.Embed(
            title="Roster updated.",
            color=discord.Color.from_str(config["color"])
        )
        # get the message
        await reply.edit(embed=embed, delete_after=5)

    @player.command(
        base="player",
        name="sign",
        description="Sign a new player.",
    )
    @app_commands.describe(member="The id of the player to sign.", team="The team to sign the player to.",
                           role="The role of the player to sign.")
    @commands.is_owner()
    @app_commands.choices(role=[Choice(name="Main Tank", value="Main Tank"),
                                Choice(name="Off Tank", value="Off Tank"),
                                Choice(name="Hitscan DPS", value="Hitscan DPS"),
                                Choice(name="Flex DPS", value="Flex DPS"),
                                Choice(name="Main Support", value="Main Support"),
                                Choice(name="Flex Support", value="Flex Support"),
                                Choice(name="Substitute", value="Substitute"),
                                Choice(name="Head Coach", value="Head Coach"),
                                Choice(name="Assistant Coach", value="Assistant Coach"),
                                Choice(name="Manager", value="Manager")])
    async def sign_player(self, context: Context, member: discord.Member, team: str, role: str) -> None:
        """
        Sign a new player.

        :param context: The hybrid command context.
        :param member: The name of the player to sign.
        :param team: The team to sign the player to.
        :param role: The role of the player to sign.
        """
        player_id = member.id
        name = member.display_name
        team = team.capitalize()
        if team.startswith("Alternate "):
            team = team
        else:
            team = "Alternate " + team

        # Check if the player already exists
        if await self.bot.database.get_player(player_id):
            embed = discord.Embed(
                title=f"Player {name} already in a roster.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        # Check if the team exists
        if not await self.bot.database.get_team(team):
            embed = discord.Embed(
                title=f"Team {team} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        await self.bot.database.add_player(player_id, team, role)

        embed = discord.Embed(
            title=f'Signed player {name} for a {team} as a {role}.',
            color=discord.Color.from_str(config["color"])
        )
        await context.send(embed=embed, delete_after=10)

    @player.command(
        base="player",
        name="release",
        description="Release an existing player.",
    )
    @app_commands.describe(member="The name of the player to release.")
    @commands.is_owner()
    async def release_player(self, context: Context, member: discord.Member) -> None:
        """
        Release an existing player.

        :param context: The hybrid command context.
        :param member: The id of the player to release.
        """
        player_id = member.id
        name = member.display_name
        if not await self.bot.database.get_player(player_id):
            embed = discord.Embed(
                title=f"Player {name} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        await self.bot.database.delete_player(player_id)

        embed = discord.Embed(
            title=f'Player {name} released.',
            color=discord.Color.from_str(config["color"])
        )
        await context.send(embed=embed, delete_after=10)

    @player.command(
        base="player",
        name="edit",
        description="Edit an existing player.",
    )
    @app_commands.describe(member="The name of the player to edit.", new_role="The new role for the player.")
    @commands.is_owner()
    @app_commands.choices(new_role=[Choice(name="Main Tank", value="Main Tank"),
                                    Choice(name="Off Tank", value="Off Tank"),
                                    Choice(name="Hitscan DPS", value="Hitscan DPS"),
                                    Choice(name="Flex DPS", value="Flex DPS"),
                                    Choice(name="Main Support", value="Main Support"),
                                    Choice(name="Flex Support", value="Flex Support"),
                                    Choice(name="Substitute", value="Substitute"),
                                    Choice(name="Head Coach", value="Head Coach"),
                                    Choice(name="Assistant Coach", value="Assistant Coach"),
                                    Choice(name="Manager", value="Manager")])
    async def edit_player(self, context: Context, member: discord.Member, new_role: str) -> None:
        """
        Edit an existing player.

        :param context: The hybrid command context.
        :param member: The id of the player to edit.
        :param new_role: The new role for the player.
        """
        player_id = member.id
        name = member.display_name
        if not await self.bot.database.get_player(player_id):
            embed = discord.Embed(
                title=f"Player {name} doesn't exist.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
            return

        await self.bot.database.edit_player(player_id=player_id, role=new_role)

        embed = discord.Embed(
            title=f'Player {name} updated.',
            color=discord.Color.from_str(config["color"])
        )
        await context.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Roster(bot))
