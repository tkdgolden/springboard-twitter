"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, Message, User

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


class LoginViewTestCase(TestCase):
    """Test login views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        self.client = app.test_client()
        db.session.commit()


    def test_logged_out_index(self):
        """ Display homepage while logged out """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]

        resp = c.get("/")
        html = resp.get_data(as_text=True)
        self.assertNotIn('<p class="small">Messages</p>', html)
        self.assertIn("<h1>What's Happening?</h1>", html)


    def test_sign_up_follow(self):
        """ Sign up follow """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]
        self.assertEqual([], User.query.filter(User.username=="testuser").all())
        resp = c.post("/signup", data={"username": "testuser", "email": "test@test.com", "password": "123456"}, follow_redirects=True)
        u = User.query.filter(User.username=="testuser").one()
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('<p class="small">Messages</p>', html)


    def test_login(self):
        """ Log in form submission """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]
        c.post("/signup", data={"username": "testuser", "email": "test@test.com", "password": "123456"})
        resp = c.post("/login", data={"username": "testuser", "password": "123456"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "http://localhost/")


    def test_login_follow(self):
        """ Log in follow """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]
        c.post("/signup", data={"username": "testuser", "email": "test@test.com", "password": "123456"})
        resp = c.post("/login", data={"username": "testuser", "password": "123456"}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('<p class="small">Messages</p>', html)


    def test_logout(self):
        """ Log out form submission """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]
        c.post("/signup", data={"username": "testuser", "email": "test@test.com", "password": "123456"})
        resp = c.get("/logout")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "http://localhost/")


    def test_logout_follow(self):
        """ Log out follow """

        with self.client as c:
            with c.session_transaction() as sess:
                if CURR_USER_KEY in sess:
                    del sess[CURR_USER_KEY]
        c.post("/signup", data={"username": "testuser", "email": "test@test.com", "password": "123456"})
        resp = c.get("/logout", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertNotIn('<p class="small">Messages</p>', html)