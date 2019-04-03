# Author : Joinemm
# File   : database.py

import json
import os
import random


""" DATABASE STRUCTURE ### data.json
{
    "settings": {
        "frequency": [
            xx,
            xxx
        ],
        "channel": <channel>
    },
    "users": {
        "<user_id>": {
            "<inventory_item>": x
        },
        .
        .
        .
        
    },
    "quotes": [
        {
            "question": "<question>",
            "answer": "<correct_answer>",
            "frequency": X
        },
        .
        .
        .
        
    ]
}
"""


class Database:

    def __init__(self):
        with open("data.json", "r") as f:
            self.data = json.load(f)

            # add categories if new data file
            if 'settings' not in self.data:
                self.data['settings'] = {}
            if 'users' not in self.data:
                self.data['users'] = {}
            if 'quotes' not in self.data:
                self.data['quotes'] = []

    def save_data(self):
        """Save data to file"""
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def change_setting(self, setting, value):
        """Change a setting"""
        self.data['settings'][setting] = value
        self.save_data()

    def add_quote(self, question, answer, freq):
        """Add quote entry"""
        entry = {"question": question,
                 "answer": answer,
                 "frequency": freq}
        self.data['quotes'].append(entry)
        self.save_data()

    def get_quotes_and_weights(self):
        entries = self.data.get('quotes')
        return entries, [x.get('frequency') for x in entries]

    def get_random_image(self):
        return 'img/' + random.choice(os.listdir('img/'))

    def get_setting(self, setting, default=None):
        """Get a setting"""
        return self.data['settings'].get(setting, default)

    def get_inventory(self, user):
        if str(user.id) in self.data['users']:
            return self.data['users'][str(user.id)]
        else:
            return {}

    def add_inventory_item(self, user, item, amount=1):
        """Add inventory item to given user"""

        # create user entry if it doesn't exist
        if str(user.id) not in self.data['users']:
            self.data['users'][str(user.id)] = {}

        # add [amount] to the quantity of item, or create it with value of [amount]
        if item in self.data['users'][str(user.id)]:
            self.data['users'][str(user.id)][item] += amount
        else:
            self.data['users'][str(user.id)][item] = amount

        # save modified data to file
        self.save_data()
        print(f"Added {amount} [{item}] to user [{user.name}#{user.discriminator}]")

    def remove_inventory_item(self, user, item, amount=1):
        """Remove inventory item from given user
        :returns False if removal failed, True on success"""

        # if user doesn't exist, just return
        if str(user.id) not in self.data['users']:
            return False

        # if item doesn't exist, just return
        if item not in self.data['users'][str(user.id)]:
            return False

        # remove [amount] from item quantity
        self.data['users'][str(user.id)][item] -= amount

        # if 0 or less, cleanup and delete entry
        if self.data['users'][str(user.id)][item] <= 0:
            del self.data['users'][str(user.id)][item]

        # save modified data to file
        self.save_data()
        print(f"Removed {amount} [{item}] from user [{user.name}#{user.discriminator}]")
        return True
