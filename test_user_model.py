"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

        # Test all fields (except password)
        self.assertEqual(self.u1.email, "test1@test.com")
        self.assertEqual(self.u1.username, "testuser1")
        self.assertEqual(self.u1.bio, "testbio1")
        self.assertEqual(self.u1.location, "testlocation1")
        self.assertEqual(self.u1.image_url, DEFAULT_IMAGE_URL)
        self.assertEqual(self.u1.header_image_url, DEFAULT_HEADER_IMAGE_URL)

    #=========================================================================================================
    # Follows/Following Tests    
    #=========================================================================================================

    def test_follows(self):
        """Test for follows & following"""

        # u1 is following u2
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)


    def test_is_following(self):
        """Test successful and fail of is_following"""

        # u1 is following u2
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(self.u1.is_following(self.u2), True)
        self.assertFalse(self.u2.is_following(self.u1), True)

    def test_is_followed_by(self):
        """Test successful and fail of is_followed_by"""

        # u1 is following u2
        self.u1.following.append(self.u2)
        db.session.commit()    

        self.assertEqual(self.u2.is_followed_by(self.u1), True)   
        self.assertFalse(self.u1.is_followed_by(self.u2), True)
    
    #=========================================================================================================
    # Create User Tests    
    #=========================================================================================================

    def test_sign_up(self):
        """Test successful signup"""

        user = User.signup("usersignuptest", "signup@signup.com", "password", None)
        uid = 9999
        user.id = uid
        db.session.commit()

        user = User.query.get(uid)
        self.assertEqual(user.username, "usersignuptest")
        self.assertEqual(user.email, "signup@signup.com")
        self.assertEqual(user.bio, None)
        self.assertEqual(user.location, None)
        self.assertEqual(user.image_url, DEFAULT_IMAGE_URL)
        self.assertEqual(user.header_image_url, DEFAULT_HEADER_IMAGE_URL)
        # Bcrypt strings should start with $2b$
        self.assertTrue(user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Test invalid empty username signup"""

        empty_username_user = User.signup(None, "signup@signup.com", "password", None)
        uid = 9999
        empty_username_user.id = uid

        # sqlalchemy will raise error as nullable=False
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_email_signup(self):
        """Test invalid empty email signup"""

        empty_email_user = User.signup("testuser", None, "password", None)
        uid = 9999
        empty_email_user.id = uid

        # sqlalchemy will raise error as nullable=False
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Test invalid missing or null-string password signup"""

        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "signup@signup.com", None, None)

        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "signup@signup.com", "", None)

    #=========================================================================================================
    # Authentication Tests    
    #=========================================================================================================

    def test_valid_authenticate(self):
        """Test valid authentication of user"""

        user = User.authenticate(self.u1.username, "password1")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.uid1)

    def test_invalid_username(self):
        """Test invalid username"""

        self.assertFalse(User.authenticate("wrongusername", "password1"))

    def test_invalid_password(self):
        """Test invalid password"""

        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))