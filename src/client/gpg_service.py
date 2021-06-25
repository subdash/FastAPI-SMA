from getpass import getpass
from typing import Set, Optional

import gnupg
import os


class GPGService:
    """
    GNU Privacy Guard service to encrypt and decrypt messages and files. This
    service is designed to be used in a web app or API to increase security of
    messaging.

    Usage note: All methods return a gnupg.Crypt object. When called, you can
    verify that encryption or decryption was successful by checking that this
    object's `ok` field has the value `True`.
    """
    # TODO: Add method to add keys
    # TODO: Add method to export keys
    # This service must only be used client side, since the server should not
    # know the user's passphrase. The client encrypts the messages and the
    # server simply sends the encrypted messages back and forth.

    def __init__(self, gnpug_home: str, passphrase: Optional[str] = None):
        """
        :param gnpug_home: the path to the user's gnupg home, something along
        the lines of '/Users/username/.gnupg'
        :param passphrase: the passphrase that is set when generating a
        key-pair with GNUPG
        """
        assert os.path.isdir(gnpug_home), "Invalid path to gnupg home."
        self.gpg = gnupg.GPG(gnupghome=gnpug_home)

        if not passphrase:
            passphrase = self.create_key()

        assert self.gpg.is_valid_passphrase(passphrase=passphrase), \
            "Invalid passphrase."

        self.passphrase = passphrase
        print("GPGService initialization successful!")

    @staticmethod
    def passphrase_is_valid(passphrase: str) -> bool:
        # https://specopssoft.com/blog/nist-password-standards/
        if len(passphrase) < 8:
            print("Password must be at least 8 characters.")
            return False

        elif len(passphrase) > 64:
            print("Password must not be greater than 64 characters.")
            return False

        return True

    def encrypt_file(self, file: str, recipients: list) -> gnupg.Crypt:
        """
        Encrypt a file. If successful, the encrypted file will have the same
        name as the original file with ".gpg" appended to it.

        :param file: The file to encrypt
        :param recipients: Recipients who can decrypt the file
        :return: Crypt object
        """
        assert os.path.isfile(file), "Invalid file path."
        assert recipients, "Empty recipients list."

        with open(file, "rb") as f:
            status = self.gpg.encrypt_file(f, recipients=recipients,
                                           output=f"{file}.gpg")

        return status

    def decrypt_file(self, file: str) -> gnupg.Crypt:
        """
        Decrypt a file. If successful, the decrypted file will have the same
        name as the original with ".decrypted" appended to it.

        :param file: The file to decrypt
        :return: Crypt object
        """
        assert os.path.isfile(file), "Invalid file path."

        with open(file, "rb") as f:
            status = self.gpg.decrypt_file(f, passphrase=self.passphrase,
                                           output=f"{file[:-4]}.decrypted")

        return status

    def encrypt_message(self, message: str, recipients: list) -> str:
        """
        Encrypt a message. The returned object when converted to a string is a
        PGP message, assuming encryption was successful.

        :param message: The message to encrypt
        :param recipients: Recipients who can decrypt the message
        :return: Crypt object
        """
        assert message, "Message is required."
        assert recipients, "Empty recipients list."

        as_bytes = bytes(message, "utf-8")
        status = self.gpg.encrypt(as_bytes, recipients=recipients)

        return str(status)

    def decrypt_message(self, message: str) -> str:
        """
        Decrypt a message. The returned object when converted to a string is
        the decrypted message, assuming decryption was successful.

        :param message: The message to decrypt
        :return: Crypt object
        """
        assert message, "Message is required."

        as_bytes = bytes(message, "utf-8")
        status = self.gpg.decrypt(as_bytes, passphrase=self.passphrase)

        return str(status)

    def list_keys(self) -> Set[str]:
        """
        Get a set of all unique key-pairs added to keyring.

        :return: The set of keys added to the keyring
        """
        key_map = self.gpg.list_keys().key_map
        all_users = [v['uids'] for v in key_map.values()]
        unique_users = set([user[0] for user in all_users])

        return unique_users

    def create_key(self, passphrase="", email="") -> str:
        """
        Create a new keypair using a passphrase and email address.

        :param passphrase: Passphrase for decryption
        :param email: Email associated with keypair
        :return: The passphrase
        """
        while not passphrase:
            passphrase = getpass("Enter your key passphrase: ")

            if not self.passphrase_is_valid(passphrase):
                passphrase = ""

        while not email:
            # Validating an email address is complicated, and since this we
            # don't care about the email being valid anyways, any non-empty
            # string will work.
            email = input("Enter your key email: ")

        input_data = self.gpg.gen_key_input(key_type="RSA", key_length=4096,
                                            name_email=email, passphrase=passphrase)
        self.gpg.gen_key(input_data)

        return passphrase
