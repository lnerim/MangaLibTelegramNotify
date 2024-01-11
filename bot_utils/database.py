import sqlite3

TABLE_TITLES = "TITLES"
TITLES_KEY = "key"
TITLES_ID = "id"
TITLES_USER_ID = "user_id"
TITLES_SITE_ID = "site_id"
TITLES_NAME = "name"


class BotDataBase:
    def __init__(self, name: str = "database.sqlite"):
        self.connection = sqlite3.connect(name, check_same_thread=False)
        self.cursor = self.connection.cursor()

        with self.connection:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_TITLES} ("
                                f"{TITLES_KEY} INTEGER PRIMARY KEY, "
                                f"{TITLES_ID} INTEGER NOT NULL, "
                                f"{TITLES_USER_ID} TEXT NOT NULL, "
                                f"{TITLES_SITE_ID} TEXT NOT NULL, "
                                f"{TITLES_NAME} TEXT NOT NULL);")

    def publication_add(self, title_id: int, user_id: int, site_id: int, name: str) -> None:
        with self.connection:
            if self.cursor.execute(
                    f"SELECT * FROM `{TABLE_TITLES}` WHERE `{TITLES_ID}` = ? AND `{TITLES_USER_ID}` = ? "
                    f"AND `{TITLES_SITE_ID}` = ? AND `{TITLES_NAME}` = ?",
                    (title_id, user_id, site_id, name)).fetchone():
                return

            self.cursor.execute(
                f"INSERT INTO `{TABLE_TITLES}` (`{TITLES_ID}`, `{TITLES_USER_ID}`, "
                f"`{TITLES_SITE_ID}`, `{TITLES_NAME}`) VALUES(?,?,?,?)", (title_id, user_id, site_id, name)
            )

    def publication_delete(self, key: int) -> None:
        with self.connection:
            self.cursor.execute(
                f"DELETE FROM `{TABLE_TITLES}` WHERE `{TITLES_KEY}` = ?", (key,)
            )

    def users_by_publication(self, title_id: int) -> list[tuple[int, int]] | None:
        """
        :param title_id:
        :return list[tuple[key, user_id]] | None:
        """
        with self.connection:
            return self.cursor.execute(
                f"SELECT `{TITLES_KEY}`, `{TITLES_USER_ID}` FROM `{TABLE_TITLES}` WHERE `{TITLES_ID}` = ?", (title_id,)
            ).fetchall()

    def publications_by_user(self, user_id: int) -> list | None:
        with self.connection:
            return self.cursor.execute(
                f"SELECT `{TITLES_KEY}`, `{TITLES_NAME}` FROM `{TABLE_TITLES}` WHERE `{TITLES_USER_ID}` = ?", (user_id,)
            ).fetchall()


db = BotDataBase()
