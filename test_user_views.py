"""user View tests."""

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


class UserViewTestCase(TestCase):
    """Test user views."""

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


    def tearDown(self):
        db.session.rollback()


    def test_access_user(self):
        """Can we look up users?"""

        with self.client as c:

            resp = c.get("/users")
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>@testuser</p>', html)
            self.assertIn('<p>@testuser2</p>', html)
                                       


    def test_add_user(self):
        """Can we add a user?"""

        with self.client as c:

            #get user form?
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Join Warbler today.</h2>', html)

            #Add a user
            resp = c.post("/signup", data={'username':'testuser3', 'password':'testpass', 'email':'test3@test.com', 'image_url':"" })

            self.assertEqual(resp.status_code, 302)
    


    def test_user_login(self):
        """Can user login?"""

        with self.client as c:

            #get login form?
            resp = c.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

            #login?
            resp = c.post("/login", data={'username':'testuser', 'password':'testuser'})
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 302)


    def test_user_logout(self):
        """Can user logout?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/logout")
            self.assertEqual(resp.status_code, 302)
            # self.assertIsNone(session[CURR_USER_KEY])

  
    def test_remove_user(self):
        """Can we remove a user?"""

        with self.client as c:
            with c.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/delete")
            self.assertEqual(resp.status_code, 302)
            
            html = resp.get_data(as_text=True)
            self.assertIn('You should be redirected automatically to the target URL: <a href="/signup">/signup</a>', html)

