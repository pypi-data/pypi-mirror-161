import slack

class SlackClient():
    def __init__(self, token):
        self.SC = slack.WebClient(token=token)
        self.USERS = None

    @staticmethod
    def process_response(resp):
        assert resp['ok']
        return resp

    def get_users(self, force_reload=False):
        if not self.USERS or force_reload:
            resp = self.process_response(self.SC.users_list())
            self.USERS = {r['id']: r for r in resp['members']}
        return self.USERS

    def chat(self, channel, *args, **kwargs):
        return self.process_response(self.SC.chat_postMessage(channel=channel, *args, **kwargs))
