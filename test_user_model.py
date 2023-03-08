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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

    

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.likes), 0)


    ## Following Tests
    def test_follows(self):
        """Test if appending to following works"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertIsNotNone(Follows.query.get_or_404((self.uid2, self.uid1)))

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?
        Does is_following successfully detect when user1 is not following user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))
        
    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user1 is not followed by user2?"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_user_signup(self):
        """Does User.create successfully create a new user given valid credentials?"""
        tu = User.signup("testdude", "test@test.com", "god", None)
        tu.id = 3333
        db.session.commit()

        tu = User.query.get(3333)
        self.assertIsNotNone(tu)
        self.assertEqual(tu.username, "testdude")
        self.assertEqual(tu.email, "test@test.com")

    