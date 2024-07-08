""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""
import asyncio
import json
import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Context

from typing import List, Dict
import traceback

from helpers import methods

config = methods.load_config()


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
        await interaction.response.send_modal(self.modal)

    @discord.ui.button(label="Cancel Delete", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Deletion of {self.actual_team_name} cancelled', ephemeral=True)
        self.value = False
        self.stop()


# Here we name the cog and create a new class for the cog.
class Team(commands.Cog, name="team"):
    """
    Team commands handle various functionalities related to teams.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    def get_players_embed(self, context: Context, team_status: bool, color: str, players: List[Dict]):
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
                roster_dict[role].append(f"{mention} - `{username}`")

        embeds = []
        for category, role_group in roles_order:
            description_str = ""
            for role in role_group:
                emoji = emojis.get(role, "")
                title = f"{emoji} {role}"
                if roster_dict[role]:
                    for username in roster_dict[role]:
                        description_str += f"**{title}:** {username}\n"
                else:
                    if team_status:
                        description_str += f"**{title}:** *Trialing*\n"
                    else:
                        pass

            if description_str:
                embed = discord.Embed(
                    description=description_str,
                    color=discord.Color.from_str(color)
                )
                embeds.append(embed)

        return embeds

    async def fetch_and_update(self, bot, team_name, new_embeds):
        config_path = f"{os.path.realpath(os.path.dirname(__file__))}/../configs/message_info.json"

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("No data found.")
            return

        if team_name not in data:
            print("Team name not found.")
            return

        to_remove = []  # Store indexes of messages that are not found
        for idx, info in enumerate(data[team_name]):
            channel_id = info['channel_id']
            message_id = info['message_id']

            channel = bot.get_channel(channel_id)
            if not channel:
                print(f"Channel {channel_id} not found.")
                continue

            message = None  # Initialize message variable
            try:
                message = await channel.fetch_message(message_id)
            except discord.errors.NotFound:
                print(f"Message {message_id} not found.")
                to_remove.append(idx)  # Mark this message for removal
                continue  # Skip to the next iteration

            if message:  # If message was successfully fetched
                if isinstance(new_embeds, list):
                    await message.edit(embeds=new_embeds)
                else:
                    await message.edit(embeds=[new_embeds])

        # Remove entries for messages that were not found
        if to_remove:
            data[team_name] = [info for i, info in enumerate(data[team_name]) if i not in to_remove]
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=4)

    async def update_roster(self, context: Context, team: str) -> bool:
        team_data = await self.bot.database.get_team(team)
        color = team_data[1]

        players = await self.bot.database.get_players(team)

        team_status = await self.bot.database.get_team_status(team)

        embeds = self.get_players_embed(context, team_status, color, players)

        await self.fetch_and_update(self.bot, team, embeds)
        return True

    @commands.hybrid_group(
        name="team",
        description="Lists, create, edit, delete and change trialing status of Alternate eSports teams.",
    )
    @commands.has_any_role("Owner", "CTO", "Managers", "OW | Coach", "Server Staff", "Technician Team")
    async def team(self, context: Context) -> None:
        """
        Lists, create, edit and delete all Alternate eSports team rosters.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n"
                            "`list` - List all team.\n`create` - Create a new team.\n"
                            "`edit` - Edit an existing team.\n`delete` - Delete an existing team.\n"
                            "`status` - Change trialing status of a team.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)

    @team.command(
        base="team",
        name="list",
        description="List all Alternate eSports team rosters.",
    )
    @commands.has_any_role("Owner", "CTO", "Managers", "OW | Coach", "Server Staff", "Technician Team")
    async def list_team(self, context: Context) -> None:
        """
        List all Alternate eSports team rosters.

        :param context: The hybrid command context.
        """
        teams = await self.bot.database.get_teams()
        embed = discord.Embed(
            title="Alternate eSports Teams",
            color=discord.Color.from_str(config["main_color"])
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
        name = methods.standardize_team_name(name)

        if await self.bot.database.get_team(name):
            embed = discord.Embed(
                title=f"Team {name} already exists.",
                color=discord.Color.from_str(config["error_color"]),
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
        name = methods.standardize_team_name(name)
        new_name = methods.standardize_team_name(new_name) if new_name else None

        existing_team = await self.bot.database.get_team(name)
        if not existing_team:
            embed = discord.Embed(
                title=f"Team {name} doesn't exist.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return

        # Update what's necessary
        if new_name or new_color:
            await self.bot.database.edit_team(name, new_name, new_color, None)
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
        name = methods.standardize_team_name(name)

        confirm_view = ConfirmView(name)
        existing_team = await self.bot.database.get_team(name)
        if not existing_team:
            embed = discord.Embed(
                title=f"Team {name} doesn't exist.",
                color=discord.Color.from_str(config["error_color"]),
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
                color=discord.Color.from_str(config["main_color"])
            )
            await context.send(embed=embed, ephemeral=True, delete_after=5)
        else:
            embed = discord.Embed(
                title=f'Deletion cancelled.',
                color=discord.Color.from_str(config["error_color"])
            )
            await context.send(embed=embed, ephemeral=True, delete_after=5)

    @team.command(
        base="team",
        name="status",
        description="Change trialing status of a team.",
    )
    @app_commands.describe(team="The name of the team to change status.")
    @commands.has_any_role("Owner", "CTO", "Managers", "OW | Coach", "Server Staff", "Technician Team")
    async def team_status(self, context: Context, team: str = None) -> None:
        """
        Change trialing status of a team.

        :param context: The hybrid command context.
        :param team: The name of the team to change status.
        """
        if team is None:
            if await methods.team_affiliation(context.author) == "Team does not exist.":
                embed = discord.Embed(
                    title=f"Team {team} doesn't exist.",
                    color=discord.Color.from_str(config["error_color"]),
                )
                await context.send(embed=embed, ephemeral=True)
                return
            elif await methods.team_affiliation(context.author) == "Sorry, you need to specify your team.":
                embed = discord.Embed(
                    title="Please specify your team.",
                    description="You are affiliated with multiple teams.",
                    color=discord.Color.from_str(config["error_color"]),
                )
                await context.send(embed=embed, ephemeral=True)
                return
            else:
                team = await methods.team_affiliation(context.author)
        else:
            team = methods.standardize_team_name(team)

        existing_team = await self.bot.database.get_team(team)
        if not existing_team:
            embed = discord.Embed(
                title=f"Team {team} doesn't exist.",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.send(embed=embed, ephemeral=True)
            return

        is_trialing = await self.bot.database.get_team_status(team)
        new_status = not is_trialing

        await self.bot.database.update_team_status(team, new_status)

        embed = discord.Embed(
            title=f'Team {team} is now {"trialing" if new_status else "not trialing"}.',
            color=discord.Color.from_str(config["main_color"])
        )
        await context.send(embed=embed, ephemeral=True, delete_after=5)

        if await self.update_roster(context, team):
            embed = discord.Embed(
                title="Rosters updated.",
                color=discord.Color.from_str(config["main_color"])
            )
            await context.interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Something went wrong",
                color=discord.Color.from_str(config["error_color"]),
            )
            await context.interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Team(bot))
