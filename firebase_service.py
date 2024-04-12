import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class FirebaseService:
    def __init__(self):
        cred_object = credentials.Certificate('./serviceAccountKey.json')
        firebase_admin.initialize_app(cred_object, {
            'databaseURL': 'https://botfiguras-default-rtdb.europe-west1.firebasedatabase.app/'
        })
        self.ref = db.reference('/')
        self.bot_data_ref = self.ref.child("last_message")
        self.sent_links_ref = self.ref.child("sent_links")
        self.create_nodes_if_not_exist()

    def create_nodes_if_not_exist(self):
        if not self.bot_data_ref.get():
            self.bot_data_ref.set({})
        if not self.sent_links_ref.get():
            self.sent_links_ref.set({})

    def save_last_message(self, message):
        self.bot_data_ref.update({"last_message": message})

    def save_last_link(self, link):
        self.bot_data_ref.update({"last_link": link})

    def load_last_message(self):
        return self.bot_data_ref.child("last_message").get() or ""

    def load_last_link(self):
        return self.bot_data_ref.child("last_link").get() or ""

    def save_sent_link(self, link):
        self.sent_links_ref.push().set(link)