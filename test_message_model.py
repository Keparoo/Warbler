"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py
#    python -m unittest -v test_message_model.py   # For results of both success and fail tests


import os
from unittest import TestCase
from sqlalchemy import exc
from datetime import datetime

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
        self.uid = 1
        u.id = self.uid

        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=========================================================================================================
    # Basic Model Tests    
    #=========================================================================================================

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="test message",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # Test __repr__
        self.assertEqual(Message.__repr__(m), f"<Message #{m.id}: {m.timestamp}, {m.user_id}>")

        # Test all fields
        self.assertEqual(m.text, "test message")
        self.assertEqual(m.user_id, self.uid)
        self.assertIsInstance(m.timestamp, datetime)

        # u should have 1 message
        self.assertEqual(len(self.u.messages), 1)

        # test message.user relationship
        self.assertEqual(m.user, self.u)

