"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py
#    FLASK_ENV=production python -m unittest -v test_user_views.py # For more verbose output


import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.uid = 666
        self.testuser.id = self.uid

        self.u1 = User.signup("user1", "test1@test.com", "password1", None)
        self.u1_id = 667
        self.u1.id = self.u1_id
        self.u2 = User.signup("user2", "test2@test.com", "password2", None)
        self.u2_id = 668
        self.u2.id = self.u1_id
        self.u3 = User.signup("user3", "test3@test.com", "password3", None)
        self.u3_id = 669
        self.u3.id = self.u1_id
        self.u4 = User.signup("user4", "test4@test.com", "password4", None)
        self.u4_id = 670
        self.u4.id = self.u1_id

        db.session.commit()

    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()