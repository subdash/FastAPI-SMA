from getpass import getpass
import json
import requests

from src.client.format import fmt_conversation
from src.client.gpg_service import GPGService


class HTTPService:
    BASE_URL = "http://localhost:8000"

    def __init__(self):
        """
        Initialize GPG service by passing in the path to a local GNUPG
        database.
        """
        home = getpass("Enter GNUPG home: ")

        self.gpg_service = GPGService(gnpug_home=home)
        self.access_token = None

    @staticmethod
    def get_user_or_email_payload(prompt) -> (dict, str):
        """
        Ask the user to enter their username or email and return it in a format
        that can be used for REST calls.

        :param prompt: The prompt to display for input
        :return: A tuple containing 1) a dictionary with the username or email
        with the key specifying which one it is and 2) the username or email
        itself
        """
        email_or_username = input(prompt)

        if "@" in email_or_username:
            return {"email": email_or_username}, email_or_username

        return {"username": email_or_username}, email_or_username

    def decrypt_and_print_conversation(self, decoded):
        for msg in decoded:
            if "-----BEGIN PGP MESSAGE-----" not in msg['content']:
                continue

            msg['content'] = self.gpg_service.decrypt_message(msg['content'])

        print(fmt_conversation(decoded))

    def register(self) -> None:
        """
        Create an account by getting input for a username, email and password.
        A key-pair will be created using this information and stored in the
        user's local GNUPG database.
        """
        # Used for creating account. Submit to /create_account endpoint
        username = input("Enter your username. " +
                         "This will be used to log in to the web service.\n")
        email = input("Enter your email. " +
                      "This will be used as your GNUPG username.\n")
        password = getpass("Enter your password. " +
                           "This will be used as your GNUPG passphrase.\n")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(f"{self.BASE_URL}/register", json=payload,
                                 headers=headers)

        self.gpg_service.create_key(passphrase=password, email=email)

        if response.status_code == 200:
            print("Account created.\nAttempting to log in...")
            self.login(username, password)

        else:
            print("There was a problem creating your account.")

    def login(self, username=None, password=None) -> None:
        """
        Authenticate an account. If authentication is successful, an
        access-token will be stored so that protected endpoitns can be called.

        :param username: The username created when registering
        :param password: The password created when registering
        """
        if not username and not password:
            username = input("Enter your username: ")
            password = getpass("Enter your password: ")

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }

        response = requests.post(f"{self.BASE_URL}/login", data=payload,
                                 headers=headers)

        if response.status_code != 200:
            print("Failed to log in. Check your credentials.")
            return

        response_as_json = json.loads(response.content.decode())

        if {"access_token", "token_type"} == set(response_as_json.keys()):
            self.access_token = response_as_json
            print("Login successful.")

    def read_conversation(self) -> None:
        """
        Make a REST call to get all correspondences between the logged in user
        and another one. Decrypt each message, then display them in a
        user-friendly format.
        """
        if not self.access_token:
            print("You must be logged in to view conversations.")
            return

        payload, _ = self.get_user_or_email_payload(
            "Enter the user whose conversation you want to view:\n"
        )
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token['access_token']}",
            "Content-Type": "application/json",
        }
        id_response = requests.post(f"{self.BASE_URL}/lookup/",
                                    headers=headers,
                                    json=payload)

        if id_response.status_code != 200:
            print("That person could not be found.")
            return

        friend_id = json.loads(id_response.content.decode())['id']
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token['access_token']}"
        }
        msg_response = requests.get(f"{self.BASE_URL}/messages/{friend_id}",
                                    headers=headers)

        if msg_response.status_code != 200:
            print("Could not retrieve messages.")

        decoded = json.loads(msg_response.content.decode())
        self.decrypt_and_print_conversation(decoded)

    def send_message(self) -> None:
        """
        Get the name of the person to send a message to. Make a REST call to
        get that person's ID. Encrypt the message, then make another rest call
        to send it.
        """
        if not self.access_token:
            print("You must be logged in to send a message.")
            return

        payload, name = self.get_user_or_email_payload(
            "Enter the user who you want to send a message to:\n"
        )

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token['access_token']}",
            "Content-Type": "application/json",
        }
        id_response = requests.post(f"{self.BASE_URL}/lookup/",
                                    headers=headers,
                                    json=payload)

        if id_response.status_code != 200:
            print("That person could not be found.")
            return

        friend_id = json.loads(id_response.content.decode())['id']

        message = input("Enter your message:\n")
        encrypted = self.gpg_service.encrypt_message(message, [name])

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token['access_token']}",
            "Content-Type": "application/json",
        }
        payload = {
            "content": encrypted
        }
        msg_response = requests.post(f"{self.BASE_URL}/messages/{friend_id}",
                                     json=payload,
                                     headers=headers)

        if msg_response.status_code != 200:
            print("An error occurred.")

        decoded = json.loads(msg_response.content.decode())
        self.decrypt_and_print_conversation(decoded)

    def preview_messages(self) -> None:
        """
        Display preview of messages. Decrypt each one and show the head of the
        text.
        """
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token['access_token']}"
        }
        response = requests.get(f"{self.BASE_URL}/messages/", headers=headers)

        if response.status_code != 200:
            print("Could not retrieve messages.")

        decoded = json.loads(response.content.decode())
        for msg in decoded:
            msg['content'] = self.gpg_service.decrypt_message(msg['content'])

        print(fmt_conversation(decoded))

    def view_friends(self) -> None:
        """
        Print list of keys (name/email pairs) which have been added to the
        keyring.
        """
        local_key_pairs = self.gpg_service.list_keys()

        headers = {"accept": "application/json"}
        response = requests.get(f"{self.BASE_URL}/friends", headers=headers)

        server_pairs = json.loads(response.content.decode())
        mapped = set(map(lambda pair: f"{pair['username']} <{pair['email']}>", server_pairs))
        intersection = local_key_pairs & mapped

        print("You can send messages to the following users:")
        for user in intersection:
            print(user)

    def add_friend(self):
        # Add friend to keyring. This will require importing their public key.
        print("Not yet implemented.")

    def send_file(self):
        # Encrypt a file and call and endpoint to send it.
        print("Not yet implemented.")

    def download_file(self):
        # Decrypt the file and make it available to download. Server holds on
        # to the encrypted file.
        print("Not yet implemented.")
