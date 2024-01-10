"""User View tests."""

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
connect_db(app)
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    def test_users(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("<p>@testuser</p>", html)


    def test_user_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f'<h4 id="sidebar-username">@{self.testuser.username}</h4>', html)


    def test_user_add_follow(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
            u2 = User.query.filter(User.username=="testuser2").one()
            name = u2.username
            resp = c.post(f"/users/follow/{u2.id}")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"http://localhost/users/{self.testuser.id}/following")


    def test_user_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
            u2 = User.query.filter(User.username=="testuser2").one()
            name = u2.username
            resp = c.post(f"/users/follow/{u2.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f'<p>@{ name }</p>', html)


    def test_user_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
            u2 = User.query.filter(User.username=="testuser2").one()
            u2.following.append(self.testuser)
            name = u2.username
            db.session.commit()
            resp = c.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f'<p>@{ name }</p>', html)


    def test_user_unfollow(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
            u2 = User.query.filter(User.username=="testuser2").one()
            c.post(f"/users/follow/{u2.id}")
            resp = c.post(f"/users/stop-following/{u2.id}")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f"http://localhost/users/{self.testuser.id}/following")


    def test_user_no_longer_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
            u2 = User.query.filter(User.username=="testuser2").one()
            name = u2.username
            id = u2.id
            c.post(f"/users/follow/{ id }", follow_redirects=True)
            resp = c.post(f"/users/stop-following/{ id }", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertNotIn(f'<p>@{ name }</p>', html)


    def test_user_delete(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post("/users/delete")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/signup")
            self.assertEqual([], User.query.all())

