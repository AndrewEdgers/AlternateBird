import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import methods

config = methods.load_config()


class MockContext:
    def __init__(self, message):
        self.message = message
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild

    async def send(self, *args, **kwargs):
        """
        Mimics Context.send by forwarding to Channel.send
        """
        await self.channel.send(*args, **kwargs)


class Coaching(commands.Cog, name="coaching"):
    """
    Coaching commands allow setting up easy coaching sessions.
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent the bot from responding to its own messages
        if message.author == self.bot.user:
            return

        # Check if the message is "LEGO® Batman™: The Videogame"
        if "LEGO® Batman™: The Videogame" in message.content:
            args = message.content.split(maxsplit=4)  # Split the message into parts

            if len(args) >= 4 and message.mentions:
                team_name = args[3]  # The team name should follow the command
                member = message.mentions[0]  # Get the first mentioned user as the member

                # Create a mock context object
                mock_ctx = MockContext(message)

                # Call the create method with the mock context and other arguments
                await self.create(mock_ctx, member, team_name)
            else:
                await message.channel.send("Usage: LEGO® Batman™: The Videogame {team} @member")

    async def thread_exists(self, context: Context, member: discord.Member) -> bool:
        target_thread_name = f"{member.name} 1 on 1 coaching"
        threads = context.channel.threads

        for thread in threads:
            if thread.name == target_thread_name:
                return True

        return False

    @commands.hybrid_group(
        name="thread",
        description="Manage 1 on 1 coaching threads.",
    )
    @commands.has_any_role("Operation Manager", "AP", "Managers", "OW | Coach", "Server Staff", "Technician Team")
    async def thread(self, context: Context) -> None:
        """
        The main command for the coaching thread management.

        :param context: The application command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="You need to specify a subcommand.\n\n**Subcommands:**\n"
                            "`create` - Create new thread(s).\n`list` - Lists all active threads.\n"
                            "`close` - Close inactive threads.\n`update` - Update the threads.",
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)

    @thread.command(
        name="create",
        description="Create a new thread. Leave the member field empty to create a thread for the whole team.",
    )
    @commands.has_any_role("Operation Manager", "AP", "Managers", "OW | Coach", "Server Staff", "Technician Team")
    async def create(self, context: Context, member: discord.Member = None, team: str = None) -> None:
        """
        Create a new thread. Leave the member field empty to create a thread for the whole team.

        :param context: The application command context.
        :param member: The member to create the thread for.
        :param team: The team to create the thread for.
        """
        channel = context.channel

        if team is None:
            if await methods.team_affiliation(context.author) == "Team does not exist.":
                embed = discord.Embed(
                    title=f"Team {team} doesn't exist.",
                    color=0xE02B2B,
                )
                await context.send(embed=embed, ephemeral=True)
                return
            elif await methods.team_affiliation(context.author) == "Sorry, you need to specify your team.":
                embed = discord.Embed(
                    title="Please specify your team.",
                    description="You are affiliated with multiple teams.",
                    color=0xE02B2B,
                )
                await context.send(embed=embed, ephemeral=True)
                return
            else:
                team = await methods.team_affiliation(context.author)
        else:
            team = methods.standardize_team_name(team)

        player_roles = ['Main Tank', 'Off Tank', 'Hitscan DPS', 'Flex DPS', 'Main Support', 'Flex Support',
                        'Substitute']
        team_members = await self.bot.database.get_players(team)
        coaches_and_managers = [m for m in team_members if m[2] in ['Head Coach', 'Assistant Coach', 'Manager']]
        players = [m for m in team_members if m[2] in player_roles]
        if member is None:
            for player in players:  # Now iterating over players list
                member_id = player[0]  # Assuming player_id is at index 0
                member = context.guild.get_member(member_id)
                if member is not None and not await self.thread_exists(context, member):
                    thread = await channel.create_thread(
                        name=f"{member.name} 1 on 1 coaching",
                        type=discord.ChannelType.private_thread,
                        auto_archive_duration=60,
                        invitable=True,
                    )
                    await thread.add_user(member)  # Add the player to their thread.

                    # Also, add coaches and managers to the player's thread.
                    for coach_or_manager in coaches_and_managers:
                        cm_member_id = coach_or_manager[0]  # Assuming player_id is at index 0 for coaches/managers too
                        cm_member = context.guild.get_member(cm_member_id)
                        if cm_member is not None:
                            await thread.add_user(cm_member)
        else:
            if not await self.thread_exists(context, member):
                thread = await channel.create_thread(
                    name=f"{member.name} 1 on 1 coaching",
                    type=discord.ChannelType.private_thread,
                    auto_archive_duration=60,
                    invitable=True,
                )
                await thread.add_user(member)

                for coach_or_manager in coaches_and_managers:
                    cm_member_id = coach_or_manager[0]
                    cm_member = context.guild.get_member(cm_member_id)
                    if cm_member is not None:
                        await thread.add_user(cm_member)

        embed = discord.Embed(
            title="Thread(s) created successfully.",
            color=discord.Color.from_str(config["color"]),
        )
        await context.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Coaching(bot))
