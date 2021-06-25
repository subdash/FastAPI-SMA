## What is this?
I had the idea to create a messaging app with end-to-end encryption like WhatsApp or
Telegram. After finishing this project, I realized I had made some mistakes from
the beginning, though I did technically achieve my goal.

All the server does is expose REST endpoints for the client to call and stores user
accounts and messages in a database. The client does all the encryption and
decryption work. What mistakes did I make? First, in order for this to be used
in practice, each user would need to have GNUPG installed on their computer. This could
not be easily ported to a web or mobile app. Additionally, in order to properly test
this, the server would need to be deployed, or multiple instances of GNUPG would need
to be installed on one computer.

Anyways, mutatis mutandis, this project would be a solid secure messaging app. The way
it is set up, only the client holds on to their private key; if the server was somehow
compromised, the hacker would only have access to a bunch of encrypted messages and
hashed passwords (and email addresses, though those could easily be stored more
securely as well).

This is my first pass at adding this kind security to an app, so there are probably
myriad additional improvements that could be made to make it more secure. I plan to
make a second pass at this in the future with the discussed security and
portability improvements so that this could be used in the real world.

## Improvements
- Ability to add friends
- Ability to more easily associate a user account with a GPG key
- Discussion points above regarding making the client code more portable
- Usage of a more secure hashing algorithm

## About
[FastAPI](https://fastapi.tiangolo.com/) is the framework used to build the server
component of this project.
The project is set up to use [MariaDB](https://mariadb.org/). 
[SQLAlchemy](https://www.sqlalchemy.org/) was used as an ORM to keep the code that
interacts with the DB clean and correct.
