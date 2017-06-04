import requests
import json
from config import tokens
from twitter_consumer.wftwitterconsumer import WFTwitterConsumer
from wfalertbot import WFAlertBot

TELEGRAM_BOT_URL = "https://api.telegram.org/bot" + tokens.BOT_TOKEN + "/"


class BotController:
    bots = []
    twitter_object = None
    telegram_offset = 0

    def __init__(self):
        self.twitter_object = WFTwitterConsumer()
        self.get_updates()

    def get_updates(self):
        """
        Gets new updates from Telegram server based on the saved offset.
        Long Polling
        :return: JSON object containing all updates
        """
        update_url = TELEGRAM_BOT_URL + "getUpdates"
        payload = {"timeout": "60", "allowed_updates": ["message"]}

        if self.telegram_offset > 0:
            payload.update({"offset": self.telegram_offset})

        # Only want the results, we can ignore the 200 Response
        updates_json = json.loads(requests.get(update_url, params=payload).content)["result"]\

        # Update the offset
        for entry in updates_json:
            # TODO: Log all incoming commands
            if int(entry["update_id"]) >= self.telegram_offset:
                self.telegram_offset = entry["update_id"] + 1

        # Return the JSON object
        return updates_json

    def new_bot(self, chat_id):
        """
        Initalizes a new WFAlertBot and saves it to the bot list
        :param chat_id: The chat ID
        :return: The new WFAlertBot object
        """
        newbot = WFAlertBot(chat_id)
        self.bots.append(newbot)
        return newbot

    def destroy_bot(self, target_bot):
        """
        Removes the bot with the specified chat ID from bot list
        :param target_bot: The bot to be removed
        :return: True if bot with target ID exists and is removed, False otherwise
        """
        self.bots.remove(target_bot)

    def bot_has_id(self, chat_id):
        """
        Checks if bot list contains a bot with that ID number
        :param chat_id: The chat ID number
        :return: The WFAlertBot object with the specified chat ID
        """
        for bot in self.bots:
            if chat_id == bot.chat_id:
                return True
        return False

    def get_bot(self, chat_id):
        """
        Returns bot with given chat ID
        :param chat_id: Target chat ID
        :return: Target bot, None if it does not exist
        """
        for bot in self.bots:
            if chat_id == bot.chat_id:
                return bot
        return None

    @staticmethod
    def alerts_as_string(alert_list, add_time):
        """
        Converts alerts list to a HTML string for easy readability
        :param alert_list: The list of alerts
        :param add_time: True/False, indicates if time start and time end should be appended
        :return: HTML formatted string
        """
        retstring = ""

        for alert in alert_list:
            alert_parts = alert.split("|")

            retstring += "<b>" + alert_parts[0] + " - " + alert_parts[1] + "</b> Mission Type: " + alert_parts[2]

            if add_time:
                retstring += " <i>" + alert_parts[5] + ", Ends In" + alert_parts[6] + "</i> \n" + \
                             "----------------------\n"
            else:
                retstring += " <b>Alert will last for " + alert_parts[7] + " minutes</b>\n----------------------\n"

        return retstring

    @staticmethod
    def send_message(bot_object, message):
        """
        Sends a message to the chat with the ID number provided
        :param bot_object: The bot that holds the target chat ID
        :param message: The message in HTML format
        :return: True if successful, False otherwise
        """
        send_message_url = TELEGRAM_BOT_URL + "sendMessage"
        payload = {"chat_id": bot_object.chat_id, "text": message, "parse_mode": "HTML"}

        if requests.get(url=send_message_url, params=payload) is None:
            # TODO: Need to log the reason why message wasn't sent
            return False
        return True

    def decipher_command(self, json_entry):
        """
        Handles the message command
        :param json_entry: The JSON-formatted command
        :return: True if successful, False otherwise
        """
        if "message" not in json_entry or "text" not in json_entry["message"]:
            return False

        chat_id = json_entry["message"]["chat"]["id"]
        command_parts = json_entry["message"]["text"].split(" ")

        item_command = ""
        if len(command_parts) > 1:
            for part in command_parts[1:]:
                item_command += part + " "
            item_command = item_command[:-1]

        command = command_parts[0].split("@")[0]

        if not self.bot_has_id(chat_id):
            target_bot = self.new_bot(chat_id)
        else:
            target_bot = self.get_bot(chat_id)

        if command == "/start":
            self.send_message(target_bot, "<b>Ordis will keep you</b> <i>in the loop</i><b>. Haha. Haha. </b>")
            target_bot.toggle_wants_updates_on()
        elif command == "/stop":
            self.send_message(target_bot, "<b>Ordis will stop bothering you now :( </b>")
            target_bot.toggle_wants_updates_off()
        elif command == "/allcurrentalerts":
            self.send_current_alerts(target_bot)
        elif command == "/ignorelist":
            self.send_ignore_list(target_bot)
        elif command == "/ignore":
            if item_command == "":
                self.send_message(target_bot, "<b>Ordis is not sure what the Operator is trying to ignore</b>")
            else:
                self.add_ignore(target_bot, item_command)
        elif command == "/noignore":
            if item_command == "":
                self.send_message(target_bot, "<b>Ordis is not sure what the Operator is not trying to ignore</b>")
            else:
                self.remove_ignore(target_bot, item_command)
        elif command == "/amigettingupdates":
            if target_bot.wants_updates:
                self.send_message(target_bot, "<b>Yes</b>")
            else:
                self.send_message(target_bot, "<b>No</b>")
        elif command == "/tellmeajoke":
            self.send_message(target_bot, "<b>Ordis thinks your face is a joke. Haha. Haha. \n...\n Sorry Operator, "
                                          "Ordis is not very good at jokes</b>")
        else:
            self.send_message(target_bot, "<i>Ordis is very confused :( </i>")

        return True

    def send_current_alerts(self, bot_object):
        """
        Sends all current alerts to the user that requested it
        :param bot_object: The bot that holds the requesting chat ID
        """
        current_alerts = self.twitter_object.getallcurrentalerts()
        alert_string = self.alerts_as_string(current_alerts, False)
        if alert_string is not "":
            self.send_message(bot_object, alert_string)
        else:
            self.send_message(bot_object, "<b>Ordis could not find any current alerts. Ordis is sorry</b>")

    def send_ignore_list(self, bot_object):
        """
        Sends the list of ignored rewards to the user that requested it
        :param bot_object: The bot that holds the requesting chat ID
        """
        if not bot_object.ignored_rewards:
            self.send_message(bot_object, "<b>There are no ignored rewards</b>")
        else:
            send_string = ""

            for item in bot_object.ignored_rewards:
                send_string += item + "\n"

            self.send_message(bot_object, send_string)

    @staticmethod
    def add_ignore(bot_object, item):
        """
        Adds new item to the bot's ignore list
        :param bot_object: Target bot holding requester's chat ID
        :param item: Target item
        """
        bot_object.add_to_ignored_rewards(item)

    @staticmethod
    def remove_ignore(bot_object, item):
        """
        Removes target item from the bot's ignore list
        :param bot_object: Target bot holding requester's chat ID
        :param item: Target item
        """
        bot_object.remove_from_ignored_rewards(item)

    def send_alerts(self, bot_object, alerts_list):
        """
        Sends out alerts updates
        :param bot_object: Target bot
        :param alerts_list: List of new alerts
        """
        use_alerts = alerts_list[:]
        for alert in use_alerts:
            alert_parts = alert.split("|")

            for ignored_rewards in bot_object.ignored_rewards:
                if ignored_rewards in alert_parts[1]:
                    use_alerts.remove(alert)

        self.send_message(bot_object, self.alerts_as_string(use_alerts, True))

    def main(self):
        """The main script"""
        while True:
            # First check for any new commands and act on them, at most this should only wait 1 minute
            updates = self.get_updates()

            for entry in updates:
                self.decipher_command(entry)

            # Now check for new Warframe Alerts and message the subscribers
            new_alerts = self.twitter_object.consume_wfstatus(
                self.twitter_object.get_statuses(self.twitter_object.offset_id))

            # TODO: Log all new alerts

            for bot in self.bots:
                if bot.wants_updates:
                    self.send_alerts(bot, new_alerts)


if __name__ == "__main__":
    btc = BotController()
    btc.main()

