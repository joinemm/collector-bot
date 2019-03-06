import json


class Database:

    def __init__(self):
        with open("data.json", "r") as f:
            self.data = json.load(f)

            # add categories if new data file
            if 'settings' not in self.data:
                self.data['settings'] = {}
            if 'users' not in self.data:
                self.data['users'] = {}
            if 'questions' not in self.data:
                self.data['questions'] = {}
            if 'images' not in self.data:
                self.data['images'] = {}

    def save_data(self):
        """Save data to file"""
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def change_setting(self, setting, value):
        """Change a setting"""
        self.data['settings'][setting] = value
        self.save_data()

    def add_question(self, question, answer, response):
        """Add a question entry"""
        self.data['questions'][question] = {"answer": answer, "response": response}
        self.save_data()

    def add_image(self, f1, answer, f2):
        """Add image entry"""
        entry = {"filename_question": "img/" + f1,
                 "answer": answer,
                 "filename_response": "img/" + f2}
        self.data['images'][f1] = entry
        self.save_data()

    def get_questions_list(self):
        """Get list of questions to use in random choose"""
        return list(self.data['questions'].keys())

    def get_images_list(self):
        return list(self.data['images'].keys())

    def get_question(self, question):
        """Get the data for a question"""
        return self.data['questions'].get(question)

    def get_answer(self, question):
        return self.data['images'][question].get('answer')

    def get_response(self, question):
        return self.data['images'][question].get('filename_response')

    def get_filename(self, question):
        return self.data['images'][question].get('filename_question')

    def get_setting(self, setting, default=None):
        """Get a setting"""
        return self.data['settings'].get(setting, default)

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
