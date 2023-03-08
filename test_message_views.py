"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.commit()
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

        self.mid = 1111
        self.testmessage = Message(text="This is a test message", user_id=self.testuser2.id)
        self.testmessage.id = self.mid
        db.session.add(self.testmessage)
        db.session.commit()
        


        
    def tearDown(self):
        db.session.rollback()


    def test_add_message(self):
        """Can user add a message?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.all()
            self.assertEqual(msg[1].text, "Hello")

    def test_add_like(self):
        """Can user like a message?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/add_like/{self.mid}")

                        # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            self.assertIsNotNone(Likes.query.filter_by(message_id=self.mid).all())


    def test_remove_like(self):
        """Can user unlike a message?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/add_like/{self.mid}")

                        # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            self.assertIsNotNone(Likes.query.filter_by(message_id=self.mid).first())

    def test_delete_message(self):
        """Can user delete a message?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{self.mid}/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            self.assertIsNone(Message.query.get(self.mid))