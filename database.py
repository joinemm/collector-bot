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
            "answer": "<correct_answer>"
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

    def add_question(self, question, answer):
        entry = {"question": question,
                 "answer": answer}
        self.data['quotes'].append(entry)
        self.save_data()

    def get_questions(self):
        entries = self.data.get('quotes')
        return entries

    def get_random_image(self):
        directories = []
        for f in os.listdir("img/"):
            directories.append(f)

        directory = random.choices(directories, [int(x) for x in directories])[0]
        filename = random.choice(os.listdir('img/' + directory + '/'))
        return f'img/{directory}/{filename}'

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
