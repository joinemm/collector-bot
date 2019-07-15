# Author : Joinemm
# File   : database.py

import json
import os
import random
import copy


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
            if 'whitelist' not in self.data:
                self.data['whitelist'] = []

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

    def remove_question(self, question):
        for i in range(len(self.get_questions())):
            if self.data['quotes'][i].get('question').lower() == question.lower():
                del self.data['quotes'][i]
                print("deleted", question)
                self.save_data()
                return True
            return False

    def get_questions(self):
        entries = self.data.get('quotes')
        return entries

    def get_random_image(self):
        directories = []
        for f in os.listdir("img/"):
            try:
                int(f)
                if os.listdir('img/' + f + '/'):
                    directories.append(f)
            except ValueError:
                continue

        directory = random.choices(directories, [int(x) for x in directories])[0]
        directory_items = os.listdir('img/' + directory + '/')
        filename = random.choice(directory_items)
        return f'img/{directory}/{filename}'

    def get_setting(self, setting, default=None):
        """Get a setting"""
        return self.data['settings'].get(setting, default)

    def get_inventory(self, user):
        if str(user.id) in self.data['users']:

            # check if image exists on disk
            inv = copy.copy(self.data['users'][str(user.id)])
            for item in inv:
                if not os.path.isfile(item):
                    self.remove_inventory_item(user, item, delete_all=True)
                    reference = check_reference(item)
                    if reference is not None:
                        self.add_inventory_item(user, reference, inv[item])

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

    def remove_inventory_item(self, user, item, delete_all=False):
        """Remove inventory item from given user
        :returns False if removal failed, True on success"""

        # if user doesn't exist, just return
        if str(user.id) not in self.data['users']:
            return False

        # if item doesn't exist, just return
        if item not in self.data['users'][str(user.id)]:
            return False

        if delete_all:
            del self.data['users'][str(user.id)][item]
        else:
            # remove [amount] from item quantity
            self.data['users'][str(user.id)][item] -= 1

            # if 0 or less, cleanup and delete entry
            if self.data['users'][str(user.id)][item] <= 0:
                del self.data['users'][str(user.id)][item]

        # save modified data to file
        self.save_data()
        print(f"Removed [{item}] from user [{user.name}#{user.discriminator}]")
        return True

    def get_whitelist(self, ctx):
        whitelist = self.data.get('whitelist', [])
        return [ctx.bot.appinfo.owner.id] + whitelist

    def whitelist(self, userid):
        self.data['whitelist'].append(int(userid))
        self.save_data()

    def unwhitelist(self, userid):
        self.data['whitelist'].remove(int(userid))
        self.save_data()

    def get_users(self):
        return self.data['users']


def check_reference(path_to_image):
    reference_path = f"img/reference/{path_to_image.split('/')[-1]}"
    if os.path.isfile(reference_path):
        return reference_path
    else:
        reference_path = f"img/Reference/{path_to_image.split('/')[-1]}"
        if os.path.isfile(reference_path):
            return reference_path
        else:
            return None



