import json
import os
import sys
import discord

from typing import Optional
from database import DatabaseManager

database: Optional[DatabaseManager] = None


def set_database(db_manager: DatabaseManager) -> None:
    global database
    database = db_manager


def load_config():
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"):
        sys.exit("'config.json' not found! Please add it and try again.")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
            return json.load(file)


def standardize_team_name(team_name: str) -> str:
    words = team_name.split()
    capitalized_words = [word.capitalize() for word in words]
    capitalized_team_name = ' '.join(capitalized_words)

    if not capitalized_team_name.startswith("Alternate "):
        return f"Alternate {capitalized_team_name}"

    return capitalized_team_name


async def team_affiliation(member: discord.Member) -> str:
    roles = [role.name for role in member.roles]
    qualifying_roles = [
        role for role in roles
        if role.startswith("OW |") and role.split()[-1] in {"Manager", "Coach", "Captain"}
    ]

    team_names = set(" ".join(role.split("|")[1].split()[:-1]).strip() for role in qualifying_roles)

    if len(team_names) == 1:
        team_name = team_names.pop()
        standardized_team_name = standardize_team_name(team_name)

        team_info = await database.get_team(standardized_team_name)
        if team_info:
            return standardized_team_name
        else:
            return "Team does not exist."
    else:
        return "Sorry, you need to specify your team."
