# controller.py

import uuid
import json
import hashlib
import random
from datetime import datetime
import requests
import os, sys
from jinja2 import Template

# Local imports
sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(0,'..')

path = os.path.dirname(os.path.abspath(__file__))

class User(object):

    def __init__(self, file=None):

        if file:
            self.subscribers_file = file
        else:
            self.subscribers_file = path + "/data/subscribers.json"

        with open(self.subscribers_file, 'r+') as f:
            try:
                self.users = json.load(f)
            except Exception as e:
                self.users = []
                self.save()

    def reload(self):
        self.__init__()

    def add(self, email, verify=False):
        if self.exists(email=email):
            return False

        salt = self.salt()

        new_user = {
            'uuid': str(uuid.uuid4()),
            'email': email,
            'token': hashlib.sha224((salt + email).encode('UTF-8')).hexdigest(),
            'verified': False,
            'registered': datetime.now().isoformat(),
            'preferences': Restaurants().preferences(),
            'salt': salt,
            'language': None,
        }

        self.users.append(new_user)
        self.save()

        if verify:
            self.verify( new_user['token'] )
        else:
            self.email_verification_html(new_user['uuid'])

        return new_user

    def get(self, uuid=None, email=None, token=None):
        if not uuid and not email and not token:
            return self.users
        for user in self.users:
            if user['uuid'] == uuid or user['email'] == email or user['token'] == token:
                return user
        return False

    def get_preferences(self, email):
        return self.get(email=email)['preferences']

    def save(self):
        with open(self.subscribers_file, 'w') as f:
            json.dump(self.users, f)
        self.reload()
        return True

    def update_preferences(self, token, new_preferences):
        uuid = self.get(token=token)['uuid']
        for i, user in enumerate(self.users):
            if user['uuid'] == uuid:
                self.users[i]['preferences'] = new_preferences
                self.save()
                return True
        return False

    def email_verification(self, uuid):

        user = self.get(uuid=uuid)

        if not user: # User not found
            return False

        return requests.post(
            SETTINGS.MAIL_URL,
            auth=("api", SETTINGS.MAIL_API_KEY),
            data={"from": SETTINGS.FROM,
                "to": user['email'],
                "subject": "Verify your email",
                "template": "email_verification",
                "h:X-Mailgun-Variables": json.dumps(user),
                 })

    def email_verification_html(self, uuid):

        recipient = self.get(uuid=uuid)

        if not recipient: # User not found
            return False

        data = {
            'title': "Please verify your email",
            'notice': {
                'title': "One last step..",
                'text': "Thank you for subscribing to the lunchScraper! Once \
                    you verify your email by clicking the button below, you \
                    will start to receive the daily menu for the restaurants \
                    in the area every day at 11AM.",
                'button': {
                    'url': SETTINGS.URL + "/verify?token=" + recipient['token'],
                    'text': "Verify", },
            },
            'recipient': {
                'email': recipient['email'],
                'url': SETTINGS.URL + "/?token=" + recipient['token'],
            },
        }

        html = Email().render_template("verification", data)

        data = {
            "from": SETTINGS.FROM,
            "to": recipient['email'],
            "subject": data['title'],
            "html": html,
        }

        return Email().send_html(data)

    def update(self, uuid, option, value):
        for i, user in enumerate(self.users):
            if user['uuid'] == uuid:
                self.users[i][option] = value
                self.save()
                self.reload()
                return True
        return False

    def verify(self, token):
        for user in self.users:
            if token == user['token']:
                self.update(
                    user['uuid'], 'verified', datetime.now().isoformat()
                )
                return True
        return False

    def remove(self, uuid=None, token=None, email=None):
        for i, user in enumerate(self.users):
            if user['uuid'] == uuid or user['email'] == email or user['token'] == token:
                self.users.pop(i)
                self.save()
                return True
        return False

    def exists(self, email=None, uuid=None):
        """Check whether the given user exists."""
        self.reload()
        for user in self.users:
            if user['email'] == email or user['uuid'] == uuid:
                return True
        return False

    def clear(self):
        """Deletes all subscribers from the database."""
        with open(self.subscribers_file, 'w') as f:
            f.write("")
        self.reload()

    def salt(self=None, length=16):
        """Creates random salt of len 16 for user. Not yet implemented."""
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []
        for char in range(length):
            chars.append(random.choice(ALPHABET))
        return "".join(chars)

    def add_restaurant_to_preferences(self, restaurant_id):
        self.reload()
        for recipient in self.users:
            recipient['preferences'].append(str(restaurant_id))
        self.save()
        return True

class Restaurants(object):

    def __init__(self):
        with open(path + "/data/restaurants.json", "r") as f:
            self.restaurants =  json.load(f)

    def restaurants(self):
        return self.restaurants

    def get(self, id=None):
        if isinstance(id, int):
            for restaurant in self.restaurants:
                if restaurant['id'] == id:
                    return restaurant
            return self.restaurants
        return self.restaurants

    def preferences(self):
        # Returns all preferences as a list
        return [ str(x['id']) for x in self.restaurants ]

class Email(object):

    def __init__(self):
        templates = os.listdir("templates/")
        self.templates = [x.split(".")[0] for x in templates if x.split(".")[1] == "html"]
        pass

    def render_template(self, template, data):

        try:
            template = template.split(".")[0]
        except:
            pass

        if template not in self.templates:
            return False

        with open("templates/{}.html".format(template), 'r') as html:
            html = html.read()
            template = Template(html)
            html = template.render(data=data)

        return html

    def send_html(self, data):

        auth = ("api", SETTINGS.MAIL_API_KEY)
        r = requests.post(SETTINGS.MAIL_URL, auth=auth, data=data)

        return r

    def get_notice(date=None):

        from datetime import datetime

        if date == None:
            date = datetime.strftime(datetime.today(), "%Y-%m-%d")

        try:
            with open(path + "/data/notices.json", 'r+') as f:
                notices = json.load(f)
                for notice in notices:
                    if notice['date'] == date:
                        return notice
        except Exception as e:
            return False, e

    def get_notices():

        try:
            with open(path + "/data/notices.json", 'r+') as f:
                return json.load(f)
        except Exception as e:
            return False, e

    def add_notice(notice=None):

        # If no notice provided, request from user (CLI only)
        if not notice:
            notice = {}
            notice['date'] = input("Provide a date to show notice (yyyy-mm-dd):\n")
            notice['title'] = input("Title of notice:\n")
            notice['text'] = input("Text of notice:\n")

        if not isinstance(notice, dict):
            raise Exception("Incorrect notice format, must be dict.")

        # try:
        with open(path + "/data/notices.json", "w") as f:
            try:
                notices = json.loads(f.read())
            except Exception as e:
                print("Failed to load notices to JSON, creating blank file", e)
                notices = []

            if notice['date'] in [x['date'] for x in notices]:
                raise Exception("Notice for given date already exists")

            notices = notices.append(notice)
            print(notices)
            json.dump(notices, f)
