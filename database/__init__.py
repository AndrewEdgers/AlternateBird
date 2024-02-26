""""
Copyright © Krypton 2019-2023 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized discord bot in Python programming language.

Version: 6.1.0
"""

import aiosqlite


class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def add_warn(
            self, user_id: int, server_id: int, moderator_id: int, reason: str
    ) -> int:
        """
        This function will add a warn to the database.

        :param user_id: The ID of the user that should be warned.
        :param reason: The reason why the user should be warned.
        """
        rows = await self.connection.execute(
            "SELECT id FROM warns WHERE user_id=? AND server_id=? ORDER BY id DESC LIMIT 1",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            warn_id = result[0] + 1 if result is not None else 1
            await self.connection.execute(
                "INSERT INTO warns(id, user_id, server_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
                (
                    warn_id,
                    user_id,
                    server_id,
                    moderator_id,
                    reason,
                ),
            )
            await self.connection.commit()
            return warn_id

    async def remove_warn(self, warn_id: int, user_id: int, server_id: int) -> int:
        """
        This function will remove a warn from the database.

        :param warn_id: The ID of the warn.
        :param user_id: The ID of the user that was warned.
        :param server_id: The ID of the server where the user has been warned
        """
        await self.connection.execute(
            "DELETE FROM warns WHERE id=? AND user_id=? AND server_id=?",
            (
                warn_id,
                user_id,
                server_id,
            ),
        )
        await self.connection.commit()
        rows = await self.connection.execute(
            "SELECT COUNT(*) FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0

    async def get_warnings(self, user_id: int, server_id: int) -> list:
        """
        This function will get all the warnings of a user.

        :param user_id: The ID of the user that should be checked.
        :param server_id: The ID of the server that should be checked.
        :return: A list of all the warnings of the user.
        """
        rows = await self.connection.execute(
            "SELECT user_id, server_id, moderator_id, reason, strftime('%s', created_at), id FROM warns WHERE user_id=? AND server_id=?",
            (
                user_id,
                server_id,
            ),
        )
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row)
            return result_list

    async def create_team(self, team_name: str, color: str, banner: str, rank: str = None):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO teams (team_name, color, banner, rank) VALUES (?, ?, ?, ?)",
                (team_name, color, banner, rank)
            )
            await self.connection.commit()

    async def delete_team(self, team_name: str):
        async with self.connection.cursor() as cursor:
            await cursor.execute("DELETE FROM teams WHERE team_name = ?", (team_name,))
            await self.connection.commit()

    async def edit_team(self, team_name: str, new_name: str = None, color: str = None, banner: str = None,
                        rank: str = None):
        async with self.connection.cursor() as cursor:
            fields = []
            values = []

            if new_name is not None:
                fields.append("team_name = ?")
                values.append(new_name)
            if color is not None:
                fields.append("color = ?")
                values.append(color)
            if banner is not None:
                fields.append("banner = ?")
                values.append(banner)
            if rank is not None:
                fields.append("rank = ?")
                values.append(rank)

            if not fields:
                return  # No changes, so no need to update the database

            query = f"UPDATE teams SET {', '.join(fields)} WHERE team_name = ?"
            values.append(team_name)

            await cursor.execute(query, values)
            await self.connection.commit()

    async def update_team_banner(self, team_name: str, new_banner_path: str):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "UPDATE teams SET banner = ? WHERE team_name = ?",
                (new_banner_path, team_name)
            )
            await self.connection.commit()

    async def get_managed_teams(self, player_id: int):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT team_name FROM players WHERE player_id = ? AND role = 'Manager'", (player_id,))
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_team(self, team_name: str):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM teams WHERE team_name = ?", (team_name,))
            return await cursor.fetchone()

    async def get_teams(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM teams")
            return await cursor.fetchall()

    async def add_player(self, player_id: int, team_name: str, role: str):
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO players (player_id, team_name, role) VALUES (?, ?, ?)",
                (player_id, team_name, role)
            )
            await self.connection.commit()

    async def delete_player(self, player_id: int, role: str = None, team_name: str = None):
        async with self.connection.cursor() as cursor:
            query = "DELETE FROM players WHERE player_id = ?"
            params = [player_id]

            if role is not None:
                query += " AND role = ?"
                params.append(role)

            if team_name is not None:
                query += " AND team_name = ?"
                params.append(team_name)

            await cursor.execute(query, params)
            await self.connection.commit()

    async def edit_player(self, player_id: int, team_name: str = None, role: str = None):
        async with self.connection.cursor() as cursor:
            fields = []
            values = []

            if team_name is not None:
                fields.append("team_name = ?")
                values.append(team_name)
            if role is not None:
                fields.append("role = ?")
                values.append(role)

            if not fields:
                return

            query = f"UPDATE players SET {', '.join(fields)} WHERE player_id = ?"
            values.append(player_id)

            await cursor.execute(query, values)
            await self.connection.commit()

    async def get_player(self, player_id: int):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
            return await cursor.fetchone()

    async def get_players(self, team_name: str):
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT * FROM players WHERE team_name = ?", (team_name,))
            return await cursor.fetchall()
