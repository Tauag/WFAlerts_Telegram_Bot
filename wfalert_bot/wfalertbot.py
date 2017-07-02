class WFAlertBot:
    chat_id = 0
    wants_updates = False
    ignored_rewards = None

    def __init__(self, chatid, update_bool=False):
        self.chat_id = chatid
        self.wants_updates = update_bool
        self.ignored_rewards = []

    def __str__(self):
        retstring = str(self.chat_id)

        if self.wants_updates:
            retstring += " wants updates and ignores "
        else:
            retstring += " does not want updates and ignores: "

        if not self.ignored_rewards:
            for item in self.ignored_rewards:
                retstring += "[" + item + "] "
        else:
            retstring += "None"

    def toggle_wants_updates_on(self):
        """
        Toggles if the chat wants to continue to be updated with warframe alerts to True
        """
        self.wants_updates = True

    def toggle_wants_updates_off(self):
        """
        Toggles if the chat wants to continue to be updated with warframe alerts to False
        """
        self.wants_updates = False

    def add_to_ignored_rewards(self, reward):
        """
        Adds to the list of ignored rewards
        :param reward: The target reward to be added
        """

        self.ignored_rewards.append(reward)

    def remove_from_ignored_rewards(self, reward):
        """
        Tries to remove a reward from the list of ignored rewards
        :param reward: The target reward to be removed
        :return: True if successful, False otherwise
        """

        if reward not in self.ignored_rewards:
            return False
        self.ignored_rewards.remove(reward)
        return True
