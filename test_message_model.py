"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py
#    python -m unittest -v test_message_model.py   # For results of both success and fail tests


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u = User.signup("testuser1", "test1@test.com", "password1", None)
        self.uid1 = 1
        u.id = self.uid1

        db.session.commit()

        self.u = User.query.get(self.uid1)

        self.client = app.test_client()

    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()