import uuid
import json
import hashlib
import random
from datetime import datetime
import requests
import settings

subscribers_file = settings.SUBSCRIBERS

class User(object):

    def __init__(self, uuid=None):
        with open(subscribers_file, 'r') as f:
            try:
                self.users = json.load(f)
            except:
                self.users = []
        if uuid:
            return True

    def reload(self):
        self.__init__()

    def add(self, email):
        self.reload()
        if self.exists(email=email):
            return False

        salt = self.salt()

        new_user = {
            'uuid': str(uuid.uuid4()),
            'email': email,
            'token': hashlib.sha224((salt + email).encode('UTF-8')).hexdigest(),
            'verified': False,
            'registered': datetime.now().isoformat(),
            'preferences': ["1","2","3","4","5","6"],
            # This should be auto filled with IDs from Restaurants() class.
            'salt': salt,
        }

        self.users.append(new_user)
        self.save()
        self.email_verification(new_user['uuid'])
        return new_user

    def get(self, uuid=None, email=None, token=None):
        if not uuid and not email and not token:
            return False
        for user in self.users:
            if user['uuid'] == uuid or user['email'] == email or user['token'] == token:
                return user

    def get_preferences(self, email):
        return self.get(email=email)['preferences']

    def save(self):
        with open(subscribers_file, 'w') as f:
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
        return requests.post(
            settings.MAILGUN_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data={"from": settings.MAILGUN_FROM,
                "to": user['email'],
                "subject": "Verify your email",
                "template": "email_verification",
                "h:X-Mailgun-Variables": json.dumps(user),
                 })

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
        with open(subscribers_file, 'w') as f:
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
        self.restaurants = [
            {"id": 1, 'name': 'Pastva'},
            {'id': 2, 'name': 'Sodexo, Riverview'},
            {'id': 3, 'name': 'Dave B, Five'},
            {'id': 4, 'name': 'Potrefena Husa - Na Verandach'},
            {'id': 5, 'name': 'Lavande Restaurant'},
            {'id': 6, 'name': 'Prostor'},
            {'id': 7, 'name': 'Gourmet Pauza'},
            ]

    def restaurants(self):
        return self.restaurants
