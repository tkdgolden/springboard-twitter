"""Message model tests."""

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

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

    def test_message_model(self):
        """ Does basic model work? """

        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        u = User.query.filter(User.username=="testuser").one()
        m = Message(
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

    
    def test_message_user(self):
        """ Tests relationship between message and user """

        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        u = User.query.filter(User.username=="testuser").one()
        m = Message(
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.user, u)

    
    def test_user_messages(self):
        """ tests relationship between user and message """

        User.signup("testuser", "test@test.com", "123456", "/static/images/default-pic.png")
        u = User.query.filter(User.username=="testuser").one()
        m = Message(
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertIn(m, u.messages)