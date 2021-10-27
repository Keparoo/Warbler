"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py
#    FLASK_ENV=production python -m unittest -v test_message_views.py # For more verbose output


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

        self.uid = 999
        self.testuser.id = self.uid

        db.session.commit()

    def tearDown(self):
        """Rollback problems from failed tests"""

        db.session.rollback()

    #=========================================================================================================
    # View Message Tests
    #=========================================================================================================

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of our tests

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        """Test fail to add message when no session var"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        """Test fail to add message when wrong user is logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 999999 # Non-existant user id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
        
    def test_message_show(self):
        """Test show message details"""

        m = Message(
            id=9999,
            text="This is a message",
            user_id=self.uid
        )
        
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            message = Message.query.get(9999)
            resp = c.get(f'/messages/{message.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(message.text, str(resp.data))
            print(str(resp.data))

    def test_show_message_invalid_id(self):
        """Test fail of message show with invalid message id"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/messages/99999')

            self.assertEqual(resp.status_code, 404)

    def test_delete_message(self):
        """Test successful delete message"""

        m = Message(
                id=9999,
                text="This is a message",
                user_id=self.uid
            )

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/9999/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            message = Message.query.get(9999)
            self.assertIsNone(message)

    def test_unauthorized_delete(self):
        """Test delete as wrong user"""

        message = Message(
            id=7777,
            text="a test message",
            user_id=self.uid
        )

        other_user = User.signup(username="other-user",
                                email="otheruser@otheruser.com",
                                password="otherpassword",
                                image_url=None
                                )
        other_user.id = 8888

        db.session.add_all([message, other_user])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 8888

            resp = c.post('/messages/7777/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))

            # Check message is still in database
            message = Message.query.get(7777)
            self.assertIsNotNone(message)

    def test_message_no_session(self):
        """Test fail of delete message if no user logged in"""

        message = Message(
            id=7777,
            text="a test message",
            user_id=self.uid
        )
        db.session.add(message)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/7777/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            message = Message.query.get(7777)
            self.assertIsNotNone(message)