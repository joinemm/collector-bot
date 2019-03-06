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

    def add_image(self, f1, answer, f2):
        """Add image entry"""
        entry = {"filename_question": "img/" + f1,
                 "answer": answer,
                 "filename_response": "img/" + f2}
        self.data['images'][f1] = entry
        self.save_data()

    def remove_image(self, key):
        if key in self.data['images']:
            del self.data['images'][key]
            self.save_data()
            return True
        else:
            return False

    def get_images_list(self):
        return list(self.data['images'].keys())

    def get_answer(self, question):
        return self.data['images'][question].get('answer')

    def get_response(self, question):
        return self.data['images'][question].get('filename_response')

    def get_filename(self, question):
        return self.data['images'][question].get('filename_question')

    def get_setting(self, setting, default=None):
        """Get a setting"""
        return self.data['settings'].get(setting, default)

    
