"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid1 = 1111
        self.uid2 = 2222

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u1.id = self.uid1
        u2 = User.signup("test2", "email2@email.com", "password", None)
        u2.id = self.uid2
        db.session.commit()

        self.u1 = User.query.get(self.uid1)
        self.u2 = User.query.get(self.uid2)
   
        self.client = app.test_client()
    
    def tearDown(self):
        db.session.rollback()

    
    def test_new_message(self):
        """Are new messages being created?"""

        newm = Message(text="Sample text for this message.")
        self.u1.messages.append(newm)
        db.session.commit()
        newm = Message(text="Second sample text for second message.")
        self.u1.messages.append(newm)
        db.session.commit()
        newm = Message(text="Third sample text for third message.")
        self.u1.messages.append(newm)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 3)
        self.assertEqual(len(self.u2.messages), 0)

    def test_likes(self):
        """Are likes being recorded?"""

        newm = Message(text="Sample text for this message.")
        self.u1.messages.append(newm)
        db.session.commit()
        newm = Message(text="Second sample text for second message.")
        self.u1.messages.append(newm)
        db.session.commit()
        newm = Message(text="Third sample text for third message.")
        self.u1.messages.append(newm)
        db.session.commit()

        lm1 = Message.query.get(1)
        lm2 = Message.query.get(2)

        self.u2.likes.append(lm1)
        self.u2.likes.append(lm2)

        self.assertEqual(len(self.u1.likes), 0)
        self.assertEqual(len(self.u2.likes), 2)
