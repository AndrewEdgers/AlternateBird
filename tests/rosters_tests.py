import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from discord.ext.commands import Context

# Adjust this import to match the actual location of your Roster class
from cogs.rosters import Roster


class TestSignPlayer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Set up the bot and context mocks
        self.bot = MagicMock()
        self.context = MagicMock()
        self.context.guild = MagicMock()

        # Properly mock interaction with AsyncMock
        self.context.interaction = MagicMock()
        self.context.interaction.response = MagicMock()
        self.context.interaction.response.defer = AsyncMock()
        self.context.interaction.followup = MagicMock()
        self.context.interaction.followup.send = AsyncMock()

        # Mock the database methods
        self.bot.database = MagicMock()
        self.bot.database.get_player = AsyncMock()
        self.bot.database.add_player = AsyncMock()
        self.bot.database.get_team = AsyncMock()
        self.bot.database.get_players = AsyncMock()
        self.bot.database.get_team_status = AsyncMock()

        # Create the command instance
        with patch('cogs.rosters.Roster.clean_expired_invites', new_callable=MagicMock):
            self.command_instance = Roster(self.bot)

    @patch('discord.utils.get')
    async def test_sign_player_success(self, mock_discord_utils_get):
        # Mock the external functions
        mock_discord_utils_get.side_effect = lambda roles, name: MagicMock() if name else None

        # Mock the database responses
        self.bot.database.get_player.return_value = None
        self.bot.database.get_team.return_value = ["Mock Team", "Mock Color"]

        # Call the command
        member = MagicMock(spec=discord.Member)
        member.id = 123456789
        member.display_name = "Mock Player"
        member.roles = []

        await self.command_instance.sign_player(self.context, member, "Main Tank", "Mock Team")

        # Assertions
        self.context.interaction.response.defer.assert_called_once_with(ephemeral=True)
        self.bot.database.add_player.assert_called_once_with(member.id, "Mock Team", "Main Tank")
        self.context.interaction.followup.send.assert_called()

    @patch('discord.utils.get')
    @patch('cogs.rosters.team_check')
    async def test_sign_player_existing_player(self, mock_team_check, mock_discord_utils_get):
        # Mock the external functions
        mock_team_check.return_value = "Mock Team"
        mock_discord_utils_get.side_effect = lambda roles, name: MagicMock() if name else None

        # Mock the database responses
        self.bot.database.get_player.return_value = [123456789, "Mock Team", "Main Tank"]

        # Call the command
        member = MagicMock(spec=discord.Member)
        member.id = 123456789
        member.display_name = "Mock Player"
        member.roles = []

        await self.command_instance.sign_player(self.context, member, "Main Tank", "Mock Team")

        # Assertions
        self.context.interaction.response.defer.assert_called_once_with(ephemeral=True)
        self.bot.database.add_player.assert_not_called()
        self.context.interaction.followup.send.assert_called()

    @patch('discord.utils.get')
    @patch('cogs.rosters.team_check')
    async def test_sign_player_team_does_not_exist(self, mock_team_check, mock_discord_utils_get):
        # Mock the external functions
        mock_team_check.return_value = "Mock Team"
        mock_discord_utils_get.side_effect = lambda roles, name: MagicMock() if name else None

        # Mock the database responses
        self.bot.database.get_player.return_value = None
        self.bot.database.get_team.return_value = None

        # Call the command
        member = MagicMock(spec=discord.Member)
        member.id = 123456789
        member.display_name = "Mock Player"
        member.roles = []

        await self.command_instance.sign_player(self.context, member, "Main Tank", "Mock Team")

        # Assertions
        self.context.interaction.response.defer.assert_called_once_with(ephemeral=True)
        self.bot.database.add_player.assert_not_called()
        self.context.interaction.followup.send.assert_called()

    @patch('discord.utils.get')
    @patch('cogs.rosters.team_check')
    async def test_sign_player_update_roster_failure(self, mock_team_check, mock_discord_utils_get):
        # Mock the external functions
        mock_team_check.return_value = "Mock Team"
        mock_discord_utils_get.side_effect = lambda roles, name: MagicMock() if name else None

        # Mock the database responses
        self.bot.database.get_player.return_value = None
        self.bot.database.get_team.return_value = ["Mock Team", "Mock Color"]

        # Mock the update_roster method to return False
        self.command_instance.update_roster = AsyncMock(return_value=False)

        # Call the command
        member = MagicMock(spec=discord.Member)
        member.id = 123456789
        member.display_name = "Mock Player"
        member.roles = []

        await self.command_instance.sign_player(self.context, member, "Main Tank", "Mock Team")

        # Assertions
        self.context.interaction.response.defer.assert_called_once_with(ephemeral=True)
        self.bot.database.add_player.assert_called_once_with(member.id, "Mock Team", "Main Tank")
        self.context.interaction.followup.send.assert_called()

    @patch('discord.utils.get')
    async def test_sign_player_exception(self, mock_discord_utils_get):
        # Mock the external functions
        mock_discord_utils_get.side_effect = lambda roles, name: MagicMock() if name else None

        # Mock the database responses
        self.bot.database.get_player.side_effect = Exception("Database Error")

        # Call the command
        member = MagicMock(spec=discord.Member)
        member.id = 123456789
        member.display_name = "Mock Player"
        member.roles = []

        with self.assertRaises(Exception):
            await self.command_instance.sign_player(self.context, member, "Main Tank", "Mock Team")

        # Assertions
        self.context.interaction.response.defer.assert_called_once_with(ephemeral=True)
        self.context.interaction.followup.send.assert_called()


if __name__ == '__main__':
    unittest.main()
