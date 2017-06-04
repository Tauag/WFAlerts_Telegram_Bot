import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timedelta
from config import tokens

TWITTER_GET_STATUS_URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"
WFALERTS_USER_ID = "1966470036"


class WFTwitterConsumer:
    oauth_token = None
    offset_id = 0

    def __init__(self):
        self.oauth_token = self.get_authorization(tokens.ACCESS_TOKEN, tokens.ACCESS_TOKEN_SECRET)
        # Updates the offset to most current tweet
        self.get_statuses(0, WFALERTS_USER_ID, 2)[1]['id']

    def get_authorization(self, token_key, token_secret):
        """
        Given an OAUTH token key and token secret, it requests authorization w/ OAuth1 protocol
        :param token_key:
        :param token_secret:
        :return: Authorization object
        """
        authorization = OAuth1(tokens.CONSUMER_KEY, client_secret=tokens.CONSUMER_SECRET, resource_owner_key=token_key,
                               resource_owner_secret=token_secret)
        return authorization

    def get_statuses(self, since, userid=WFALERTS_USER_ID, count=0):
        """
        Returns json file with most recent tweets and updates the offset to the newest message recieved
        :param since: The last tweet id to start polling from
        :param userid: The userid of the account to poll from
        :param count: Maximum number of tweets desired, by default 0 means no maximum
        :return: JSON file of tweets
        """
        payload = {"user_id": userid, "trim_user": "true", "include_rts": "false", "exclude_replies": "true"}

        if count > 0:
            payload.update({"count": str(count)})

        if since > 0:
            payload.update({"since_id": str(since)})

        r = requests.get(url=TWITTER_GET_STATUS_URL, auth=self.oauth_token, params=payload)

        # Update the offset
        for entry in r.json():
            if int(entry["id"]) > self.offset_id:
                self.offset_id = int(entry["id"])

        return r.json()

    def consume_wfstatus(self, alert_json):
        """
        Breaks the json file into a list of strings and updates the offset to the last message recieved
        String format is: Credit Reward|Object Reward|Mission Type|Archwing|Map Name|Time Until Start|Time Until End|
        Time Leftover
        :return: List of alert strings
        """
        alert_list = []
        for entry in alert_json:

            alert_parts = str(entry['text']).split("|")
            reward_parts = alert_parts[5].split("-")

            if len(reward_parts) > 1:
                alert_string = reward_parts[0] + "|" + reward_parts[1]
            else:
                alert_string = alert_parts[5] + "|"

            alert_string += ("|" + alert_parts[1])
            alert_string += ("|" + alert_parts[2])
            alert_string += ("|" + alert_parts[0])
            alert_string += ("|" + alert_parts[3])
            alert_string += ("|" + alert_parts[4])

            # Figure out when the alert ends
            alert_time = datetime.strptime(str(entry['created_at']), '%a %b %d %H:%M:%S +' + entry['created_at'][21:26]
                                           + '%Y')
            alert_time -= timedelta(hours=4)
            alert_length = int(alert_parts[4][:-2]) + int(alert_parts[3].split(" ")[3][:-1])
            alert_time += timedelta(minutes=alert_length)
            # Figure out the difference between end time and now
            sec_diff = (alert_time - datetime.now()).seconds
            min_diff = sec_diff / 60

            alert_string += ("|" + str(min_diff))

            alert_list.append(alert_string)

        return alert_list

    def getallcurrentalerts(self):
        """
        Returns a list of all current alerts
        :return: List of all current alerts
        """
        alerts_json = self.get_statuses(0)
        current_alerts_json = []

        for entry in alerts_json:
            alert_time = datetime.strptime(str(entry['created_at']), '%a %b %d %H:%M:%S +' + entry['created_at'][21:26]
                                           + '%Y')
            alert_time -= timedelta(hours=4)
            alert_parts = str(entry['text']).split("|")
            alert_length = int(alert_parts[4][:-2]) + int(alert_parts[3].split(" ")[3][:-1])
            alert_time += timedelta(minutes=alert_length)

            if alert_time > datetime.now():
                current_alerts_json.append(entry)

        return self.consume_wfstatus(current_alerts_json)


if __name__ == "__main__":
    tcom = WFTwitterConsumer()
    print(tcom.getallcurrentalerts())
