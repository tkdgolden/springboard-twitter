"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
import sqlalchemy
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
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """ Tears down session from bad failed commits """

        db.session.rollback()
        db.session.remove()

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
        self.assertEqual(u.email, 'test@test.com')
        self.assertEqual(u.username, 'testuser')

    def test_user_signup(self):
        """ does signup correctly has pass and insert to db? """

        u = User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")

        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.email, 'test@test.com')
        self.assertEqual(u.username, 'testuser')
        self.assertNotEqual(u.password, '123456')

    def test_user_signup_fail_no_username(self):
        """ Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail? """

        with self.assertRaises(exc.IntegrityError) as context:
            User.signup(None, "test@test.com", "123456", "/static/images/default-pic.png")
            db.session.commit()

    
    def test_user_signup_fail_no_email(self):
        """ Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail? """

        with self.assertRaises(exc.IntegrityError) as context:
            User.signup("testuser", None, "123456", "/static/images/default-pic.png")
            db.session.commit()


    def test_user_signup_fail_username_taken(self):
        """ Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail? """
        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")

        with self.assertRaises(exc.IntegrityError) as context:
            User.signup("testuser", "test1@test.com", "123456", "/static/images/default-pic.png")
            db.session.commit()


    def test_user_signup_fail_email_taken(self):
        """ Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail? """
        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")

        with self.assertRaises(exc.IntegrityError) as context:
            User.signup("testuser1", "test@test.com", "123456", "/static/images/default-pic.png")
            db.session.commit()


    def test_user_repr(self):
        """ does representation method work as expected? """

        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        u = User.query.filter(User.username=="testuser").one()
        display = u.__repr__()

        self.assertEqual(display, f'<User #{u.id}: testuser, test@test.com>')

    def test_user_is_following(self):
        """ Does is_following successfully detect when user1 is following user2? """

        User.signup("testuser1", "test1@test.com", "123456", "/static/images/default-pic.png")
        User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
        u1 = User.query.filter(User.username=="testuser1").one()
        u2 = User.query.filter(User.username=="testuser2").one()
        u1.following.append(u2)

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    def test_user_is_followed_by(self):
        """ Does is_followed_by successfully detect when user1 is followed by user2? """

        User.signup("testuser1", "test1@test.com", "123456", "/static/images/default-pic.png")
        User.signup("testuser2", "test2@test.com", "123456", "/static/images/default-pic.png")
        u1 = User.query.filter(User.username=="testuser1").one()
        u2 = User.query.filter(User.username=="testuser2").one()
        u1.followers.append(u2)

        self.assertTrue(u1.is_followed_by(u2))
        self.assertFalse(u2.is_followed_by(u1))


    def test_user_authenticate(self):
        """ Does User.authenticate successfully return a user when given a valid username and password? """

        u = User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        self.assertEqual(User.authenticate("testuser", "123456"), u)

    
    def test_fail_user_authenticate(self):
        """ Does User.authenticate fail to return a user when the username is invalid? """

        u = User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        self.assertFalse(User.authenticate("test", "123456"))
        self.assertFalse(User.authenticate("testuser", "123457"))
