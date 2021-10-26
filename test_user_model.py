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

DEFAULT_IMAGE_URL ="/static/images/default-pic.png"
DEFAULT_HEADER_IMAGE_URL ="/static/images/warbler-hero.jpg"
PASWORD1_HASHED = "$2b$12$YE0exSz7LXOXVFvswfhqzebpxKWqcwEi3.44FqFfeul3TyE3b6l4."

U1 = User(
        email="test1@test.com",
        username="testuser1",
        password="HASHED_PASSWORD1",
        bio="testbio1",
        location="testlocation1"
        )

U2 = User(
        email="test2@test.com",
        username="testuser2",
        password="HASHED_PASSWORD2",
        bio="testbio2",
        location="testlocation2"
        )

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("testuser1", "test1@test.com", "password1", None)
        u1.bio = "testbio1"
        u1.location = "testlocation1"
        uid1 = 1
        u1.id = uid1

        u2 = User.signup("testuser2", "test2@test.com", "password2", None)
        u2.bio = "testbio2"
        u2.location = "testlocation2"
        uid2 = 2
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 0)
        self.assertEqual(len(self.u1.likes), 0)
        # Test __repr__
        self.assertEqual(User.__repr__(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")
        self.assertEqual(self.u1.email, "test1@test.com")
        self.assertEqual(self.u1.username, "testuser1")
        self.assertEqual(self.u1.bio, "testbio1")
        self.assertEqual(self.u1.location, "testlocation1")
        self.assertEqual(self.u1.image_url, DEFAULT_IMAGE_URL)
        self.assertEqual(self.u1.header_image_url, DEFAULT_HEADER_IMAGE_URL)

        
    def test_follows(self):
        """Test for follows & following"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)


    def test_is_following(self):
        """Test successful is_following"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertFalse(self.u2.is_following(self.u1), True)

    def test_is_followed_by(self):
        """Test successful is_followed_by"""

        self.u1.following.append(self.u2)
        db.session.commit()    

        self.assertEqual(self.u2.is_followed_by(self.u1), True)   
        self.assertFalse(self.u1.is_followed_by(self.u2), True)   


