class WFAlertBot:
    chat_id = 0
    ignored_rewards = None
    wants_updates = False

    def __init__(self, chatid):
        self.chat_id = chatid
        self.ignored_rewards = []

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
