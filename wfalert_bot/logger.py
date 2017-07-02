import MySQLdb
from config import tokens
from wfalertbot import WFAlertBot


class Logger:
    db = None
    db_cursor = None

    def __init__(self):
        self.connect_wfalertsdb()

    def connect_wfalertsdb(self):
        """
        Connects and returns a cursor to the wfalerts database
        :return: Database cursor object
        """
        self.db = MySQLdb.connect(host="localhost",
                                  user=tokens.SQL_USER,
                                  passwd=tokens.SQL_PASSWORD,
                                  db="wfalerts")
        self.db_cursor = self.db.cursor()

    def get_all_bot_instances(self):
        """
        Returns a list of all bot instances on the database
        :return: List of bots. If there is none, return an empty list
        """
        ret_list = []
        self.db_cursor.execute("SELECT * FROM bot_instances")

        for bot_row in self.db_cursor.fetchall():
            ret_list.append(WFAlertBot(int(bot_row[0]), bot_row[1] == 1))

        return ret_list

    def new_bot_instance(self, bot_obj):
        """
        Inserts a new bot instance into database
        :param bot_obj: Telegram bot object
        """
        sql_query = """INSERT INTO bot_instances (chat_id, wants_updates) VALUES ("""
        sql_query += str(bot_obj.chat_id) + """, """
        sql_query += str(bot_obj.wants_updates) + """);"""

        self.db_cursor.execute(sql_query)
        self.db.commit()

    def toggle_bot_wantsupdates(self, chatid):
        """
        Toggles the wants_updates field in the database
        :param chatid: Telegram chat ID
        """
        # Lookup what the current setting is
        sql_query = """SELECT wants_updates FROM bot_instances WHERE chat_id = """
        sql_query += str(chatid) + """;"""
        self.db_cursor.execute(sql_query)

        bot_option = self.db_cursor.fetchone()[0]
        new_option = not (bot_option == 1)

        # Toggle the setting
        sql_query = """UPDATE bot_instances SET wants_updates = """
        sql_query += str(new_option) + """  WHERE chat_id = """ + str(chatid) + """;"""

        # Execute sql query and commit to database
        self.db_cursor.execute(sql_query)
        self.db.commit()

    def iterate_command(self, command):
        """
        Iterates the specified command, intended to log commands used by users
        :param command: Bot command used
        """
        # TODO

    def log_reward(self, reward_name, reward_time):
        """
        Logs the reward and the time of the reward on to the database
        :param reward_name: Name of the reward
        :param reward_time: When the reward was announced
        """
        # TODO

    def log_errors(self, event_message, error, error_datetime):
        """
        Logs errors into database
        :param event_message: A self-generated message to provide context for the error
        :param error: The error
        :param error_datetime: The date & time of the event
        """
        # TODO

if __name__ == "__main__":
    log_test = Logger()
    bot_test = WFAlertBot(4, True)
    log_test.new_bot_instance(bot_test)
    bot_list = log_test.get_all_bot_instances()

    for bot in bot_list:
        print(bot)

    print("Toggling")
    log_test.toggle_bot_wantsupdates(4)
    bot_list = log_test.get_all_bot_instances()

    for bot in bot_list:
        print(bot)
